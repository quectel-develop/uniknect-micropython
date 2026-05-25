import Qth
import _thread
import utime
import gc
from quectel import Log

log = Log()
log.set_level(Log.NONE)


def App_devEventCb(event, result):
    print('dev event:{} result:{}'.format(event, result))
    if 2 == event and 0 == result:
        Qth.otaRequest()
        print("state:" + str(Qth.state()))


def App_cmdRecvTransCb(value):
    ret = Qth.sendTrans(1, value)
    print('recvTrans value:{} ret:{}'.format(value, ret))


def App_cmdRecvTslCb(value):
    print('recvTsl:{}'.format(value))
    for cmdId, val in value.items():
        print('recvTsl {}:{}'.format(cmdId, val))


def App_cmdReadTslCb(ids, pkgId):
    print('readTsl ids:{} pkgId:{}'.format(ids, pkgId))
    value = dict()
    for id in ids:
        if 1 == id:
            value[1] = 180
        elif 2 == id:
            value[2] = 30
        elif 3 == id:
            value[3] = True
    Qth.ackTsl(1, value, pkgId)


def App_cmdRecvTslServerCb(serverId, value, pkgId):
    print('recvTslServer serverId:{} value:{} pkgId:{}'.format(serverId, value, pkgId))
    Qth.ackTslServer(1, serverId, value, pkgId)


def App_otaPlanCb(plans):
    print('otaPlan:{}'.format(plans))
    Qth.otaAction(1)


def App_fotaResultCb(comp_no, result):
    print('fotaResult comp_no:{} result:{}'.format(comp_no, result))


def nmea_checksum(sentence):
    if sentence.startswith('$'):
        sentence = sentence[1:]

    checksum = 0
    for ch in sentence:
        checksum ^= ord(ch)

    return "{:02X}".format(checksum)


def decimal_to_nmea(value, is_lat):
    abs_val = abs(value)
    degrees = int(abs_val)
    minutes = (abs_val - degrees) * 60.0

    if is_lat:
        direction = 'N' if value >= 0 else 'S'
        coord = "{:02d}{:07.4f}".format(degrees, minutes)
    else:
        direction = 'E' if value >= 0 else 'W'
        coord = "{:03d}{:07.4f}".format(degrees, minutes)

    return coord, direction


def build_gpgga(loc):
    lat, lat_dir = decimal_to_nmea(loc["latitude"], True)
    lon, lon_dir = decimal_to_nmea(loc["longitude"], False)

    body = (
        "$GPGGA,{},".format(loc["utc_time"]) +
        "{},{},".format(lat, lat_dir) +
        "{},{},".format(lon, lon_dir) +
        "1," +
        "{:02d},".format(loc["satellites"]) +
        "{:.2f},".format(loc["hdop"]) +
        "{:.1f},M,,M,,".format(loc["altitude"])
    )

    cs = nmea_checksum(body)
    return "{}*{}".format(body, cs)


def Qth_tslSend(ctx):
    static_var = 0
    gnss = None

    try:
        from quectel import GNSS

        gnss = GNSS()
        if not gnss.start():
            print("GNSS启动失败!")
            return

        print("Qth_tslSend thread start")

        while ctx["running"]:
            try:
                # 先判断连接云平台状态
                if Qth.state():
                    Qth.sendTsl(1, {1: static_var})
                    static_var += 1
                    print("send:", {1: static_var})
                    if static_var >= 100:
                        static_var = 0

                    loc = gnss.get_location()
                    if loc:
                        gpgga = build_gpgga(loc)
                        print(gpgga)
                        Qth.sendOutsideLocation(gpgga)

            except Exception as e:
                pass
                print("Qth_tslSend loop exception:{}".format(e))

            # 分段 sleep，方便 Ctrl+C 后更快退出
            for i in range(10):
                if not ctx["running"]:
                    break
                utime.sleep_ms(100)

    except Exception as e:
        print("Qth_tslSend exception:{}".format(e))

    finally:
        if gnss:
            try:
                gnss.stop()
            except Exception as e:
                print("GNSS stop exception:{}".format(e))

        print("Qth_tslSend thread exit")


if __name__ == '__main__':
    tsl_tid = None
    ctx = {"running": True}

    Qth.init()
    Qth.setProductInfo('p11yq3', 'emcxQnJBV0VKZ0l1')
    Qth.setDK("123600000000000")
    Qth.setServer('mqtt://iot-south.quectelcn.com:1883')
    Qth.setVer('v2.0.0')
    eventCb = {
        'devEvent': App_devEventCb,
        'recvTrans': App_cmdRecvTransCb,
        'recvTsl': App_cmdRecvTslCb,
        'readTsl': App_cmdReadTslCb,
        'readTslServer': App_cmdRecvTslServerCb
    }
    Qth.setEventCb(eventCb)

    try:
        Qth.start()
        _thread.stack_size(4096)
        tsl_tid = _thread.start_new_thread(Qth_tslSend, (ctx,))
        _thread.stack_size(2048)

        count = 0
        while True:
            count += 1
            if count >= 5:
                count = 0
                free_mem = gc.mem_free()
                print("Free memory: {} bytes".format(free_mem))

            utime.sleep(1)

    except KeyboardInterrupt:
        print("KeyboardInterrupt, stopping...")

    except Exception as e:
        print("main exception:{}".format(e))

    finally:

        ctx["running"] = False

        if tsl_tid is not None:
            _thread.join(tsl_tid)
        try:
            Qth.stop()
        except Exception as e:
            print("Qth.stop exception:{}".format(e))

        print("app stopped")