import asyncio
import socket
from dotenv import load_dotenv
from threading import Thread
import os
from DiscordBot import DiscordBot


class App:
    def __init__(self):
        self.discord_bot = None
        self.connected_clients = {}
        self.active_connections = 0

    def init_discord(self):
        self.discord_bot = DiscordBot(self)
        self.discord_bot.run(os.getenv('DISCORD_BOT_TOKEN'))

    def get_discord_bot(self):
        return self.discord_bot

    def get_connected_clients(self):
        return self.connected_clients

    def socket_connection(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('127.0.0.1', 1024))
        server_socket.listen(3)
        while True:
            socket_conn, address = server_socket.accept()
            try:
                while True:
                    # If there's a connected client, get the message. Otherwise, there are no connected clients.
                    # Break loop and wait for a client.
                    try:
                        message = socket_conn.recv(1024).decode()
                    except ConnectionResetError:
                        break

                    # Read message - if command, take care of it. Otherwise, it's a user_id.
                    if not message:
                        break
                    print(f'Server: got message {message}')
                    if message.startswith("!"):
                        self.handle_command(message, socket_conn)
                    else:
                        self.add_client(message, socket_conn)
                        print("Accepted connection from client")
                        self.active_connections += 1
                        print(f'Current active connections: {self.active_connections}')
            finally:
                self.remove_client(socket_conn)
                socket_conn.close()
                print("Client disconnected")
                self.active_connections -= 1
                print(f'Current active connections: {self.active_connections}')


    def handle_command(self, message, socket_conn):
        if message == '!remind_user':
            sender_id = self.get_user_id_from_socket(socket_conn)
            # Since a thread is handling the socket communication, and the call to send the user a message needs to
            # be asynchronous, we need to run the co-routine In a threadsafe environment.
            asyncio.run_coroutine_threadsafe(self.discord_bot.send_user_reminder(sender_id), self.discord_bot.loop)
        elif message.startswith('!get_user_id'):
            username = message.split(' ')[1]
            if not username:
                raise Exception("Username not provided.")
            print(f'Getting user id now... {username}')
            asyncio.run_coroutine_threadsafe(self.discord_bot.send_socket_user_id_by_username(username, socket_conn), self.discord_bot.loop)

    def get_user_id_from_socket(self, socket_conn):
        try:
            # O(1) Time and Space complexity.
            users = list(self.connected_clients.keys())
            sockets = list(self.connected_clients.values())

            sender_socket = sockets.index(socket_conn)
            return users[sender_socket]
        except Exception as e:
            print(f'Discord User ID of this connection was not found. Error. {e}')

    def add_client(self, user_id, client_socket):
        self.connected_clients[user_id] = client_socket

    def remove_client(self, socket_conn):
        try:
            del self.connected_clients[self.get_user_id_from_socket(socket_conn)]
        except Exception as e:
            print(f'Failed to disconnect client from server. Error. {e}')


def socket_listen(app):
    app.socket_connection()


def main():
    # Load .env
    load_dotenv()

    # Initialize App object
    server = App()

    # Establish socket connection
    socket_thread = Thread(target=socket_listen, args=(server,))
    socket_thread.start()

    print('Server is now listening for connections...')

    # Initialize Discord object
    server.init_discord()


if __name__ == '__main__':
    main()
