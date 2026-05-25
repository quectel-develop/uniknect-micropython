import _thread
import utime
import sys

class ProducerConsumer:
    def __init__(self):
        self.items = []
        self.lock = _thread.allocate_lock()
        self.semaphore = _thread.allocate_semaphore(0)
        self.running = True
        self.producer_count = 0
        self.consumer_count = 0

        self.producer_tid = None
        self.consumer_tid = None

    def producer(self):
        """生产者线程"""
        print("[生产者] 启动")

        while self.running:
            self.producer_count += 1
            item = "商品{}".format(self.producer_count)

            with self.lock:
                self.items.append(item)
                print("[生产] {}，库存: {}".format(item, len(self.items)))

            self.semaphore.release()

            # 2秒生产一个，但支持中断
            for i in range(40):  # 40 * 50ms = 2秒
                if not self.running:
                    print("[生产者] 退出")
                    return
                utime.sleep_ms(50)

        print("[生产者] 退出")

    def consumer(self):
        """消费者线程"""
        print("[消费者] 启动")

        while self.running:
            # 等待产品，支持中断
            try:
                if self.semaphore.acquire():  # 最多等0.5秒
                    if not self.running:
                        break

                    with self.lock:
                        if self.items:
                            item = self.items.pop(0)
                            self.consumer_count += 1
                            print("[消费] {}，剩余: {}".format(item, len(self.items)))
                else:
                    continue  # 超时，检查退出标志
            except Exception as e:
                if not self.running:
                    break
                print("[消费者] semaphore 异常:", e)

            # 1秒消费一个，但支持中断
            for i in range(20):  # 20 * 50ms = 1秒
                if not self.running:
                    print("[消费者] 退出")
                    return
                utime.sleep_ms(50)

        print("[消费者] 退出")

    def start(self):
        """启动线程"""
        self.producer_tid = _thread.start_new_thread(self.producer, ())
        self.consumer_tid = _thread.start_new_thread(self.consumer, ())

        print("[系统] producer_tid:", self.producer_tid)
        print("[系统] consumer_tid:", self.consumer_tid)

    def status(self):
        """显示状态"""
        with self.lock:
            return "生产: {}个, 消费: {}个, 库存: {}".format(
                self.producer_count,
                self.consumer_count,
                len(self.items)
            )

    def stop(self):
        """停止所有线程"""
        print("\n正在停止程序...")
        self.running = False

        # 释放信号量，让可能阻塞在 acquire() 的消费者退出
        try:
            self.semaphore.release()
        except Exception as e:
            print("[系统] release semaphore 异常:", e)

        # 等待生产者退出
        if self.producer_tid is not None:
            print("[系统] 等待生产者线程退出...")
            ret = _thread.join(self.producer_tid)
            print("[系统] 生产者 join:", ret)

        # 等待消费者退出
        if self.consumer_tid is not None:
            print("[系统] 等待消费者线程退出...")
            ret = _thread.join(self.consumer_tid)
            print("[系统] 消费者 join:", ret)

        print("最终状态: {}".format(self.status()))
        print("程序已停止")
        sys.exit(0)

def main():
    """主函数"""
    print("=== 生产者消费者演示 ===")
    print("生产者: 2秒/个")
    print("消费者: 1秒/个")
    print("按 Ctrl+C 退出程序\n")

    pc = ProducerConsumer()

    # 启动线程
    pc.start()

    try:
        # 主循环
        counter = 0
        while True:
            utime.sleep(1)
            counter += 1

            # 每5秒显示状态
            if counter % 5 == 0:
                print("\n[系统状态] {}".format(pc.status()))

    except KeyboardInterrupt:
        pc.stop()

if __name__ == "__main__":
    main()
