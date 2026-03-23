from quectel import Voice
import time


def voice_cb(id, direction, state, number):
    if state == Voice.STATE_IDLE:
        state_str = "IDLE"
    elif state == Voice.STATE_HOLD:
        state_str = "HOLD"
    elif state == Voice.STATE_ORIGINAL:
        state_str = "ORIGINAL"
    elif state == Voice.STATE_CONNECT:
        state_str = "CONNECT"
    elif state == Voice.STATE_INCOMING:
        state_str = "INCOMING"
    elif state == Voice.STATE_WAITING:
        state_str = "WAITING"
    elif state == Voice.STATE_END:
        state_str = "END"
    elif state == Voice.STATE_ALERTING:
        state_str = "ALERTING"
    else:
        state_str = "UNKNOWN"

    # 呼叫方向
    if direction == Voice.DIR_MO:
        dir_str = "MO"
    elif direction == Voice.DIR_MT:
        dir_str = "MT"
    else:
        dir_str = "UNKNOWN"

    # 打印
    print("===== VOICE EVENT =====")
    print("call id:", id)
    print("direction:", dir_str)
    print("state:", state_str, f"({state})")
    print("number:", number)
    print("=======================")


# 主循环菜单
def menu():
    print("")
    print("===== Voice Test Menu =====")
    print("1. Dial number")
    print("2. Hang up")
    print("3. Answer")
    print("4. Exit")

v = Voice()
v.init(voice_cb)
while True:
    menu()
    cmd = input("Select: ")

    if cmd == "1":
        num = input("Number: ")
        v.dial(num)
    elif cmd == "2":
        v.hangup()
    elif cmd == "3":
        v.answer()
    elif cmd == "4":
        v.deinit()
        break
    else:
        print("Invalid command")
    time.sleep(0.1)
