# main.py - 同时读取AHT20和LIS2DH12
import machine
import time
from lis2dh12 import LIS2DH12
from st7735 import LCD
# 初始化I2C
i2c = machine.I2C(1, freq=400000)
spi = machine.SPI(1, baudrate=20000000, polarity=0, phase=0)
lcd = LCD(spi, dc_pin="F12", cs_pin="D14")
lcd.set_rotation(0)
# 初始化LIS2DH12
lis2dh = LIS2DH12(i2c) 
print("LIS2DH12 就绪")
lcd.show_string(0, 0, "Acceleration", lcd.BLUE, lcd.BLACK, 16)
# 主循环
while True:
    
    # 读取加速度
    acc_x, acc_y, acc_z = lis2dh.acceleration
    
    # 显示结果
    print("加速度 X:{:+.3f} Y:{:+.3f} Z:{:+.3f} m/s²".format(acc_x, acc_y, acc_z))
    print("---")
    lcd.show_string(0, 20, f"X:{acc_x:+.2f}", lcd.WHITE, lcd.BLACK, 16)
    lcd.show_string(0, 40, f"Y:{acc_y:+.2f}", lcd.WHITE, lcd.BLACK, 16)
    lcd.show_string(0, 60, f"Z:{acc_z:+.2f}", lcd.WHITE, lcd.BLACK, 16)
    lcd.flush()
    time.sleep(1)