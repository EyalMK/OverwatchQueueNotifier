import sys
import os
import time

import cv2
import numpy as np
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

heroes_coordinates_1920x1080 = {
    #  [x, y]
    # Tanks
    "D.Va": [250, 830],
    "Doomfist": [320, 830],
    "Junker Queen": [370, 830],
    "Orisa": [440, 830],
    "Ramattra": [500, 830],
    "Reinhardt": [570, 830],
    "Roadhog": [320, 890],
    "Sigma": [370, 890],
    "Winston": [440, 890],
    "Wrecking Ball": [500, 890],
    "Zarya": [570, 890],

    # Dps'
    "Ashe": [740, 830],
    "Bastion": [800, 830],
    "Cassidy": [860, 830],
    "Echo": [920, 830],
    "Genji": [990, 830],
    "Hanzo": [1060, 830],
    "Junkrat": [1120, 830],
    "Mei": [1180, 830],
    "Pharah": [1250, 830],
    "Reaper": [770, 890],
    "Sojourn": [830, 890],
    "Soldier: 76": [890, 890],
    "Sombra": [960, 890],
    "Symmetra": [1020, 890],
    "Torbjorn": [1090, 890],
    "Tracer": [1150, 890],
    "Widowmaker": [1220, 890],

    # Supports
    "Ana": [1410, 830],
    "Baptiste": [1480, 830],
    "Brigette": [1530, 830],
    "Illari": [1600, 830],
    "Kiriko": [1660, 830],
    "Lifeweaver": [1410, 890],
    "Lucio": [1480, 890],
    "Mercy": [1530, 890],
    "Moira": [1600, 890],
    "Zenyatta": [1660, 890]
}

region_resolution_options = {
    "queue_region_big_1920x1080": {
        "x": 750,
        "y": 0,
        "width": 425,
        "height": 139
    },

    "queue_region_small_1920x1080": {
        "x": 750,
        "y": 0,
        "width": 425,
        "height": 40
    },

    "queue_region_top_left_1920x1080": {
        "x": 100,
        "y": 20,
        "width": 200,
        "height": 40
    },

    "queue_pop_region_1920x1080": {
        "x": 770,
        "y": 0,
        "width": 375,
        "height": 100
    },

    "menu_region_1920x1080": {
        "x": 850,
        "y": 0,
        "width": 200,
        "height": 500
    },

    "full_menu_region_1920x1080": {
        "x": 870,
        "y": 150,
        "width": 320,
        "height": 800
    },

    "hero_change_button_region_1920x1080": {
        "x": 850,
        "y": 950,
        "width": 250,
        "height": 75
    },

    # Hero selection screen exclusive text
    "hero_select_details_region_1920x1080": {
        "x": 20,
        "y": 1000,
        "width": 400,
        "height": 40
    }
}


class QueueWatcher:
    found_game = False
    active_queue_phases = [False, False, False]
    # Phase 0: Find competitive text from screenshot of big region (big box at the beginning of the queue).
    # Phase 1: Find competitive text from screenshot of small region (minimized big box).
    # Phase 2: Find Game Found text from screenshot of queue pop box region.
    monitor_resolution = None  # (Width, Height)
    overwatch_client = None
    selected_hero = None

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

    def set_overwatch_active_window(self):
        try:
            win32gui.ShowWindow(self.overwatch_client, win32con.SW_SHOW)
            win32gui.SetForegroundWindow(self.overwatch_client)
        except Exception as e:
            print(f'Error setting Overwatch as active window. {e}')

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

    def get_resolution(self):
        home_dir = os.path.expanduser("~")
        config_path = os.path.join(home_dir, 'Documents', 'Overwatch', 'Settings', 'Settings_v0.ini')

        config = configparser.ConfigParser()
        config.read(config_path)

        return int(config['Render.13']['FullScreenWidth'].split('"')[1]), int(
            config['Render.13']['FullScreenHeight'].split('"')[1])

    def get_region_dimensions(self, region):
        res_w, res_h = self.get_resolution()
        return region_resolution_options[region + f'_{res_w}x{res_h}']

    def cancel_queue(self):
        if self.found_game:
            self.client_handler.cancel_queue_failure(1)  # Errno 1: In game.

        # Check if rectangle exists atop. If so, PyAutoGUI to hover over it for 0.5 seconds and then go down 100
        # height and press on cancel. Else, check if rectangle exists top left. If so, press Escape until we see "Menu"
        # and then go to "Leave Game and Queue"
        # Each check must be done 3 times at most,
        # after which, safe to assume not in queue, so we send the server "Not in queue".
        def capture_and_leave(x, y, width, height, attempt):
            if self.capture_region(x, y, width, height, "Competitive"):
                self.leave_queue(attempt)
                # Reset all phases
                self.active_queue_phases[0] = self.active_queue_phases[1] = self.active_queue_phases[2] = False

                return True
            return False

        def attempt_to_leave(attempt, region):
            reg = self.get_region_dimensions(region)
            if capture_and_leave(reg["x"],
                                 reg["y"],
                                 reg["width"],
                                 reg["height"],
                                 attempt):
                return True
            return False

        left_queue = False

        attempts = 0
        max_attempts = 6

        while attempts < max_attempts and not left_queue:
            attempts += 1

            if attempts < 3:
                left_queue = attempt_to_leave(1, "queue_region_big")
            elif attempts < 5:
                left_queue = attempt_to_leave(1, "queue_region_small")
            else:
                left_queue = attempt_to_leave(2, "queue_region_top_left")

            time.sleep(0.5)

        if not left_queue:
            self.client_handler.cancel_queue_failure(2)  # Errno 2: Not in queue.
        else:
            self.client_handler.cancel_queue_success()

    def move_mouse(self, x, y):
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

            self.move_mouse(x, y)

            # Wait for a second
            time.sleep(1)

            # Move the mouse to the cancel bar coordinates. Height only.
            self.move_mouse(x, 150)

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
                menu_region = self.get_region_dimensions("menu_region")
                while not self.capture_region(menu_region["x"],
                                              menu_region["y"],
                                              menu_region["width"],
                                              menu_region["height"],
                                              "Menu"):
                    pyautogui.press('esc')
                    time.sleep(0.5)

                # Menu found, press "Leave Game And Queue" and then "Yes". If in custom game, Menu has more options,
                # therefore these coordinates will press "Leave Queue" and then "Show Lobby" instead.
                x, y = 1077, 638

                self.move_mouse(x, y)

                # Wait for half a second
                time.sleep(0.5)

                # Left click.
                pyautogui.click()

                # Press "Yes"
                new_x, new_y = 1050, 600
                self.move_mouse(new_x, new_y)

                # Wait for half a second
                time.sleep(0.5)

                # Left click.
                pyautogui.click()

            elif self.monitor_resolution == (2560, 1440):
                pass

    def check_available_selection(self):
        # Take screenshot of region of the "Continue" Button.
        left, top, right, bottom = win32gui.GetWindowRect(self.overwatch_client)
        image = pyautogui.screenshot(region=(left, top, right - left, bottom - top))

        # Crop the region by the defined coordinates and save it.
        region = image.crop((875, 962, 875 + 170, 962 + 55))
        region.save(os.getcwd() + 'con-bt-scrn.png')

        # Load the image using OpenCV
        image = cv2.imread(os.getcwd() + 'con-bt-scrn.png')

        # Convert the image to the HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Define the range for orange color in HSV
        lower_orange = np.array([5, 50, 50])
        upper_orange = np.array([15, 255, 255])

        # Create a mask for the orange color
        mask = cv2.inRange(hsv, lower_orange, upper_orange)

        # Calculate the percentage of orange pixels
        total_pixels = image.shape[0] * image.shape[1]
        orange_pixels = np.sum(mask > 0)
        percentage_orange = (orange_pixels / total_pixels) * 100

        # If more than a certain percentage of the image is orange,
        # consider it the pressable button
        return percentage_orange > 50  # You can adjust this threshold as needed

    def select_hero(self, hero):
        self.set_overwatch_active_window()
        if self.found_game:
            # Enter hero select screen, if not there.
            hero_details_region = self.get_region_dimensions("hero_select_details_region")
            if not self.capture_region(hero_details_region["x"],
                                       hero_details_region["y"],
                                       hero_details_region["width"],
                                       hero_details_region["height"],
                                       "Hero Details"):
                pyautogui.press('h')
                while not self.capture_region(hero_details_region["x"],
                                              hero_details_region["y"],
                                              hero_details_region["width"],
                                              hero_details_region["height"],
                                              "Hero Details"):
                    pyautogui.press('esc')
                    pyautogui.press('h')

            if self.selected_hero is not None:
                hero_change_button_region = self.get_region_dimensions("hero_change_button_region")
                # Now we check if we've already picked a hero (Change Hero button)
                if self.capture_region(hero_change_button_region["x"],
                                       hero_change_button_region["y"],
                                       hero_change_button_region["width"],
                                       hero_change_button_region["height"],
                                       "Change Hero"):
                    # Now select Change Hero button
                    self.move_mouse(950, 970)
                    time.sleep(0.3)
                    pyautogui.click()
                    # Now we're in the hero selection screen. Continue outside the function to select the hero.
                # Otherwise, we haven't picked a hero, the button is "Ready" or "Continue", so we're already in the
                # hero selection screen.
            coordinates = heroes_coordinates_1920x1080[hero]
            self.move_mouse(coordinates[0], coordinates[1])
            time.sleep(0.3)
            pyautogui.click()
            # Now select Ready/Continue button
            self.move_mouse(950, 970)
            # Check if "Continue" button is greyed out.
            if self.check_available_selection():
                pyautogui.click()
            else:
                self.selected_hero = None
                self.client_handler.set_select_hero_failure()
        else:  # Not in a game. Schedule for it to be selected later through run_queue_watcher().
            self.selected_hero = hero
            self.client_handler.set_select_hero_scheduled()

    def check_text(self, image, expected_text):
        # Returns True if expected_text is found in the provided image.
        gray_image = image.convert('L')
        extracted_text = pytesseract.image_to_string(gray_image)
        return expected_text.lower() in extracted_text.lower()

    def capture_region(self, x, y, width, height, expected_test):
        left, top, right, bottom = win32gui.GetWindowRect(self.overwatch_client)
        image = pyautogui.screenshot(region=(left, top, right - left, bottom - top))

        # Crop the region by the defined coordinates
        region = image.crop((x, y, x + width, y + height))

        return self.check_text(region, expected_test)

    def capture_and_set_phase(self, region, phase, condition="Competitive"):
        if self.capture_region(region["x"], region["y"], region["width"], region["height"], condition):
            self.active_queue_phases[phase] = True
            if phase == 1: self.active_queue_phases[0] = True  # If phase 1 is active, then set phase 0 to True as well.

    def detect_current_phase(self):
        region_to_capture = self.get_region_dimensions("queue_region_big")
        self.capture_and_set_phase(region_to_capture, 0)

        region_to_capture = self.get_region_dimensions("queue_region_small")
        self.capture_and_set_phase(region_to_capture, 1)

        region_to_capture = self.get_region_dimensions("queue_region_top_left")
        self.capture_and_set_phase(region_to_capture, 1)

    def run_queue_watcher(self):
        while True:
            # First detect which phase the user is in (assuming the user queued before launching the client).
            self.detect_current_phase()
            while not self.found_game:
                region_to_capture = self.get_region_dimensions("queue_region_big")
                while not self.active_queue_phases[0]:
                    print(f'In Phase 1')
                    self.capture_and_set_phase(region_to_capture, 0)
                    time.sleep(1)

                region_to_capture = self.get_region_dimensions("queue_region_small")
                while not self.active_queue_phases[1] and self.active_queue_phases[0]:
                    print(f'In Phase 2')
                    self.capture_and_set_phase(region_to_capture, 1)
                    time.sleep(1)

                region_to_capture = self.get_region_dimensions("queue_pop_region")
                while not self.active_queue_phases[2] and self.active_queue_phases[1]:
                    print(f'In Phase 3')
                    self.capture_and_set_phase(region_to_capture, 2, condition="Game Found!")
                    # Needs to be faster than other phases due to the shorter time window of the game found box.
                    time.sleep(0.5)

                # If the phases haven't been reset, and we finished all loops.
                if self.active_queue_phases[2]:
                    print(f'Found game...')
                    self.found_game = True

            # Game Found
            self.client_handler.game_found(self.selected_hero)
            while self.found_game:
                print(f'Checking if game is over...')
                # Take screenshots and if we find 1) POTG, 2) Menu screen, 3) Stats screen after potg:
                self.active_queue_phases[0] = self.active_queue_phases[1] = self.active_queue_phases[2] = False
                self.found_game = False
                time.sleep(5)
