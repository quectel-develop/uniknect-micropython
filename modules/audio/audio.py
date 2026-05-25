from quectel import Audio
import time

RECORD_FILE = "SD:test.wav"

def event_cb(evt):
    if evt == Audio.PLAY_END:
        print("play finished")
    elif evt == Audio.PLAY_STOP:
        print("play stopped")
    elif evt == Audio.TTS_END:
        print("tts finished")
    elif evt == Audio.TTS_STOP:
        print("tts stopped")
    else:
        print("unknown event:", evt)
def audio_demo_exec(audio, cmd):
    if cmd == 1:
        audio.record_start(RECORD_FILE)
    elif cmd == 2:
        audio.record_stop()
    elif cmd == 3:
        audio.play_local(RECORD_FILE, True)
    elif cmd == 4:
        audio.play_stop()
    elif cmd == 5:
        audio.tts_play("今天天气38度，请注意降温。")
    elif cmd == 6:
        audio.tts_stop()
    elif cmd == 7:
        audio.tts_set_speed(85)
    elif cmd == 8:
        print(audio.tts_get_speed())
    elif cmd == 9:
        audio.tts_set_volume(50)
    elif cmd == 10:
        print(audio.tts_get_volume())
    elif cmd == 11:
        audio.set_speaker_volume(5)
    elif cmd == 12:
        print(audio.get_speaker_volume())   
    else:
        print("Unknown cmd:", cmd)


def audio_demo():
    audio = Audio()

    if not audio.init(event_cb):
        print("Audio init failed")
        return

    print("Audio demo start")
    print("1: Start record")
    print("2: Stop record")
    print("3: Play local file")
    print("4: Stop Play local file")
    print("5: Play TTS")
    print("6: Stop Play TTS")
    print("7: Set TTS Speed")
    print("8: Get TTS Speed")
    print("9: Set TTS Volume")
    print("10: Get TTS Volume")
    print("11: Set Speaker Volume")
    print("12: Get Speaker Volume")
    print("0: Exit")

    while True:
        try:
            cmd = int(input("Input cmd: "))
        except Exception:
            print("Invalid input")
            continue

        if cmd == 0:
            break

        try:
            audio_demo_exec(audio, cmd)
        except Exception as e:
            print("Command failed:", e)

    audio.deinit()
    print("Audio demo end")


# 运行 demo
audio_demo()