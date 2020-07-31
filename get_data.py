import threading
import time
from datetime import datetime
import psutil


class ThreadData(threading.Thread):
    def run(self):  # Default called function with mythread.start()
        print("{} started!".format(self.getName()))
        while True:

            with open('cpuData.txt', 'a+') as arquivoCPU:
                text = datetime.now().strftime("%d/%m/%Y; %H:%M:%S; ") + str(psutil.cpu_percent(interval=0.1, percpu=False))
                arquivoCPU.write(text+'\n')

            with open('memoriaData.txt', 'a+') as arquivoMemoria:
                text = datetime.now().strftime("%d/%m/%Y; %H:%M:%S; ") + str(psutil.virtual_memory().percent)
                arquivoMemoria.write(text+'\n')

            time.sleep(2)  # Pretend to work for a second

        print("{} finished!".format(self.getName()))
