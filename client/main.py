import os
import socket
import sys
import keepalive
from threading import Thread
from ClientUI import LoginScreen
from ClientHandler import ClientHandler


class App:
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
            self.client_socket.connect((ip_address, port))
            keepalive.set(self.client_socket)  # After 60 seconds of idleness, send a keepalive packet to the server
            # to avoid forced connection closing from the server.
            print(f'Client has connected to server @ {ip_address}:{port}. Awaiting Discord Authorization...')
        except ConnectionRefusedError:
            print('Connection refused.')

    def init_client_handler(self):
        self.client_handler = ClientHandler(self.client_socket, self)
        self.client_handler.run()

    def init_client(self):
        self.client = LoginScreen(self.client_handler)
        self.client.show()

    def load_config(self):
        home_dir = os.path.expanduser("~")
        config_dir = os.path.join(home_dir, 'Documents', 'OverwatchQueueNotifier')
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

    def get_client_ui(self):
        return self.client

    def destroy_gui(self):
        self.client.window.destroy()

    def start(self):
        # Establish socket connection
        socket_thread = Thread(target=self.socket_connection)
        socket_thread.start()

        # Allow some time for the socket connection to be established
        socket_thread.join(timeout=5)  # Adjust timeout as needed

        # Create configuration environment
        self.load_config()

        # Initialize Client Handler
        self.init_client_handler()

        # Initialize Tkinter
        self.init_client()

    def quit(self):
        self.client.window.destroy()
        sys.exit()


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
