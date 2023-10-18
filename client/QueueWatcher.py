import win32gui
import configparser
import os
from threading import Thread
import tkinter as tk


class QueueWatcher:
    found_game = False
    monitor_resolution = None  # (Width, Height)
    overwatch_client = None

    def __init__(self, client_handler):
        self.client_handler = client_handler
        # self.run()

    def run(self):
        # Find main monitor resolution.
        self.get_monitor_resolution()

        # While Overwatch window is not found, keep looking before proceeding.
        self.find_overwatch()

        # When Overwatch window is found, make sure the resolution matches the main monitor resolution.
        if not self.monitor_resolution == self.get_resolution():
            pass  # Send error message through Discord and exit program.

        # Call self.queue_watcher() method, which starts taking screenshots of Overwatch window, and checking if at
        # the top middle of the screen, there is a red bar containing the words "Competitive" and a timer
        queue_watcher_thread = Thread(target=self.run_queue_watcher)
        queue_watcher_thread.start()

    ''' 
        TESTED
    '''
    def get_monitor_resolution(self):
        # Gets main monitor resolution by running Tkinter (which launches on the main monitor) and utilizing library
        # methods.
        root = tk.Tk()
        height = root.winfo_screenheight()
        width = root.winfo_screenwidth()
        root.destroy()

        self.monitor_resolution = width, height

    ''' 
            TESTED
    '''
    def find_overwatch(self):
        # Finds Overwatch window.
        while True:
            hwnd = win32gui.FindWindow(None, 'Overwatch')
            if hwnd != 0:
                return hwnd

    ''' 
            TESTED
    '''
    def get_resolution(self):
        home_dir = os.path.expanduser("~")
        config_path = os.path.join(home_dir, 'Documents', 'Overwatch', 'Settings', 'Settings_v0.ini')

        config = configparser.ConfigParser()
        config.read(config_path)

        return int(config['Render.13']['FullScreenWidth'].split('"')[1]), int(config['Render.13']['FullScreenHeight'].split('"')[1])


    def cancel_queue(self):
        if self.found_game:
            pass  # Send message that a game has already been found.
        # PyAutoGUI to cancel queue.
        pass

    def select_hero(self, hero):
        pass
        # Check the hero's coordinates, double click on them. If icon is greyed out, self.client_handler.set_select_hero_failure()

    def run_queue_watcher(self):

        resolution = win32gui.GetWindowRect(self.overwatch_client)
        min_x, min_y, max_x, max_y = resolution
        width = max_x - min_x
        height = max_y - min_y
        center_x = (min_x + max_x) // 2

        while not self.found_game:
            # Take screenshots and find square OR rectangle in top middle/top left.
            # If found, trigger event condition "event_screen_change"
            # event_screen_change - Look for 1) Lobby screen, 2) Competitive title top left, 3) Hero selection screen.
            # self.found_game = True, self.client_handler.game_found()
            pass

        while self.found_game:
            # Look for 1) Menu screen, 2) Queue screen
            # When found, self.found_game = False, self.client_handler.game_finished()
            pass


if __name__ == '__main__':
    test = QueueWatcher(None)