from get_data import ThreadData
from monitor import ThreadMonitor
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
import resource

app = QApplication([])
app.setQuitOnLastWindowClosed(False)

# Create the icon
icon = QIcon(":/color.png")


def open_monitor():
    # ...Instantiate a thread and pass a unique ID to it
    thread_monitor = ThreadMonitor(name="Thread Monitor", daemon=False)
    thread_monitor.start()  # ...Start the thread, run method will be invoked
    thread_monitor.join()


# Create the tray
tray = QSystemTrayIcon()
tray.setIcon(icon)
tray.setVisible(True)

# Create the menu
menu = QMenu()
action1 = QAction("Monitor")
action1.triggered.connect(open_monitor)
menu.addAction(action1)

quit = QAction("Sair")
quit.triggered.connect(app.quit)
menu.addAction(quit)

# Add the menu to the tray
tray.setContextMenu(menu)

thread_data = ThreadData(name="Thread Data", daemon=True)  # ...Instantiate a thread and pass a unique ID to it
thread_data.start()  # ...Start the thread, run method will be invoked

app.exec_()
