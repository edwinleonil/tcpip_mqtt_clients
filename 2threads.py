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

        self.signals.finished.emit(1)
        self.app.thread1_stopped = True
        print(self.app.thread1_stopped)
        # update the text box
        self.app.text_box.append("Thread 1 finished")


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

        self.signals.finished.emit(2)
        self.app.thread2_stopped = True
        print(self.app.thread2_stopped)
        # update the text box
        self.app.text_box.append("Thread 2 finished")


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
        # add a text box to show the progress
        self.text_box = QTextEdit()
        self.layout.addWidget(self.text_box)

        self.show()
        
        
    def start_threads(self):
        # create QThreadPool and add the tasks to it
        thread_pool = QThreadPool()
        self.task1 = Task1(app= self)
        self.task2 = Task2(app = self)
        # connect the signals to the thread pool and output the result inmediately
        self.task1.signals.finished.connect(self.progress_fn)
        self.task2.signals.finished.connect(self.progress_fn)

        # start the threads   
        thread_pool.start(self.task1)
        thread_pool.start(self.task2)

    def progress_fn(self, n):
        print(f"Thread {n} finished")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())




