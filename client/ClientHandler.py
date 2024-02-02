import os
import sys
from threading import Thread

import psutil
from plyer import notification

from GameInfo import get_hero_key, game_data
from QueueWatcher import QueueWatcher

favicon_path = os.getcwd() + '\\assets\\images\\favicon.ico'  # Dev env default path
if getattr(sys, 'frozen', False):
    favicon_path = os.path.join(sys._MEIPASS, './assets/images/favicon.ico')  # Client path


def exit_game():
    game_name = "Overwatch.exe"
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == game_name:
            print(f"Terminating {process.info['name']} (PID: {process.info['pid']})")
            process.terminate()
            return


class ClientHandler:
    socket_thread_running = False
    reminder = False
    queue_watcher = None
    scheduled_hero = None
    hero_select_failed = False

    def __init__(self, socket, main_app):
        self.default_support = None
        self.default_dps = None
        self.default_tank = None
        self.discord_id = None
        self.client_socket = socket
        self.main_app = main_app
        self.run()

    def receive_messages(self):
        while self.socket_thread_running:
            try:
                message = self.client_socket.recv(1024).decode()
                print(f'Received message: {message}')
                if message == 'set_reminder_true':
                    self.activate_reminder()
                elif message == 'set_reminder_false':
                    self.deactivate_reminder()
                elif message == 'cancel_queue':
                    self.cancel_queue()
                elif message == 'exit_game':
                    exit_game()
                elif message == '$user_already_logged_in':  # Error messages from server.
                    # For now, we don't want to do anything.
                    pass

                if message.startswith('!authorized_login'):  # Command message from server.
                    self.authorized_login(message)
                elif message.startswith('!select_hero'):
                    try:
                        parts = message.split(' ')[1::]
                        hero = " ".join(parts)
                        self.schedule_hero(hero, manual=True)
                    except Exception as e:
                        print(f'Error !select_hero - {e}')

            except:
                self.socket_thread_running = False
                print(f'Socket connection terminated.')

    def run(self):
        print("Client Handler is running...")
        # Create a thread to manage socket communication.
        self.socket_thread_running = True
        socket_listen_thread = Thread(target=self.receive_messages, args=())
        socket_listen_thread.start()

    def init_queue_watcher(self):
        self.queue_watcher.start()

    def activate_reminder(self):
        self.reminder = True
        self.main_app.get_client_ui().set_reminder_var('Reminder is set.')

    def deactivate_reminder(self):
        self.reminder = False
        self.main_app.get_client_ui().set_reminder_var('Reminder is not set.')

    def get_reminder(self):
        return self.reminder

    def cancel_queue(self):
        self.queue_watcher.cancel_queue()

    def cancel_queue_failure(self, errno):
        self.client_socket.send(f'!queue_cancellation_failed {errno}'.encode())

    def cancel_queue_success(self):
        self.client_socket.send(b'!queue_cancellation_success')

    def select_hero_scheduled(self):
        self.client_socket.send(b'!select_hero_scheduled')

    def resolutions_not_matching(self):
        self.client_socket.send(b'!not_matching_resolution_error')

    def set_default_tank(self, hero):
        self.default_tank = hero

    def set_default_dps(self, hero):
        self.default_dps = hero

    def set_default_support(self, hero):
        self.default_support = hero

    def set_hero_select_failure(self, boolean):
        self.hero_select_failed = boolean

    def get_default_heroes(self):
        return [hero for hero in [self.default_tank, self.default_support, self.default_dps] if hero is not None]

    def schedule_hero(self, hero, manual=False):
        if hero in game_data['heroes']:
            hero_to_select = get_hero_key(hero)

            if self.queue_watcher.found_game:
                return self.select_hero(hero_to_select, manual)
            else:
                try:
                    self.queue_watcher.set_overwatch_active_window()
                except:
                    pass

                self.scheduled_hero = hero_to_select
                self.client_socket.send(f'!select_hero_scheduled {self.scheduled_hero}'.encode())
        else:
            self.client_socket.send(b'!select_hero_invalid')

    def select_hero(self, hero, manual):
        try:
            default_heroes = self.get_default_heroes()
            self.queue_watcher.select_hero(hero)

            # Selection failed
            if self.hero_select_failed:
                if hero not in default_heroes or manual:
                    self.client_socket.send(b'!select_hero_unavailable')
                return False

            # Selection succeeded
            if hero in default_heroes and not manual:
                self.client_socket.send(f'!select_default_hero_success {hero}'.encode())
                return True
            self.client_socket.send(b'!select_hero_success')
            return True

        except Exception as e:
            print(f'Error selecting hero: {e}')

    def game_found(self, objective, map_name):
        msg = f'!found_game'
        if objective != '':

            # Edge case - The only time the objective is read wrong is when the map is Numbani.
            # The OCR can't read Defend correctly over Numbani's background.
            # Safer to just tell the player that they're defending, even when it's not the case, so they have time to set up
            if map_name == 'Numbani':
                objective = "defending"

            msg += f' {objective}'

        if map_name != '':
            msg += f' {map_name}'

        self.client_socket.send(msg.encode())
        notification.notify(title='Overwatch Queue Notifier', message='Your match has been found!',
                            app_icon=favicon_path, timeout=5)

    def game_finished(self):
        self.scheduled_hero = None
        self.hero_select_failed = False

        if self.reminder:
            self.client_socket.send(b'!remind_user')
            self.reminder = False  # Reset

    def link_discord_user(self, username):
        try:
            message = f'!get_connection_authorization {username}'
            self.client_socket.send(message.encode())
        except Exception as e:
            print(f'Error - Could not connect discord user to server. {e}')

    def authorized_login(self, message):
        try:
            username = message.split(' ')[1]
            self.discord_id = message.split(' ')[2]
            self.main_app.get_client_ui().set_connected(username)
            print(f'Connected discord user {username} to server.')

            self.queue_watcher = QueueWatcher(self)
            queue_watcher_thread = Thread(target=self.init_queue_watcher)
            queue_watcher_thread.start()
        except Exception as e:
            print(f'Error connecting to server. Restart and try again please. {e}')

    def stop_queue_watcher(self):
        if self.queue_watcher is not None:
            self.queue_watcher.stop()

    def close_connection(self):
        self.socket_thread_running = False
        self.client_socket.close()

    def send_disconnect(self):
        if self.discord_id is not None and self.client_socket and not self.client_socket._closed:
            self.client_socket.send(f'!disconnect {self.discord_id}'.encode())
            self.discord_id = None
