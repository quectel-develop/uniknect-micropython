import utime

print("boot start")

try:
    import Qth

    if Qth.apply_pending_update():
        print("OTA script update applied")

except Exception as e:
    print("boot ota exception:", e)

print("boot done")
import example_ota
example_ota.app_start()