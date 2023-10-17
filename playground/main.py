import socket

class App:
    def __init__(self):
        self.client_socket = None

    def socket_connection(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect(('127.0.0.1', 1024))
            print("Connected to server")
            while True:
                pass
        except ConnectionRefusedError:
            print("Connection refused. Is the server running?")

def main():
    client = App()
    client.socket_connection()

if __name__ == '__main__':
    main()