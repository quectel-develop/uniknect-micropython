from machine import Pin
import time

# 初始化连接到LED的引脚为输出模式
led = Pin('LED_BLUE', Pin.OUT, Pin.PULL_NONE, value=0)
led.value(1) #led.on()/led.high()
time.sleep(2)
led.value(0) #led.off()/led.low()

button = machine.Pin('SW', Pin.IN, Pin.PULL_DOWN)

last_interrupt_time = 0
DEBOUNCE_MS = 200  # 200ms防抖动时间窗口

def button_handler(pin):
    global last_interrupt_time
    
    current_time = time.ticks_ms()
    
    # 关键：如果距离上次中断时间小于200ms，则直接放弃
    if time.ticks_diff(current_time, last_interrupt_time) < DEBOUNCE_MS:
        return  # 直接返回，不处理本次中断
    last_interrupt_time = current_time
    
    # 原有的消抖逻辑
    
    # 延时后再次确认电平状态
    if pin.value() == 1:  # 确认是稳定的按下状态
        print("press button！")

button.irq(trigger=Pin.IRQ_RISING, handler=button_handler)
print("start testing")
while True:
    time.sleep(1)