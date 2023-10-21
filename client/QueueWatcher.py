import sys
import os
import time
import win32con
import win32gui
import configparser
import pytesseract
import pyautogui
from threading import Thread
import tkinter as tk

if getattr(sys, 'frozen', False):
    _path = os.path.join(sys._MEIPASS, './Tesseract-OCR/tesseract.exe')
    print(_path)
    pytesseract.pytesseract.tesseract_cmd =_path


queue_region_big_1920x1080 = {
    "x": 750,
    "y": 0,
    "width": 425,
    "height": 139
}

queue_region_small_1920x1080 = {
    "x": 750,
    "y": 0,
    "width": 425,
    "height": 40
}

queue_pop_region_1920x1080 = {
    "x": 770,
    "y": 0,
    "width": 375,
    "height": 100
}

heroes_coordinates_1920x1080 = {
    "D.Va": [555, 555]  # [x, y]
}


class QueueWatcher:
    found_game = False
    phase1 = False  # Find competitive text found from screenshot of big region (big box at the beginning of the queue).
    phase2 = False  # Find competitive text found from screenshot of small region (minimized big box).
    phase3 = False  # Find competitive text found from screenshot of hero selection screen.
    monitor_resolution = None  # (Width, Height)
    overwatch_client = None
    queue_cancelled = False  # Actively see if the queue is cancelled and if it is, we reset all phases.
    q_cancel_phase_1 = False

    # todo: check if already in queue and if so, self.phase1 = self.phase2 = True

    def __init__(self, client_handler):
        self.client_handler = client_handler
        self.run()

    def run(self):
        # Find main monitor resolution.
        self.get_monitor_resolution()

        # While Overwatch window is not found, keep looking before proceeding.
        self.overwatch_client = self.find_overwatch()

        # When Overwatch window is found, make sure the resolution matches the main monitor resolution.
        if self.monitor_resolution != self.get_resolution():
            pass  # Send error message through Discord and exit program.

        # Bring Overwatch to the foreground (active window).
        self.set_overwatch_active_window()

        # Call self.queue_watcher() method, which starts taking screenshots of Overwatch window, and checking if at
        # the top middle of the screen, there is a red bar containing the words "Competitive" and a timer
        queue_watcher_thread = Thread(target=self.run_queue_watcher)
        queue_watcher_thread.start()

    ''' 
        TESTED
    '''

    def set_overwatch_active_window(self):
        win32gui.ShowWindow(self.overwatch_client, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(self.overwatch_client)

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
                print(f'Found overwatch...')
                return hwnd
            print(f'Looking for Overwatch...')
            time.sleep(0.5)  # Look every half a second... Takes a lot of time to launch and connect to Overwatch on
            # average anyway.

    ''' 
        TESTED
    '''

    def get_resolution(self):
        home_dir = os.path.expanduser("~")
        config_path = os.path.join(home_dir, 'Documents', 'Overwatch', 'Settings', 'Settings_v0.ini')

        config = configparser.ConfigParser()
        config.read(config_path)

        return int(config['Render.13']['FullScreenWidth'].split('"')[1]), int(
            config['Render.13']['FullScreenHeight'].split('"')[1])

    def cancel_queue(self):
        if self.found_game:
            pass  # Send message that a game has already been found.
        # PyAutoGUI to cancel queue.
        pass

    def select_hero(self, hero):
        pass
        # Check the hero's coordinates, double click on them. If icon is greyed out, self.client_handler.set_select_hero_failure()

    ''' 
        TESTED
    '''

    def check_competitive(self, image, expected_text):
        # Returns True if expected_text is found in the provided image.
        gray_image = image.convert('L')
        extracted_text = pytesseract.image_to_string(gray_image)

        print(extracted_text)
        # Hackfix, current modifications to captured region allow Tesseract OCR to read "pampetitive" instead of "competitive"
        return 'pampetitive' in extracted_text.lower() or expected_text.lower() in extracted_text.lower()

    ''' 
        TESTED
    '''

    def capture_region(self, x, y, width, height, expected_test):
        left, top, right, bottom = win32gui.GetWindowRect(self.overwatch_client)
        image = pyautogui.screenshot(region=(left, top, right - left, bottom - top))

        # Crop the region by the defined coordinates
        region = image.crop((x, y, x + width, y + height))

        return self.check_competitive(region, expected_test)

    ''' 
        TESTED UP TO PHASE 3 (INCLUDING)
    '''

    def run_queue_watcher(self):
        while not self.found_game:
            while not self.phase1:
                # Take screenshots and save them to image_path variable.
                print(f'In Phase 1')
                if self.monitor_resolution == (1920, 1080):
                    if self.capture_region(queue_region_big_1920x1080["x"], queue_region_big_1920x1080["y"],
                                           queue_region_big_1920x1080["width"], queue_region_big_1920x1080["height"],
                                           "Competitive"):
                        self.phase1 = True
                elif self.monitor_resolution == (2560, 1440):
                    pass
                time.sleep(1)

            while not self.phase2:
                # Take screenshots and save them to image_path variable.
                print(f'In Phase 2')
                if self.monitor_resolution == (1920, 1080):
                    if self.capture_region(queue_region_small_1920x1080["x"], queue_region_small_1920x1080["y"],
                                           queue_region_small_1920x1080["width"],
                                           queue_region_small_1920x1080["height"], "Competitive"):
                        self.phase2 = True
                elif self.monitor_resolution == (2560, 1440):
                    pass
                time.sleep(1)

            while not self.phase3:
                # todo: Find a way to detect if queue has been cancelled. Maybe check if rectangle is hovered (big box exists), or if the rectangle is in top
                # left, where it is checked every 2 seconds and only if it hasn't been found in 3 tries, then self.queue_cancelled = True
                if self.queue_cancelled:
                    self.phase1 = self.phase2 = self.phase3 = self.found_game = self.queue_cancelled = False
                    break
                # Take screenshots and save them to image_path variable.
                print(f'In Phase 3')
                if self.monitor_resolution == (1920, 1080):
                    if self.capture_region(queue_pop_region_1920x1080["x"], queue_pop_region_1920x1080["y"],
                                           queue_pop_region_1920x1080["width"],
                                           queue_pop_region_1920x1080["height"], "Game Found!"):
                        self.phase3 = True
                elif self.monitor_resolution == (2560, 1440):
                    pass
                time.sleep(
                    0.5)  # Needs to be faster than other phases due to the shorter time window of the game found box.

            print(f'Found game...')
            self.found_game = True
            self.client_handler.game_found()
            while self.found_game:
                print(f'Checking if game is over...')
                # Take screenshots and if we find 1) POTG, 2) Menu screen, 3) Stats screen after potg:
                self.phase1 = self.phase2 = self.phase3 = self.found_game = False
                time.sleep(5)
