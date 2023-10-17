import time
import psutil
from threading import Thread


class ClientHandler:
    reminder = False
    connected_as = None  # Discord user

    def __init__(self, socket, client_app):
        self.client_socket = socket
        self.client_app = client_app
        print("Client Handler is running...")

        self.run()

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                print(f'Received message: {message}')
                if message == 'set_reminder_true':
                    self.activate_reminder()
                elif message == 'set_reminder_false':
                    self.deactivate_reminder()
                elif message == 'test_game_finished':
                    self.game_finished()
                elif message == 'test_exit':
                    self.exit_program()
                elif message == 'test_exit_game':
                    self.exit_game()
                elif message == '$user_id_not_found' or message == '$user_already_logged_in':  # Error messages from
                    # server.
                    self.exit_program()

                if message.startswith('!authorized_login'):  # Command message from server.
                    self.authorized_login(message)
            except Exception as e:
                print(f'Waiting for a message... {e}')
                time.sleep(3)

    def run(self):
        # Create a thread to manage socket communication.
        socket_listen_thread = Thread(target=self.receive_messages, args=())
        socket_listen_thread.start()

        # Rest of code logic.

    def activate_reminder(self):
        self.reminder = True

    def deactivate_reminder(self):
        self.reminder = False

    def get_reminder(self):
        return self.reminder

    def cancel_queue(self):
        pass

    def select_hero(self, hero=None):
        pass

    def game_found(self):
        pass

    def game_finished(self):
        if self.reminder:
            print('Reminding user...')
            self.client_socket.send(b'!remind_user')

    def link_discord_user(self, discord_id):
        try:
            message = f'!get_connection_authorization {discord_id}'
            self.client_socket.send(message.encode())
        except Exception as e:
            print(f'Error - Could not connect discord user to server. {e}')

    def authorized_login(self, message):
        try:
            username = message.split(' ')[1]
            self.connected_as = username
            print(f'Connected discord user {self.connected_as} to server.')
            self.client_app.switch_to_main_window()
        except Exception as e:
            print(f'Error connecting to server. Restart and try again please. {e}')

    def exit_program(self):
        pass

    def exit_game(self):
        game_name = "Overwatch.exe"
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name'] == game_name:
                print(f"Terminating {process.info['name']} (PID: {process.info['pid']})")
                process.terminate()
                return
