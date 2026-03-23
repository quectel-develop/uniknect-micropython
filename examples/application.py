import machine
import time
from ahtx0 import AHT20
from lis2dh12 import LIS2DH12
from st7735 import LCD
from images import QQ_ICON_40x40
from umqtt.robust import MQTTClient
import json
from collections import OrderedDict


# MQTT连接配置
BROKER = '101.37.104.185'
PORT = 46502
USERNAME = 'quectel'
PASSWORD = '12345678'
CLIENT_ID = 'umqtt_client'
TOPIC = b'/a1vvrmkn43t/NiFtKoHMcu6j0VIXtC6e/user/get'

# 创建MQTT客户端
client = MQTTClient(
    client_id = CLIENT_ID,
    server = BROKER,
    port = PORT,
    user = USERNAME,
    password = PASSWORD
)

# 连接到服务器
print(f'### Connecting to {BROKER}:{PORT}...')
client.connect()
print('### Connected successfully !')

# 初始化ADC
ldr = machine.ADC(machine.Pin('C5'))

# 初始化I2C (AHT20 / LIS2DH12)
i2c = machine.I2C(1, freq=400000)
aht20 = AHT20(i2c)
lis2dh = LIS2DH12(i2c) 

# 初始化SPI (LCD)
spi = machine.SPI(1, baudrate=20000000, polarity=0, phase=0)
lcd = LCD(spi, dc_pin='F12', cs_pin='D14')
lcd.set_rotation(3)
lcd.fill_screen(lcd.BLACK)
lcd.show_string(0, 6, 'Voltage', lcd.CYAN, lcd.BLACK, 16)
lcd.show_string(0, 46, 'Temp/Humi', lcd.CYAN, lcd.BLACK, 16)
lcd.show_string(0, 86, 'G-Sensor', lcd.CYAN, lcd.BLACK, 16)
lcd.show_image(100, 10, 40, 40, QQ_ICON_40x40)

# 获取光敏电阻对应的电压
def get_voltage():
    value_16bit = ldr.read_u16()  # 0-65535
    value_12bit = value_16bit >> 4  # 0-4095
    return (value_12bit * 3.3) / 4096.0

# 主循环
try:
    while True:
        # 获取光敏电阻对应的电压
        voltage = get_voltage()
        print(f'Voltage: {voltage:.2f}V')
        
        # 读取温湿度
        temp = aht20.temperature
        humi = aht20.relative_humidity
        print(f'Temp / Humi: {temp:.1f}C / {humi:.1f}%')
        
        # 读取加速度
        acc_x, acc_y, acc_z = lis2dh.acceleration
        print(f'G-Sensor: X:{acc_x:+.3f} Y:{acc_y:+.3f} Z:{acc_z:+.3f}')
        
        # LCD显示
        lcd.show_string(0, 26, f'{voltage:.2f}V', lcd.YELLOW, lcd.BLACK, 16)
        lcd.show_string(0, 68, f'{temp:.1f}C / {humi:.1f}%', lcd.YELLOW, lcd.BLACK, 16)
        lcd.show_string(0, 106, f'X:{acc_x:.2f} Y:{acc_y:.2f} Z:{acc_z:.2f}', lcd.YELLOW, lcd.BLACK, 16)
        lcd.flush()
        
        # 定义一个有序字典，并json序列化
        data = OrderedDict()
        data["Voltage"] = round(voltage, 2)
        data["Temp"] = round(temp, 1)
        data["Humi"] = round(humi, 1)
        data["G-Sensor"] = {"X": round(acc_x, 3), "Y": round(acc_y, 3), "Z": round(acc_z, 3)}
        data_post = json.dumps(data)
        print(data_post)
        
        # 上传到MQTT服务器
        try:
            client.publish(TOPIC, data_post)
        except Exception as e:
            print(f'*** Publish failed. Err: {e}')
            break
        
        time.sleep(1)
        print('-' * 20 + '\n')
        
except KeyboardInterrupt:
    print('\n### Interrupted.')
finally:
    # 断开MQTT连接
    client.disconnect()
    print('### Disconnected.')


    
