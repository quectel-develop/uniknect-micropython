# gnss_thread.py - 使用 join 等待线程退出的版本

import quectel
import time
import _thread

# 全局变量
gnss = None
running = True


def gnss_loop():
    global gnss, running

    try:
        gnss = quectel.GNSS()

        if not gnss.start():
            print("GNSS启动失败!")
            return

        print("开始循环打印定位信息...")

        while running:
            try:
                loc = gnss.get_location()
                now = time.time()

                if loc:
                    print("[{}] 纬度:{:.6f}, 经度:{:.6f}".format(
                        now,
                        loc["latitude"],
                        loc["longitude"]
                    ))
                else:
                    print("[{}] 定位中...".format(now))

                # 分段 sleep，方便更快响应退出
                for i in range(10):
                    if not running:
                        break
                    time.sleep(0.1)

            except Exception as e:
                print("错误:", e)
                break

    finally:
        # 退出循环后清理
        if gnss:
            try:
                gnss.stop()
                print("GNSS线程已退出")
            except Exception as e:
                print("GNSS stop failed:", e)


# 启动线程
_thread.stack_size(4096)
thread_id = _thread.start_new_thread(gnss_loop, ())
print("GNSS线程已启动，thread_id:", thread_id)
print("按Ctrl+C停止")

# 主线程
try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n正在停止...")
    running = False

    print("等待GNSS线程退出...")
    ret = _thread.join(thread_id)
    print("GNSS线程 join:", ret)

    print("程序退出")
