from PyQt6.QtCore import QRunnable, QThreadPool
import time

class Task1(QRunnable):
    def run(self):
        # long task 1 goes here
        for i in range(10):
            print("thread 1: "+str(i))
            time.sleep(1)
        return

class Task2(QRunnable):
    def run(self):
        # long task 2 goes here
        for i in range(10):
            print("thread 2: "+str(i))
            time.sleep(0.5)
        return

# create instances of Task1 and Task2
task1 = Task1()
task2 = Task2()

# create QThreadPool and add the tasks to it
thread_pool = QThreadPool()
thread_pool.start(task1)
thread_pool.start(task2)