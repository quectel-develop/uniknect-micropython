from pyb import Pin, Timer
import time

# 使用板载蓝灯
led = Pin('LED_BLUE')

tim = Timer(4, freq=1000)
ch = tim.channel(2, Timer.PWM, pin=led)

print("PWM start on LED_BLUE")
print("按 Ctrl+C 退出，并自动 deinit 定时器")

try:
    while True:
        ch.pulse_width_percent(10)
        print("duty = 10%")
        time.sleep(4)

        ch.pulse_width_percent(50)
        print("duty = 50%")
        time.sleep(4)

        ch.pulse_width_percent(90)
        print("duty = 90%")
        time.sleep(4)

except KeyboardInterrupt:
    print("KeyboardInterrupt")

finally:
    # 先把输出占空比清零
    try:
        ch.pulse_width_percent(0)
    except:
        pass

    # 再反初始化定时器
    try:
        tim.deinit()
    except:
        pass
