import os
import socket
import sys
from threading import Thread

import keepalive

from ClientHandler import ClientHandler
from ClientUI import ClientScreen


def load_config():
    home_dir = os.path.expanduser("~")
    config_dir = os.path.join(home_dir, 'Documents', 'OverwatchQueueNotifier')
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)


class App:
    connected = False

    def __init__(self):
        self.client_socket = None
        self.client = None  # Tkinter Window
        self.client_handler = None

    def socket_connection(self):
        try:
            # When running dev-env, environment variables SERVER_IP/PORT will be available.
            ip_address = os.getenv('SERVER_IP', '217.160.99.85')
            port = int(os.getenv('SERVER_PORT', 60650))
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            while not self.connected:
                try:
                    self.client_socket.connect((ip_address, port))
                    keepalive.set(self.client_socket)  # After 60 seconds of idleness, send a keepalive packet to the server
                    # to avoid forced connection closing from the server.
                    self.connected = True
                    print(f'Client has connected to server.\nAwaiting Discord Connection...')
                except ConnectionError as e:
                    print(f'Connection error. {e}')
        except ConnectionError as e:
            print(f'Connection refused. {e}')

    def init_client_handler(self):
        self.client_handler = ClientHandler(self.client_socket, self)

    def init_client(self):
        self.client = ClientScreen(self)
        self.client.show()

    def get_client_ui(self):
        return self.client

    def cleanup(self):
        if self.client_handler is not None:
            self.client_handler.send_disconnect()
            self.client_handler.stop_queue_watcher()
            self.client_handler.close_connection()

    def start(self):
        # Create configuration environment
        load_config()

        # Establish socket connection
        socket_thread = Thread(target=self.socket_connection)
        socket_thread.start()

        # Allow some time for the socket connection to be established
        socket_thread.join(timeout=5)

        # Initialize Client Handler
        client_handler_thread = Thread(target=self.init_client_handler)
        client_handler_thread.start()

        # Initialize Tkinter
        self.init_client()


def main():
    if len(sys.argv) > 1:
        environment = sys.argv[1]
        if environment == 'dev':
            os.environ['SERVER_IP'] = '127.0.0.1'
            os.environ['SERVER_PORT'] = '1024'

    # Initialize App Object
    client = App()

    # Start routine
    client.start()


if __name__ == '__main__':
    main()
