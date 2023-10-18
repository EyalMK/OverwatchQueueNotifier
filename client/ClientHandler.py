import time
import psutil
from threading import Thread
from QueueWatcher import QueueWatcher

# Heroes
tanks = {
    "D.Va": ["D.Va", "d.va", "dva", "Dva"],
    "Doomfist": ["Doom", "doom", "DF", "df", "doomfist", "Doomfist"],
    "Junker Queen": ["Junker Queen", "JQ", "Queen", "queen", "junker", "jq"],
    "Orisa": ["orisa", "Orisa", "horse"],
    "Ramattra": ["Ramattra", "Ram", "ram"],
    "Reinhardt": ["Reinhardt", "Rein", "rein"],
    "Roadhog": ["Roadhog", "road", "hog", "Hog"],
    "Sigma": ["Sigma", "sigma", "sig", "Sig"],
    "Winston": ["Winston", "winston", "monkey", "winton", "Winton"],
    "Wrecking Ball": ["Wrecking Ball", "wrecking ball", "Ball", "ball", "hamster", "Hamster"],
    "Zarya": ["Zarya", "zarya"]
}

dps = {
    "Ashe": ["Ashe", "ashe"],
    "Bastion": ["Bastion", "bastion", "bast", "Bast"],
    "Cassidy": ["Cassidy", "cassidy", "Cree", "cree"],
    "Echo": ["Echo", "echo"],
    "Genji": ["Genji", "genji", "genju"],
    "Hanzo": ["Hanzo", "hanzo"],
    "Junkrat": ["Junkrat", "junkrat", "Junk", "junk"],
    "Mei": ["Mei", "mei", "the devil"],
    "Pharah": ["Pharah", "pharah", "phara", "Phara"],
    "Reaper": ["Reaper", "reaper", "reap"],
    "Sojourn": ["Sojourn", "sojourn", "Soj", "soj"],
    "Soldier: 76": ["Soldier: 76", "soldier: 76", "Soldier", "soldier", "sold", "Sold"],
    "Sombra": ["Sombra", "sombra", "somb"],
    "Symmetra": ["Symmetra", "symmetra", "sym", "Symetra", "symetra"],
    "Torbjorn": ["Torbjorn", "torbjorn", "Torb", "torb"],
    "Tracer": ["Tracer", "tracer", "tr"],
    "Widowmaker": ["Widowmaker", "widowmaker", "Widow", "widow"]
}

supports = {
    "Ana": ["Ana", "ana"],
    "Baptiste": ["Baptiste", "baptiste", "bap", "Bap"],
    "Brigette": ["Brigette", "brigette", "brig", "Brig"],
    "Illari": ["Illari", "illari"],
    "Kiriko": ["Kiriko", "kiriko", "Kiri", "kiri"],
    "Lifeweaver": ["Lifeweaver", "lifeweaver", "life", "Life", "Weaver", "weaver", "wifeleaver", "Wifeleaver"],
    "Lucio": ["Lucio", "lucio"],
    "Mercy": ["Mercy", "mercy"],
    "Moira": ["Moira", "moira"],
    "Zenyatta": ["Zenyatta", "zenyatta", "Zen", "zen"]
}

heroes = [item for hero in [tanks, dps, supports] for values in hero.values() for item in values]

class ClientHandler:
    reminder = False
    connected_as = None  # Discord user
    queue_watcher = None
    select_hero_failure = False

    def __init__(self, socket, main_thread):
        self.client_socket = socket
        self.main_thread = main_thread
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
                elif message == 'test_cancel_queue':
                    self.cancel_queue()
                elif message == 'test_exit':
                    self.exit_program()
                elif message == 'exit_game':
                    self.exit_game()
                elif message == '$user_id_not_found' or message == '$user_already_logged_in':  # Error messages from
                    # server.
                    self.exit_program()

                if message.startswith('!authorized_login'):  # Command message from server.
                    self.authorized_login(message)
                elif message.startswith('!test_select_hero'):
                    self.select_hero(message)
            except Exception as e:
                print(f'Waiting for a message... {e}')
                time.sleep(3)

    def run(self):
        # Create a thread to manage socket communication.
        socket_listen_thread = Thread(target=self.receive_messages, args=())
        socket_listen_thread.start()

        # Create Queue Watcher.
        self.queue_watcher = QueueWatcher(self)

    def activate_reminder(self):
        self.reminder = True

    def deactivate_reminder(self):
        self.reminder = False

    def get_reminder(self):
        return self.reminder

    def cancel_queue(self):
        self.queue_watcher.cancel_queue()

    def set_select_hero_failure(self):
        self.select_hero_failure = True

    def select_hero(self, message):
        try:
            self.select_hero_failure = False  # Reset in-case the user selected another hero after a failed attempt.
            parts = message.split(' ')[1::]
            hero = " ".join(parts)
            if hero in heroes:
                self.queue_watcher.select_hero(hero)
                if not self.select_hero_failure:
                    self.client_socket.send(b'!select_hero_success')
            else:
                self.client_socket.send(b'!select_hero_invalid_error')
        except Exception as e:
            print(f'Invalid input.')

    def game_found(self):
        self.client_socket.send(b'!found_game')

    def game_finished(self):
        if self.reminder:
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
            self.main_thread.switch_to_main_window()
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