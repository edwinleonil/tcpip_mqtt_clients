from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import time
import sys

class WorkerSignals(QObject):
    finished = pyqtSignal(int)

class Task1(QRunnable):
    def __init__(self,app):
        super().__init__()
        self.signals = WorkerSignals()
        self.app = app

    @pyqtSlot()
    def run(self):
        # long task 1 goes here
        for i in range(10):
            print("thread 1: "+str(i))
            time.sleep(1)
        self.signals.finished.emit(10)
        # print the signal 
        # print(self.signals.finished.signal)
        self.app.thread1_stopped = True
        print(self.app.thread1_stopped)


class Task2(QRunnable):
    def __init__(self,app):
        super().__init__()   
        self.signals = WorkerSignals()
        self.app = app

    @pyqtSlot()    
    def run(self):
        # long task 2 goes here
        for i in range(10):
            print("thread 2: "+str(i))
            time.sleep(0.5)
        self.signals.finished.emit(20)
        # print the signal 
        # print(self.signals.finished)
        self.app.thread2_stopped = True
        print(self.app.thread2_stopped)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Threads")
        self.resize(300, 300)

        # create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.thread2_stoped = False
        self.thread1_stopped = False

        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)
        
        self.button = QPushButton("Start")
        self.layout.addWidget(self.button)
        self.button.clicked.connect(self.start_threads)
        self.show()
        
        
    def start_threads(self):
   
        # create QThreadPool and add the tasks to it
        thread_pool = QThreadPool()
        self.task1 = Task1(app= self)
        self.task2 = Task2(app = self)
        # connect the signals to the thread pool
        self.task1.signals.finished.connect(self.progress_fn)
        self.task2.signals.finished.connect(self.progress_fn)

        thread_pool.start(self.task1)
        thread_pool.start(self.task2)

    def progress_fn(self, n):
        # print a integer
        print(f"Thread {n} finished")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())




