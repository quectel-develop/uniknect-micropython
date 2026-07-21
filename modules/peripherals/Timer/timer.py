from machine import Pin, Timer
import time

led = Pin("LED_BLUE", Pin.OUT, value=0)

def timer_callback(timer):
    # 读取当前电平，再写入相反电平
    led.value(led.value() ^ 1)

tim = Timer(-1)

tim.init(
    period=1000,
    mode=Timer.PERIODIC,
    callback=timer_callback
)
print("创建定时器完成")
try:
    # 保持主程序运行，等待 Ctrl+C
    while True:
        time.sleep_ms(100)

except KeyboardInterrupt:
    print("检测到 Ctrl+C，程序退出")

finally:
    # 关闭定时器，否则定时器仍会继续触发
    tim.deinit()
    led.value(0)
    print("定时器已停止")