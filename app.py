import socket
from threading import Thread
import warnings
import pygal
import pandas as pd
import numpy as np
from statsmodels.tsa.api import SimpleExpSmoothing
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
import time
from datetime import datetime, date, timedelta
import psutil
import requests
from requests.exceptions import HTTPError

import resource

INTERVAL_SECONDS_DATA = 2

warnings.filterwarnings("ignore")
mydateparser = lambda x: datetime.strptime(x, "%d/%m/%Y %H:%M:%S")
url = 'https://api-monitor-utfpr.herokuapp.com/monitor'


# MONITOR
def plot_data(series, labels, is_cpu=False):
    line_chart = pygal.DateTimeLine(
        x_label_rotation=35,
        truncate_label=-1,
        x_value_formatter=lambda dt: dt.strftime('%d/%m/%Y - %H:%M:%S'),
        show_dots=False
    )

    line_chart.title = 'CPU' if is_cpu else 'Memory'
    for idx, val in enumerate(series):
        line_chart.add(labels[idx], val)
    # line_chart.render_to_png('cpuGraph.png' if is_cpu else 'memoryGraph.png')
    line_chart.render_in_browser()


def format_values(frame):
    rowns_invalid = []
    for index, row in frame.iterrows():
        if not isinstance(row['date'], str):
            rowns_invalid.append(index)

    if len(rowns_invalid) > 0:
        frame = frame.drop(rowns_invalid)

    frame['date'] = frame['date'].apply(mydateparser)
    return frame


def filter_day(frame):
    today = date.today()
    yesterday = today - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    tomorrow = today + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")

    return frame[(frame['date'] > yesterday_str) & (frame['date'] < tomorrow_str)]


class ThreadCPU(Thread):
    def __init__(self, name, daemon, small=False):
        Thread.__init__(self, name=name, daemon=daemon)
        self.small = small

    def run(self):  # Default called function with mythread.start()
        print("{} started!".format(self.getName()))

        data = pd.read_csv('cpuData.txt', dtype={'date': str, 'cpu': np.float16}, sep=';', names=['date', 'cpu'])

        data = format_values(data)

        # Simple Exponential Smoothing
        fit = SimpleExpSmoothing(data['cpu']).fit(smoothing_level=0.2, optimized=False)
        data['cpu'] = fit.fittedvalues
        # END

        data = filter_day(data)

        if self.small:
            data = data.tail(50)

        plot_data([data.to_numpy()], ['0.2'], is_cpu=True)

        print("{} finished!".format(self.getName()))


class ThreadMemory(Thread):
    def __init__(self, name, daemon, small=False):
        Thread.__init__(self, name=name, daemon=daemon)
        self.small = small

    def run(self, tk=None):  # Default called function with mythread.start()
        print("{} started!".format(self.getName()))

        data = pd.read_csv('memoriaData.txt', dtype={'date': str, 'memory': np.float16}, sep=';',
                           names=['date', 'memory'])

        data = format_values(data)

        # Simple Exponential Smoothing
        fit = SimpleExpSmoothing(data['memory']).fit(smoothing_level=0.2, optimized=False)
        data['memory'] = fit.fittedvalues
        # END

        data = filter_day(data)

        if self.small:
            data = data.tail(50)

        plot_data([data.to_numpy()], ['0.2'])

        print("{} finished!".format(self.getName()))

# END MONITOR

# GETDATA


class ThreadData(Thread):
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

            time.sleep(INTERVAL_SECONDS_DATA)  # Pretend to work for a second

        print("{} finished!".format(self.getName()))


# END GETDATA


# MAIN

def open_monitor_cpu():
    # ...Instantiate a thread and pass a unique ID to it
    thread_cpu = ThreadCPU(name="Thread CPU 1", daemon=False)
    thread_cpu.start()  # ...Start the thread, run method will be invoked
    thread_cpu.join()


def open_monitor_memory():
    # ...Instantiate a thread and pass a unique ID to it
    thread_memory = ThreadMemory(name="Thread Memo 1", daemon=False)
    thread_memory.start()  # ...Start the thread, run method will be invoked
    thread_memory.join()


#
def open_monitor_cpu_sm():
    # ...Instantiate a thread and pass a unique ID to it
    thread_cpu2 = ThreadCPU(name="Thread CPU 2", daemon=False, small=True)
    thread_cpu2.start()  # ...Start the thread, run method will be invoked
    thread_cpu2.join()


def open_monitor_memory_sm():
    # ...Instantiate a thread and pass a unique ID to it
    thread_memory2 = ThreadMemory(name="Thread Memo 2", daemon=False, small=True)
    thread_memory2.start()  # ...Start the thread, run method will be invoked
    thread_memory2.join()


# API Functions
def send_monitor_cpu_sm():
    computer_name = socket.gethostname()
    today = date.today()
    date_str = today.strftime("%d/%m/%Y")

    #

    data = pd.read_csv('cpuData.txt', dtype={'date': str, 'cpu': np.float16}, sep=';', names=['date', 'cpu'])

    data = format_values(data)

    # Simple Exponential Smoothing
    fit = SimpleExpSmoothing(data['cpu']).fit(smoothing_level=0.2, optimized=False)
    data['cpu'] = fit.fittedvalues

    data = filter_day(data)
    data = data.tail(50)['cpu'].tolist()
    #

    new_list = [round(e, 2) for e in data]

    obj = {
        'computer': computer_name,
        'date': date_str,
        'type': 'cpu',
        'info_array': new_list,
    }

    print(obj)
    
    try:
        r = requests.post(url, json=obj)

        if r.status_code == 200:
            print('Success!')
        else:
            print(f'#{r.status_code} Error.')
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6


def send_monitor_memory_sm():
    computer_name = socket.gethostname()
    today = date.today()
    date_str = today.strftime("%d/%m/%Y")

    #

    data = pd.read_csv('memoriaData.txt', dtype={'date': str, 'memory': np.float16}, sep=';', names=['date', 'memory'])

    data = format_values(data)

    # Simple Exponential Smoothing
    fit = SimpleExpSmoothing(data['memory']).fit(smoothing_level=0.2, optimized=False)
    data['memory'] = fit.fittedvalues

    data = filter_day(data)
    data = data.tail(50)['memory'].tolist()
    #

    new_list = [round(e, 2) for e in data]

    obj = {
        'computer': computer_name,
        'date': date_str,
        'type': 'memory',
        'info_array': new_list,
    }

    print(obj)

    try:
        r = requests.post(url, json=obj)

        if r.status_code == 200:
            print('Success!')
        else:
            print(f'#{r.status_code} Error.')
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6


def get_data_memory_computers():
    today = date.today()
    date_str = today.strftime("%d/%m/%Y")

    #

    obj = {
        'date': date_str,
        'type': 'memory',
    }

    print(obj)

    try:
        r = requests.get(url, json=obj)

        if r.status_code == 200:
            print('Success!')

            f = open("memory_series.txt", "w")
            f.write(r.text)
            f.close()
        else:
            print(f'#{r.status_code} Error.')
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6


def get_data_cpu_computers():
    today = date.today()
    date_str = today.strftime("%d/%m/%Y")

    #

    obj = {
        'date': date_str,
        'type': 'cpu',
    }

    print(obj)

    try:
        r = requests.get(url, json=obj)

        if r.status_code == 200:
            print('Success!')

            f = open("cpu_series.txt", "w")
            f.write(r.text)
            f.close()
        else:
            print(f'#{r.status_code} Error.')
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6


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

    # SMALL
    action3 = QAction("Monitor CPU Small")
    action3.triggered.connect(open_monitor_cpu_sm)
    menu.addAction(action3)

    action4 = QAction("Monitor Memory Small")
    action4.triggered.connect(open_monitor_memory_sm)
    menu.addAction(action4)

    # API
    actionApiCpu = QAction("Send Monitor CPU Small")
    actionApiCpu.triggered.connect(send_monitor_cpu_sm)
    menu.addAction(actionApiCpu)

    actionApiMemory = QAction("Send Monitor Memory Small")
    actionApiMemory.triggered.connect(send_monitor_memory_sm)
    menu.addAction(actionApiMemory)

    #
    actionGetCpu = QAction("Get All Monitor CPU Small")
    actionGetCpu.triggered.connect(get_data_cpu_computers)
    menu.addAction(actionGetCpu)

    actionGetMemory = QAction("Get All Monitor Memory Small")
    actionGetMemory.triggered.connect(get_data_memory_computers)
    menu.addAction(actionGetMemory)



    sair = QAction("Sair")
    sair.triggered.connect(app.quit)
    menu.addAction(sair)

    # Add the menu to the tray
    tray.setContextMenu(menu)

    thread_data = ThreadData(name="Thread Data", daemon=True)  # ...Instantiate a thread and pass a unique ID to it
    thread_data.start()  # ...Start the thread, run method will be invoked

    app.exec_()


if __name__ == "__main__":
    main()
