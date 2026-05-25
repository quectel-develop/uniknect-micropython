import _thread
import utime

a = 0
test = False

# 创建一个 lock 的实例
lock = _thread.allocate_lock()


def th_func(delay, id):
    global a

    while True:
        lock.acquire()
        if a >= 10:
            print("thread %d exit" % id)
            lock.release()
            break

        a += 1
        print("[thread %d] a is %d" % (id, a))
        lock.release()

        utime.sleep(delay)


def th_func1():
    global test

    while True:
        if test is True:
            break

        print("thread th_func1 is running")
        utime.sleep(1)

    print("thread th_func1 exit")


if __name__ == "__main__":
    tids = []

    # 创建两个工作线程
    for i in range(2):
        tid = _thread.start_new_thread(th_func, (i + 1, i))
        tids.append(tid)
        print("start thread %d, tid: %s" % (i, tid))

    # 创建后台线程
    thread_id = _thread.start_new_thread(th_func1, ())
    print("start th_func1, tid: %s" % thread_id)

    # 等待两个工作线程退出
    for tid in tids:
        print("wait thread tid %s exit..." % tid)
        ret = _thread.join(tid)
        print("thread tid %s join: %s" % (tid, ret))

    # 两个工作线程都退出后，通知 th_func1 退出
    test = True

    # 等待 th_func1 退出
    print("wait th_func1 tid %s exit..." % thread_id)
    ret = _thread.join(thread_id, 3000)
    print("th_func1 join: %s" % ret)

    print("all threads stopped")
