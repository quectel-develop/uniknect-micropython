from quectel import BLEClient
import utime


class BLEClientDemo(object):
    PROP_READ = 0x02
    PROP_WRITE_NO_RSP = 0x04
    PROP_WRITE = 0x08
    PROP_NOTIFY = 0x10
    PROP_INDICATE = 0x20

    CCCD_UUID = 0x2902

    def __init__(self, target_name):
        self.blec = BLEClient()
        self.target_name = target_name

        self.target_addr = None
        self.target_addr_type = None

        self.connected = False
        self.conn_id = -1
        self.mtu = 0

        self.services = []
        self.chars = []

        self.current_desc_char = None

    def str_to_hex(self, s):
        return ''.join('%02X' % b for b in s.encode())

    def hex_to_str(self, hexstr):
        if hexstr is None:
            return ""

        try:
            if len(hexstr) % 2 != 0:
                return hexstr

            data = bytearray()
            for i in range(0, len(hexstr), 2):
                data.append(int(hexstr[i:i + 2], 16))

            return data.decode()
        except Exception:
            return hexstr

    def clean_name(self, name):
        if name is None:
            return ""
        return name.replace("\x00", "").strip()

    def is_connected(self):
        return self.connected

    def callback(self, evt):
        event = evt.get("event")

        if event == self.blec.EVT_SCAN_RESULT:
            name = self.clean_name(evt.get("name"))

            if name == self.target_name and self.target_addr is None:
                self.target_addr = evt.get("addr")
                self.target_addr_type = evt.get("addr_type")

                print("找到目标设备:")
                print("  name      =", name)
                print("  addr      =", self.target_addr)
                print("  addr_type =", self.target_addr_type)
                print("  rssi      =", evt.get("rssi"))

        elif event == self.blec.EVT_CONNECTED:
            self.connected = True
            self.conn_id = evt.get("conn_id", self.blec.get_conn_id())

            print("连接成功")
            print("  conn_id =", self.conn_id)
            print("  addr    =", evt.get("addr"))

        elif event == self.blec.EVT_DISCONNECTED:
            print("连接断开")
            print("  addr   =", evt.get("addr"))
            print("  reason =", evt.get("reason"))
            print("  status =", evt.get("status"))

            self.connected = False
            self.conn_id = -1

        elif event == self.blec.EVT_MTU:
            self.mtu = evt.get("mtu")
            print("MTU:", self.mtu)

        elif event == self.blec.EVT_SERVICE:
            uuid = evt.get("uuid")
            start = evt.get("start_handle")
            end = evt.get("end_handle")

            print("发现服务:")
            print("  uuid  =", hex(uuid) if uuid is not None else uuid)
            print("  start =", start)
            print("  end   =", end)

            if uuid == 0x1800 or uuid == 0x1801:
                print("  skip standard service")
                return

            if uuid is not None and start is not None and end is not None:
                self.services.append({
                    "uuid": uuid,
                    "start": start,
                    "end": end
                })

        elif event == self.blec.EVT_CHARACTER:
            uuid = evt.get("uuid")
            decl_handle = evt.get("handle")
            value_handle = evt.get("value_handle")
            properties = evt.get("properties")

            print("发现特征:")
            print("  uuid         =", hex(uuid) if uuid is not None else uuid)
            print("  decl_handle  =", decl_handle)
            print("  value_handle =", value_handle)
            print("  properties   =", properties)

            if uuid is not None and decl_handle is not None and value_handle is not None:
                self.chars.append({
                    "uuid": uuid,
                    "decl_handle": decl_handle,
                    "value_handle": value_handle,
                    "prop": properties,
                    "service_end": 0,
                    "cccd": -1
                })

        elif event == self.blec.EVT_DESCRIPTOR:
            uuid = evt.get("uuid")
            handle = evt.get("handle")

            print("发现描述符:")
            print("  uuid   =", hex(uuid) if uuid is not None else uuid)
            print("  handle =", handle)

            if uuid == self.CCCD_UUID and self.current_desc_char is not None:
                self.current_desc_char["cccd"] = handle

                print("保存 CCCD:")
                print("  char uuid =", hex(self.current_desc_char["uuid"]))
                print("  cccd      =", handle)

        elif event == self.blec.EVT_READ_RESULT:
            value = evt.get("value")

            print("")
            print("读取结果:")
            print("  value  =", value)

        elif event == self.blec.EVT_WRITE_RESULT:
            if evt.get("ok"):
                print("")
                print("写入 OK")
            else:
                print("")
                print("写入 FAILED:", evt)

        elif event == self.blec.EVT_NOTIFY:
            value = evt.get("value")

            print("")
            print("收到 Notify:")
            print("  handle =", evt.get("handle"))
            print("  len    =", evt.get("len"))
            print("  value  =", value)
            print("  str    =", self.hex_to_str(value))

        elif event == self.blec.EVT_INDICATE:
            value = evt.get("value")

            print("")
            print("收到 Indicate:")
            print("  handle =", evt.get("handle"))
            print("  len    =", evt.get("len"))
            print("  value  =", value)
            print("  str    =", self.hex_to_str(value))

        elif event == self.blec.EVT_ATT_ERROR:
            print("ATT ERROR:", evt.get("att_err"))

        else:
            print("事件:", evt)

    def start(self):
        print("init ble client")

        if not self.blec.init(self.callback):
            print("ble client init failed")
            return False

        print("start ble client")
        self.blec.start()

        self.blec.set_scan_params(
            self.blec.SCAN_PASSIVE,
            0x640,
            0x30,
            self.blec.SCAN_FILTER_ALL,
            self.blec.ADDR_PUBLIC
        )
        self.blec.set_name_filter(self.target_name)
        return True

    def scan_target(self):
        print("开始扫描目标设备:", self.target_name)

        self.target_addr = None
        self.target_addr_type = None

        self.blec.scan(True)

        while self.target_addr is None:
            utime.sleep_ms(100)

        print("停止扫描")
        self.blec.scan(False)

        utime.sleep_ms(500)
        return True

    def connect_target(self, timeout_ms=10000):
        if self.target_addr is None:
            print("目标地址为空，不能连接")
            return False

        print("开始连接:")
        print("  addr_type =", self.target_addr_type)
        print("  addr      =", self.target_addr)

        self.connected = False

        try:
            self.blec.connect(self.target_addr_type, self.target_addr)
        except Exception as e:
            print("connect failed:", e)
            return False

        start = utime.ticks_ms()

        while not self.connected:
            if utime.ticks_diff(utime.ticks_ms(), start) > timeout_ms:
                print("连接超时")
                return False

            utime.sleep_ms(100)

        utime.sleep_ms(1000)
        return True

    def discover_services(self):
        print("开始发现服务")

        self.services = []

        try:
            self.blec.discover_services(self.conn_id)
        except Exception as e:
            print("discover services failed:", e)
            return False

        utime.sleep_ms(1500)

        print("服务发现完成，数量:", len(self.services))
        return True

    def discover_characteristics(self):
        print("开始发现特征")

        self.chars = []

        for s in self.services:
            print("发现服务内特征:")
            print("  service uuid =", hex(s["uuid"]))
            print("  start        =", s["start"])
            print("  end          =", s["end"])

            before_count = len(self.chars)

            try:
                self.blec.discover_characteristics(
                    self.conn_id,
                    s["start"],
                    s["end"]
                )
            except Exception as e:
                print("discover characteristics failed:", e)
                continue

            utime.sleep_ms(1000)

            for i in range(before_count, len(self.chars)):
                self.chars[i]["service_end"] = s["end"]

        print("特征发现完成，数量:", len(self.chars))
        return True

    def discover_descriptors(self):
        print("开始发现描述符")

        if len(self.chars) == 0:
            print("没有特征，不发现描述符")
            return True

        sorted_chars = sorted(self.chars, key=lambda x: x["decl_handle"])

        for i in range(len(sorted_chars)):
            c = sorted_chars[i]

            start = c["value_handle"] + 1

            if i + 1 < len(sorted_chars):
                next_decl = sorted_chars[i + 1]["decl_handle"]
                end = next_decl - 1
            else:
                end = c["service_end"]

            if start > end:
                continue

            self.current_desc_char = c

            print("发现特征描述符:")
            print("  char uuid =", hex(c["uuid"]))
            print("  start     =", start)
            print("  end       =", end)

            try:
                self.blec.discover_descriptors(
                    self.conn_id,
                    start,
                    end
                )
            except Exception as e:
                print("discover descriptors failed:", e)
                continue

            utime.sleep_ms(800)

        self.current_desc_char = None

        print("描述符发现完成")
        return True

    def discover_all(self):
        if not self.discover_services():
            return False

        if not self.discover_characteristics():
            return False

        self.discover_descriptors()
        self.print_char_list()

        return True

    def print_char_list(self):
        print("")
        print("========== 已发现特征 ==========")

        if len(self.chars) == 0:
            print("无")
            print("================================")
            return

        for c in self.chars:
            print("uuid =", hex(c["uuid"]),
                  "decl =", c["decl_handle"],
                  "value =", c["value_handle"],
                  "prop =", c["prop"],
                  "cccd =", c.get("cccd", -1))

        print("================================")

    def read_by_handle(self, handle):
        if not self.connected:
            print("当前未连接")
            return

        print("读取特征:")
        print("  value_handle =", handle)

        try:
            self.blec.read_char_by_handle(self.conn_id, handle)
        except Exception as e:
            print("read failed:", e)

    def write_by_handle(self, handle, data):
        if not self.connected:
            print("当前未连接")
            return

        data_hex = self.str_to_hex(data)
        data_len = len(data.encode())

        print("写入特征:")
        print("  value_handle =", handle)
        print("  str          =", data)
        print("  hex          =", data_hex)
        print("  len          =", data_len)

        try:
            self.blec.write_char(
                self.conn_id,
                handle,
                data_len,
                data_hex
            )
        except Exception as e:
            print("write failed:", e)

    def write_no_rsp_by_handle(self, handle, data):
        if not self.connected:
            print("当前未连接")
            return

        data_hex = self.str_to_hex(data)
        data_len = len(data.encode())

        print("无响应写入特征:")
        print("  value_handle =", handle)
        print("  str          =", data)
        print("  hex          =", data_hex)
        print("  len          =", data_len)

        try:
            self.blec.write_char_no_rsp(
                self.conn_id,
                handle,
                data_len,
                data_hex
            )
        except Exception as e:
            print("write no rsp failed:", e)

    def write_cccd(self, cccd_handle, value_hex):
        if not self.connected:
            print("当前未连接")
            return

        if cccd_handle is None or cccd_handle < 0:
            print("CCCD handle 无效")
            return

        print("写 CCCD:")
        print("  cccd_handle =", cccd_handle)
        print("  data        =", value_hex)

        try:
            self.blec.write_descriptor(
                self.conn_id,
                cccd_handle,
                2,
                value_hex
            )
        except Exception as e:
            print("write descriptor failed:", e)

    def open_notify(self, cccd_handle):
        self.write_cccd(cccd_handle, "0100")

    def open_indicate(self, cccd_handle):
        self.write_cccd(cccd_handle, "0200")

    def close_notify_indicate(self, cccd_handle):
        self.write_cccd(cccd_handle, "0000")

    def stop(self):
        print("clean up...")

        try:
            if self.connected:
                print("disconnect")
                self.blec.disconnect()
        except Exception as e:
            print("disconnect failed:", e)

        self.connected = False
        self.conn_id = -1

        try:
            print("stop ble client")
            self.blec.stop()
        except Exception as e:
            print("ble stop failed:", e)

        try:
            print("deinit ble client")
            self.blec.deinit()
        except Exception as e:
            print("ble deinit failed:", e)

        print("clean up done")


def parse_int(s):
    s = s.strip()

    if s.startswith("0x") or s.startswith("0X"):
        return int(s, 16)

    return int(s)


def input_value_handle():
    s = input("请输入 value_handle，例如 21 或 0x15: ").strip()

    try:
        return parse_int(s)
    except Exception:
        print("value_handle 输入无效")
        return None


def input_cccd_handle():
    s = input("请输入 CCCD handle，例如 22 或 0x16: ").strip()

    try:
        return parse_int(s)
    except Exception:
        print("CCCD handle 输入无效")
        return None


def cmd_read(app):
    if not app.is_connected():
        print("当前未连接")
        return

    handle = input_value_handle()

    if handle is None:
        return

    app.read_by_handle(handle)


def cmd_write(app):
    if not app.is_connected():
        print("当前未连接")
        return

    handle = input_value_handle()

    if handle is None:
        return

    data = input("请输入要写入的字符串: ")
    app.write_by_handle(handle, data)


def cmd_write_no_rsp(app):
    if not app.is_connected():
        print("当前未连接")
        return

    handle = input_value_handle()

    if handle is None:
        return

    data = input("请输入要写入的字符串: ")
    app.write_no_rsp_by_handle(handle, data)


def cmd_open_notify(app):
    if not app.is_connected():
        print("当前未连接")
        return

    cccd = input_cccd_handle()

    if cccd is None:
        return

    app.open_notify(cccd)


def cmd_open_indicate(app):
    if not app.is_connected():
        print("当前未连接")
        return

    cccd = input_cccd_handle()

    if cccd is None:
        return

    app.open_indicate(cccd)


def cmd_close_push(app):
    if not app.is_connected():
        print("当前未连接")
        return

    cccd = input_cccd_handle()

    if cccd is None:
        return

    app.close_notify_indicate(cccd)


def command_loop(app):
    print("")
    print("========== BLE Client 命令菜单 ==========")
    print("1: 读取特征")
    print("2: 写入特征")
    print("3: 无响应写入特征")
    print("4: 打开 Notify")
    print("5: 打开 Indicate")
    print("6: 关闭 Notify/Indicate")
    print("7: 打印已发现特征")
    print("q: 退出")
    print("========================================")

    while app.is_connected():
        cmd = input("请输入命令: ").strip()

        if cmd == "1":
            cmd_read(app)

        elif cmd == "2":
            cmd_write(app)

        elif cmd == "3":
            cmd_write_no_rsp(app)

        elif cmd == "4":
            cmd_open_notify(app)

        elif cmd == "5":
            cmd_open_indicate(app)

        elif cmd == "6":
            cmd_close_push(app)

        elif cmd == "7":
            app.print_char_list()

        elif cmd == "q" or cmd == "Q":
            print("退出命令菜单")
            break

        else:
            print("未知命令:", cmd)

        utime.sleep_ms(100)


def main():
    app = BLEClientDemo("Uniknect_BLE_DEMO")

    try:
        if not app.start():
            return

        if not app.scan_target():
            return

        if not app.connect_target():
            return

        app.discover_all()

        command_loop(app)

    except KeyboardInterrupt:
        print("Ctrl+C")

    except Exception as e:
        print("程序异常:", e)

    finally:
        app.stop()


main()