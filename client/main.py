import socket
from threading import Thread
from ClientUI import MainWindow, LoginScreen
from ClientHandler import ClientHandler


class App:
    def __init__(self):
        self.client_socket = None
        self.client = None  # Tkinter Window
        self.client_handler = None

    def socket_connection(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(('127.0.0.1', 1024))
            print('Client has connected to server. Awaiting Discord Username...')
        except ConnectionRefusedError:
            print('Connection refused.')

    def init_client_handler(self):
        self.client_handler = ClientHandler(self.client_socket, self)
        self.client_handler.run()

    def init_client(self):
        self.client = LoginScreen(self.client_handler, self.switch_to_main_window)
        self.client.show()

    def get_client_ui(self):
        return self.client

    def switch_to_main_window(self):
        self.client.window.destroy()
        self.client = MainWindow()
        self.client.show()

    def start(self):
        # Establish socket connection
        socket_thread = Thread(target=self.socket_connection)
        socket_thread.start()

        # Allow some time for the socket connection to be established
        socket_thread.join(timeout=5)  # Adjust timeout as needed

        # Initialize Queue Watcher Object
        self.init_client_handler()

        # Initialize Tkinter
        self.init_client()


def main():
    # Initialize App Object
    client = App()

    # Start routine
    client.start()


if __name__ == '__main__':
    main()
