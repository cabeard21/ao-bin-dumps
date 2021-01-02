import queue
import threading


exit_flag = 0
queue_lock = threading.Lock()
work_queue = queue.Queue(50)
result_lock = threading.Lock()


class MyThread(threading.Thread):

    def __init__(self, fun, q, results):
        threading.Thread.__init__(self)
        self.fun = fun
        self.q = q
        self.results = results

    def run(self):
        print(f"{self.getName()} Begin processing...")
        process_data(self.fun, self.q, self.results, self.getName())
        print(f"{self.getName()} Finished processing.")


def process_data(fun, q, results, thread_name):
    while not exit_flag:
        queue_lock.acquire()
        if not work_queue.empty():
            data = q.get()
            queue_lock.release()
            print(f"{thread_name} calling function on {data}...")
            res = fun(data)
            print(f"{thread_name} finished function call.")
            result_lock.acquire()
            results.append(res)
            result_lock.release()

        else:
            queue_lock.release()


def set_exit_flag(new_flag):
    global exit_flag
    exit_flag = new_flag
