from quectel import SMS
import math

PI = 3.1415926535897932384626
A = 6378245.0
EE = 0.00669342162296594323


def out_of_china(lng, lat):
    return not (72.004 <= lng <= 137.8347 and 0.8293 <= lat <= 55.8271)


def transform_lat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) +
            20.0 * math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * PI) +
            40.0 * math.sin(lat / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * PI) +
            320.0 * math.sin(lat * PI / 30.0)) * 2.0 / 3.0
    return ret


def transform_lng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) +
            20.0 * math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * PI) +
            40.0 * math.sin(lng / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * PI) +
            300.0 * math.sin(lng / 30.0 * PI)) * 2.0 / 3.0
    return ret


def wgs84_to_gcj02(lng, lat):
    if out_of_china(lng, lat):
        return lng, lat

    dlat = transform_lat(lng - 105.0, lat - 35.0)
    dlng = transform_lng(lng - 105.0, lat - 35.0)

    radlat = lat / 180.0 * PI
    magic = math.sin(radlat)
    magic = 1 - EE * magic * magic
    sqrtmagic = math.sqrt(magic)

    dlat = (dlat * 180.0) / ((A * (1 - EE)) / (magic * sqrtmagic) * PI)
    dlng = (dlng * 180.0) / (A / sqrtmagic * math.cos(radlat) * PI)

    mg_lat = lat + dlat
    mg_lng = lng + dlng

    return mg_lng, mg_lat


# 你的 GPS 原始坐标，QGPSLOC 里是 纬度,经度
gps_lat = 31.82188
gps_lng = 117.11582

# 转高德 GCJ02
amap_lng, amap_lat = wgs84_to_gcj02(gps_lng, gps_lat)

# 高德链接 position 顺序是：经度,纬度
url = "https://uri.amap.com/marker?position={:.6f},{:.6f}&name=SOS".format(
    amap_lng,
    amap_lat
)

msg = "SOS(GPS):" + url

# 需要切换到usim卡
sms = SMS()
sms.send("15256042186", msg)
sms.deinit()