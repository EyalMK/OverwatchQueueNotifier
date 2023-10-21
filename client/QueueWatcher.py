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

_path = r'C:/Program Files/Tesseract-OCR/tesseract.exe'  # Dev env default path
if getattr(sys, 'frozen', False):
    _path = os.path.join(sys._MEIPASS, './Tesseract-OCR/tesseract.exe')  # Client path

pytesseract.pytesseract.tesseract_cmd = _path

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

queue_region_small_top_left_1920x1080 = {
    "x": 100,
    "y": 20,
    "width": 200,
    "height": 40
}

queue_pop_region_1920x1080 = {
    "x": 770,
    "y": 0,
    "width": 375,
    "height": 100
}

menu_region_1920x1080 = {
    "x": 850,
    "y": 0,
    "width": 200,
    "height": 500
}

full_menu_region_1920x1080 = {
    "x": 870,
    "y": 150,
    "width": 320,
    "height": 800
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
        win32gui.ShowWindow(self.overwatch_client, win32con.SW_SHOW)
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
        # todo: Refactor this disgusting non-modular code.
        if self.found_game:
            self.client_handler.cancel_queue_failure(1)  # Errno 1: In game.

        # Reset all phases
        self.phase1 = self.phase2 = self.phase3 = False

        # Check if rectangle exists atop. If so, PyAutoGUI to hover over it for 0.5 seconds and then go down 100
        # height and press on cancel. Else, check if rectangle exists top left. If so, press Escape until we see "Menu"
        # and then go to "Leave Game and Queue"
        # Each check must be done 3 times at most,
        # after which, safe to assume not in queue, so we send the server "Not in queue".
        attempts = 0
        left_queue = False

        # First loop to check if, just entered queue. (Big box).
        while attempts < 2 and not left_queue:
            attempts += 1
            if self.monitor_resolution == (1920, 1080):
                if self.capture_region(queue_region_big_1920x1080["x"], queue_region_big_1920x1080["y"],
                                       queue_region_big_1920x1080["width"], queue_region_big_1920x1080["height"],
                                       "Competitive"):
                    self.leave_queue(1)  # Phase 1
                    left_queue = True
            elif self.monitor_resolution == (2560, 1440):
                pass
            time.sleep(0.5)

        # If we haven't left queue, we'll enter the second loop. (Minimized box - rectangle).
        while attempts < 4 and not left_queue:
            attempts += 1
            if self.monitor_resolution == (1920, 1080):
                if self.capture_region(queue_region_small_1920x1080["x"], queue_region_small_1920x1080["y"],
                                       queue_region_small_1920x1080["width"],
                                       queue_region_small_1920x1080["height"], "Competitive"):
                    self.leave_queue(1)  # Act 1 - Edge case of previous scan. Same PyAutoGUI algorithm.
                    left_queue = True
            elif self.monitor_resolution == (2560, 1440):
                pass
            time.sleep(0.5)

        # If we haven't left queue, we'll look for the top left rectangle.
        while attempts < 6 and not left_queue:
            attempts += 1
            if self.monitor_resolution == (1920, 1080):
                if self.capture_region(queue_region_small_top_left_1920x1080["x"],
                                       queue_region_small_top_left_1920x1080["y"],
                                       queue_region_small_top_left_1920x1080["width"],
                                       queue_region_small_top_left_1920x1080["height"], "Competitive"):
                    self.leave_queue(2)  # Act 2
                    left_queue = True
            elif self.monitor_resolution == (2560, 1440):
                pass
            time.sleep(0.5)

        if not left_queue:
            self.client_handler.cancel_queue_failure(2)  # Errno 2: Not in queue.
        else:
            self.client_handler.cancel_queue_success()

    def move_mouse_and_click(self, x, y):
        # Calculate the actual coordinates based on the screen resolution
        actual_x = int((x / 1920) * self.monitor_resolution[0])
        actual_y = int((y / 1080) * self.monitor_resolution[1])

        # Move the mouse to the specified coordinates
        pyautogui.moveTo(actual_x, actual_y, duration=0.3)


    def leave_queue(self, action):
        if action == 1:
            # Hover over rectangle for 0.5 sec and then press "Cancel"
            # Set the coordinates to hover over
            x, y = 900, 0

            self.move_mouse_and_click(x, y)

            # Wait for a second
            time.sleep(1)

            # Move the mouse to the cancel bar coordinates. Height only.
            self.move_mouse_and_click(x, 150)

            # Wait a bit.
            time.sleep(0.3)

            # Left click.
            pyautogui.click()

        elif action == 2:
            if self.monitor_resolution == (1920, 1080):
                # Set Overwatch active window.
                self.set_overwatch_active_window()
                time.sleep(0.2)

                # Keep pressing Escape until check menu_region_1920x1080 passes
                while not self.capture_region(menu_region_1920x1080["x"], menu_region_1920x1080["y"],
                                           menu_region_1920x1080["width"],
                                           menu_region_1920x1080["height"], "Menu"):
                    pyautogui.press('esc')
                    time.sleep(1)

                # Menu found, press "Leave Game And Queue" and then "Yes". If in custom game, Menu has more options,
                # therefore these coordinates will press "Leave Queue" and then "Show Lobby" instead.
                x, y = 1077, 638

                self.move_mouse_and_click(x, y)

                # Wait for half a second
                time.sleep(0.5)

                # Left click.
                pyautogui.click()

                # Press "Yes"
                new_x, new_y = 1050, 600
                self.move_mouse_and_click(new_x, new_y)

                # Wait for half a second
                time.sleep(0.5)

                # Left click.
                pyautogui.click()

            elif self.monitor_resolution == (2560, 1440):
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
        # todo: Refactor this disgusting non-modular code.
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

            while not self.phase2 and self.phase1:
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

            while not self.phase3 and self.phase2:
                # Take screenshots and save them to image_path variable.
                print(f'In Phase 3')
                if self.monitor_resolution == (1920, 1080):
                    if self.capture_region(queue_pop_region_1920x1080["x"], queue_pop_region_1920x1080["y"],
                                           queue_pop_region_1920x1080["width"],
                                           queue_pop_region_1920x1080["height"], "Game Found!"):
                        self.phase3 = True
                elif self.monitor_resolution == (2560, 1440):
                    pass
                # Needs to be faster than other phases due to the shorter time window of the game found box.
                time.sleep(0.5)

            # If the phases haven't been reset, and we finished all loops.
            if self.phase3:
                print(f'Found game...')
                self.found_game = True
                self.client_handler.game_found()
                while self.found_game:
                    print(f'Checking if game is over...')
                    # Take screenshots and if we find 1) POTG, 2) Menu screen, 3) Stats screen after potg:
                    self.phase1 = self.phase2 = self.phase3 = self.found_game = False
                    time.sleep(5)
