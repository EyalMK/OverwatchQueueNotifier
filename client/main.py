import socket
import threading
from threading import Thread
from ClientUI import MainWindow, DiscordPopUp
from QueueWatcher import QueueWatcher


class App:
    def __init__(self):
        self.client_socket = None
        self.client = None  # Tkinter Window
        self.queue_watcher = None

    def socket_connection(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(('127.0.0.1', 1024))
            print('Client has connected to server. Awaiting Discord Username...')
        except ConnectionRefusedError:
            print('Connection refused.')

    def init_queue_watcher(self):
        self.queue_watcher = QueueWatcher(self.client_socket)
        self.queue_watcher.run()

    def init_gui(self):
        self.client = DiscordPopUp(self.queue_watcher, self.switch_to_main_window)
        self.client.window.mainloop()

    def switch_to_main_window(self):
        self.client.window.destroy()
        self.client = MainWindow(self.queue_watcher)
        self.client.show()

    def start(self):
        # Establish socket connection
        socket_thread = Thread(target=self.socket_connection)
        socket_thread.start()

        # Allow some time for the socket connection to be established
        socket_thread.join(timeout=5)  # Adjust timeout as needed

        # Initialize Queue Watcher Object
        self.init_queue_watcher()

        # Initialize Window Object
        self.init_gui()


def main():
    # Initialize App Object
    client = App()

    # Start routine
    client.start()


if __name__ == '__main__':
    main()
