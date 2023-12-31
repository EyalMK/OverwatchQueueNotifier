import asyncio
import os
import socket
import sys
import threading
from threading import Thread

from dotenv import load_dotenv

from DiscordBot import DiscordBot


class User:
    def __init__(self, cl_socket):
        self.__reminder = False
        self.socket = cl_socket

    def get_socket(self):
        return self.socket

    def set_reminder(self, reminder: bool):
        self.__reminder = reminder

    def get_reminder(self):
        return self.__reminder


class App:
    def __init__(self):
        self.discord_bot = None
        self.connected_clients = {}
        self.awaiting_connections = {}

    def init_discord(self):
        self.discord_bot = DiscordBot(self)
        self.discord_bot.run(os.getenv('DISCORD_BOT_TOKEN'))

    def get_discord_bot(self):
        return self.discord_bot

    def get_connected_clients(self):
        return self.connected_clients

    def get_awaiting_connections(self):
        return self.awaiting_connections

    def handle_client_connection(self, socket_conn):
        try:
            while True:
                # If there's a connected client, get the message. Otherwise, there are no connected clients.
                # Break loop and wait for a client.
                try:
                    message = socket_conn.recv(1024).decode()
                except ConnectionResetError:
                    break

                # Read message - if command, take care of it.
                if not message:
                    break
                if message.startswith("!"):
                    self.handle_command(message, socket_conn)
        finally:
            self.remove_client(socket_conn)

    def socket_connection(self):
        # When running dev-env, environment variables SERVER_IP/PORT will be available.
        ip_address = os.getenv('SERVER_IP', '')
        port = int(os.getenv('SERVER_PORT', 60650))
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((ip_address, port))
        server_socket.listen(700)  # Up to 700 concurrent clients.
        print(f'Server listening on {ip_address}:{port}')
        while True:
            socket_conn, _ = server_socket.accept()
            th = threading.Thread(target=self.handle_client_connection, args=(socket_conn,))
            th.start()

    def run_async_coroutine_with_discord_bot(self, socket_conn, method):
        # Since a thread is handling the socket communication, and the call to send the user a message needs to
        # be asynchronous, we need to run the co-routines in a threadsafe environment.

        sender_id = self.get_user_id_from_socket(socket_conn)
        asyncio.run_coroutine_threadsafe(method(sender_id), self.discord_bot.loop)

    def handle_command(self, message, socket_conn):
        if message == '!remind_user':
            self.run_async_coroutine_with_discord_bot(socket_conn, self.discord_bot.send_user_reminder)

        elif message == '!select_hero_unavailable':
            self.run_async_coroutine_with_discord_bot(socket_conn, self.discord_bot.inform_user_select_hero_unavailable)

        elif message == '!select_hero_success':
            self.run_async_coroutine_with_discord_bot(socket_conn, self.discord_bot.inform_user_select_hero_success)

        elif message == '!select_hero_invalid':
            self.run_async_coroutine_with_discord_bot(socket_conn, self.discord_bot.inform_user_select_hero_invalid)

        elif message == '!select_default_hero_unavailable':
            self.run_async_coroutine_with_discord_bot(socket_conn, self.discord_bot.inform_user_select_default_hero_unavailable)

        elif message == '!queue_cancellation_success':
            self.run_async_coroutine_with_discord_bot(socket_conn, self.discord_bot.inform_user_cancel_queue_success)

        elif message == '!not_matching_resolution_error':
            self.run_async_coroutine_with_discord_bot(socket_conn, self.discord_bot.inform_user_resolution_error)

        elif message.startswith('!disconnect'):
            try:
                discord_id = message.split(' ')[1]
                if discord_id is not None:
                    if discord_id in self.awaiting_connections.keys():
                        self.remove_awaiting_connection(discord_id)
                    if discord_id in self.connected_clients.keys():
                        self.remove_client(socket_conn)
            except Exception as e:
                print(f'Disconnection completed unsuccessfully. Failed to remove closed socket from server. {e}')

        elif message.startswith('!found_game'):
            try:
                user_id = self.get_user_id_from_socket(socket_conn)
                obj = message.split(' ')[1]
                map_name = ''
                try:
                    parts = message.split(' ')[2::]
                    map_name = " ".join(parts)
                except:
                    pass

                if not obj:
                    print('Objective mode not provided.')
                    asyncio.run_coroutine_threadsafe(self.discord_bot.notify_user_game_found(user_id),
                                                     self.discord_bot.loop)
                    return
                if not map_name:
                    print('Map name not provided.')
                    asyncio.run_coroutine_threadsafe(self.discord_bot.notify_user_game_found(user_id, obj_mode=obj),
                                                     self.discord_bot.loop)
                    return

                asyncio.run_coroutine_threadsafe(
                    self.discord_bot.notify_user_game_found(user_id, obj_mode=obj, map_name=map_name),
                    self.discord_bot.loop)
            except Exception as e:
                print(f'Game Found Notification unsuccessful. {e}')

        elif message.startswith('!select_hero_scheduled'):
            try:
                parts = message.split(' ')[1::]
                hero = " ".join(parts)
                if not hero:
                    return
                user_id = self.get_user_id_from_socket(socket_conn)
                asyncio.run_coroutine_threadsafe(self.discord_bot.inform_user_select_hero_scheduled(user_id, hero),
                                                 self.discord_bot.loop)
            except Exception as e:
                print(f'Hero scheduling unsuccessful. {e}')

        elif message.startswith('!select_default_hero_success'):
            try:
                parts = message.split(' ')[1::]
                hero = " ".join(parts)
                if not hero:
                    return
                user_id = self.get_user_id_from_socket(socket_conn)
                asyncio.run_coroutine_threadsafe(self.discord_bot.inform_user_select_hero_success(user_id, hero=hero), self.discord_bot.loop)
            except Exception as e:
                print(f'Default hero selection error: {e}')

        elif message.startswith('!queue_cancellation_failed'):
            try:
                errno = message.split(' ')[1]
                sender_id = self.get_user_id_from_socket(socket_conn)
                asyncio.run_coroutine_threadsafe(self.discord_bot.inform_user_cancel_queue_failure(sender_id, errno),
                                                 self.discord_bot.loop)
            except Exception as e:
                print(f'Error logging queue cancellation failure. {e}')

        elif message.startswith('!get_connection_authorization'):
            username = message.split(' ')[1]
            if not username:
                print("Username not provided.")
                return

            task = asyncio.run_coroutine_threadsafe(self.discord_bot.send_socket_user_id_by_username(username),
                                                    self.discord_bot.loop)
            user_id = str(task.result())
            self.awaiting_connections[user_id] = User(socket_conn)
            print(f'Awaiting authorization from {user_id}...')

    def get_user_id_from_socket(self, socket_conn):
        try:
            for user_id, user_obj in self.connected_clients.items():
                if user_obj.socket == socket_conn:
                    return user_id
            raise ValueError('User ID not found for this socket connection')
        except Exception as e:
            print(f'Error: {e}')

    def add_client(self, user_id):
        self.connected_clients[user_id] = self.awaiting_connections[user_id]
        del self.awaiting_connections[user_id]

    def remove_client(self, socket_conn):
        try:
            del self.connected_clients[self.get_user_id_from_socket(socket_conn)]
            print(f'Client disconnected.')
            print(f'Active connections: {len(self.connected_clients)}')
        except Exception as e:
            pass  # User had already disconnected before closing connection.

    def remove_awaiting_connection(self, user_id):
        try:
            del self.awaiting_connections[user_id]
        except Exception as e:
            print(f'Failed to remove client from awaiting connections list. {e}')


def socket_listen(app):
    app.socket_connection()


def main():
    # Load .env
    load_dotenv()

    if len(sys.argv) > 1:
        environment = sys.argv[1]
        if environment == 'dev':
            os.environ['SERVER_IP'] = '127.0.0.1'
            os.environ['SERVER_PORT'] = '1024'

    # Initialize App object
    server = App()

    # Establish socket connection
    socket_thread = Thread(target=socket_listen, args=(server,))
    socket_thread.start()

    # Initialize Discord object
    server.init_discord()


if __name__ == '__main__':
    main()
