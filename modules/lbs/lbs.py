import _thread
import utime
from quectel import LBS

running = True

def lbs_thread():
    global running

    lbs = LBS()
    print("[LBS线程] 启动")

    while running:
        print("[LBS线程] 开始定位...")

        try:
            loc = lbs.get_location(15000)   # 15秒超时
            if loc:
                print("定位成功:", loc["latitude"], loc["longitude"])
            else:
                print("定位失败")
        except Exception as e:
            print("定位异常:", e)

        # 每10秒定位一次，分段sleep方便退出
        for i in range(10):
            if not running:
                break
            utime.sleep(1)

    lbs.deinit()
    print("[LBS线程] 退出")


print("===== LBS周期定位测试 =====")
print("按 Ctrl+C 退出")

tid = _thread.start_new_thread(lbs_thread, ())
print("线程ID:", tid)

try:
    while True:
        utime.sleep(1)

except KeyboardInterrupt:
    print("收到 Ctrl+C，退出中...")
    running = False
    _thread.join(tid)
    print("测试结束")