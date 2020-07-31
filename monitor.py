import threading
import tkinter.messagebox as tk


class ThreadMonitor(threading.Thread):
    def run(self):  # Default called function with mythread.start()
        print("{} started!".format(self.getName()))
        tk.showinfo(title="Greetings", message="Hello World!")
        print("{} finished!".format(self.getName()))
