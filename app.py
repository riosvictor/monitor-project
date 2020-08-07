import threading
import warnings
import pygal
import pandas as pd
from statsmodels.tsa.api import SimpleExpSmoothing
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
import time
from datetime import datetime
import psutil
import resource

warnings.filterwarnings("ignore")
mydateparser = lambda x: datetime.strptime(x, "%d/%m/%Y %H:%M:%S")


# MONITOR
def plot_data(serie, is_cpu=False):
    line_chart = pygal.DateTimeLine(
        x_label_rotation=35,
        truncate_label=-1,
        x_value_formatter=lambda dt: dt.strftime('%d/%m/%Y - %H:%M:%S')
    )

    line_chart.title = 'CPU' if is_cpu else 'Memory'
    line_chart.add('CPU' if is_cpu else 'Memory', serie)
    # line_chart.render_to_png('cpuGraph.png' if is_cpu else 'memoryGraph.png')
    line_chart.render_in_browser()


class ThreadCPU(threading.Thread):
    def run(self):  # Default called function with mythread.start()
        print("{} started!".format(self.getName()))

        data = pd.read_csv('cpuData.txt'
                           , header=None
                           , sep=';'
                           , date_parser=mydateparser
                           , names=['date', 'cpu']
                           , parse_dates=['date'])

        # Simple Exponential Smoothing
        fit = SimpleExpSmoothing(data['cpu']).fit(smoothing_level=0.2, optimized=False)
        data['cpu'] = fit.fittedvalues
        print(data.head())

        plot_data(data.to_numpy(), is_cpu=True)

        print("{} finished!".format(self.getName()))


class ThreadMemory(threading.Thread):
    def run(self, tk=None):  # Default called function with mythread.start()
        print("{} started!".format(self.getName()))

        data = pd.read_csv('memoriaData.txt'
                           , header=None
                           , sep=';'
                           , date_parser=mydateparser
                           , names=['date', 'memory']
                           , parse_dates=['date'])

        # Simple Exponential Smoothing
        fit = SimpleExpSmoothing(data['memory']).fit(smoothing_level=0.2, optimized=False)

        data['memory'] = fit.fittedvalues
        print(data.head())

        plot_data(data.to_numpy())

        print("{} finished!".format(self.getName()))

# END MONITOR

# GETDATA


class ThreadData(threading.Thread):
    def run(self):  # Default called function with mythread.start()
        print("{} started!".format(self.getName()))
        while True:
            with open('cpuData.txt', 'a+') as arquivoCPU:
                text = datetime.now().strftime("%d/%m/%Y %H:%M:%S; ") + str(
                    psutil.cpu_percent(interval=0.1, percpu=False))
                arquivoCPU.write(text + '\n')

            with open('memoriaData.txt', 'a+') as arquivoMemoria:
                text = datetime.now().strftime("%d/%m/%Y %H:%M:%S; ") + str(psutil.virtual_memory().percent)
                arquivoMemoria.write(text + '\n')

            time.sleep(2)  # Pretend to work for a second

        print("{} finished!".format(self.getName()))


# END GETDATA


# MAIN

def open_monitor_cpu():
    # ...Instantiate a thread and pass a unique ID to it
    thread_cpu = ThreadCPU(name="Thread CPU", daemon=False)
    thread_cpu.start()  # ...Start the thread, run method will be invoked
    thread_cpu.join()

def open_monitor_memory():
    # ...Instantiate a thread and pass a unique ID to it
    thread_memory = ThreadMemory(name="Thread Memory", daemon=False)
    thread_memory.start()  # ...Start the thread, run method will be invoked
    thread_memory.join()


def main():
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)

    # Create the icon
    icon = QIcon(":/color.png")

    # Create the tray
    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)

    # Create the menu
    menu = QMenu()
    action1 = QAction("Monitor CPU")
    action1.triggered.connect(open_monitor_cpu)
    menu.addAction(action1)

    action2 = QAction("Monitor Memory")
    action2.triggered.connect(open_monitor_memory)
    menu.addAction(action2)

    quit = QAction("Sair")
    quit.triggered.connect(app.quit)
    menu.addAction(quit)

    # Add the menu to the tray
    tray.setContextMenu(menu)

    thread_data = ThreadData(name="Thread Data", daemon=True)  # ...Instantiate a thread and pass a unique ID to it
    thread_data.start()  # ...Start the thread, run method will be invoked

    app.exec_()


if __name__ == "__main__":
    main()