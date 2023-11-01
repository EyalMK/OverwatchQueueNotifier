import os
import sys
import time
import tkinter as tk
from ctypes import windll
from threading import Thread

import cv2
import numpy as np
import pyautogui
import pytesseract
import win32con
import win32gui
import win32ui
from PIL import Image

_path = r'C:/Program Files/Tesseract-OCR/tesseract.exe'  # Dev env default path
if getattr(sys, 'frozen', False):
    _path = os.path.join(sys._MEIPASS, './Tesseract-OCR/tesseract.exe')  # Client path

pytesseract.pytesseract.tesseract_cmd = _path

heroes_coordinates_1920x1080 = {
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

comp_cards_expected_text = "competitive play competitive play\nrole queue open queue\n\nchoose a role before you play " \
                           "any role.\nplay."
quick_cards_expected_text = "quick play quick play\nrole queue open queue\n\nchoose a role before you play any " \
                            "role.\nplay."

region_resolution_options = {
    "queue_region_big_1920x1080": {
        "x": 750,
        "y": 0,
        "width": 425,
        "height": 139
    },
    "queue_region_big_2560x1440": {
        "x": 998,
        "y": 0,
        "width": 566,
        "height": 186
    },

    "queue_region_small_1920x1080": {
        "x": 750,
        "y": 0,
        "width": 425,
        "height": 40
    },
    "queue_region_small_2560x1440": {
        "x": 998,
        "y": 0,
        "width": 566,
        "height": 53
    },
    "queue_region_top_left_1920x1080": {
        "x": 100,
        "y": 20,
        "width": 200,
        "height": 40
    },
    "queue_region_top_left_2560x1440": {
        "x": 133.33,
        "y": 26.67,
        "width": 266.67,
        "height": 53.33
    },
    "queue_pop_region_1920x1080": {
        "x": 770,
        "y": 0,
        "width": 375,
        "height": 100
    },
    "queue_pop_region_2560x1440": {
        "x": 1024,
        "y": 0,
        "width": 500,
        "height": 133.33
    },
    "menu_region_1920x1080": {
        "x": 850,
        "y": 0,
        "width": 200,
        "height": 500
    },
    "menu_region_2560x1440": {
        "x": 1133.33,
        "y": 0,
        "width": 266.67,
        "height": 666.67
    },
    "full_menu_region_1920x1080": {
        "x": 870,
        "y": 150,
        "width": 320,
        "height": 800
    },
    "full_menu_region_2560x1440": {
        "x": 1168,
        "y": 200,
        "width": 373.33,
        "height": 1066.67
    },
    "hero_change_button_region_1920x1080": {
        "x": 850,
        "y": 950,
        "width": 250,
        "height": 75
    },
    "hero_change_button_region_2560x1440": {
        "x": 1133.33,
        "y": 1066.67,
        "width": 333.33,
        "height": 100
    },
    "hero_select_details_region_1920x1080": {
        "x": 20,
        "y": 1000,
        "width": 400,
        "height": 40
    },
    "hero_select_details_region_2560x1440": {
        "x": 30.67,
        "y": 1133.33,
        "width": 533.33,
        "height": 53.33
    },
    "enter_game_region_1920x1080": {
        "x": 780,
        "y": 505,
        "width": 320,
        "height": 50
    },
    "enter_game_region_2560x1440": {
        "x": 936.67,
        "y": 606.67,
        "width": 426.67,
        "height": 66.67
    },
    "queue_cards_region_1920x1080": {
        "x": 500,
        "y": 557,
        "width": 600,
        "height": 115
    },
    "queue_cards_region_2560x1440": {
        "x": 833.33,
        "y": 834.67,
        "width": 1000,
        "height": 191.67
    },
    "potm_title_region_1920x1080": {
        "x": 40,
        "y": 20,
        "width": 280,
        "height": 65
    },
    "potm_title_region_2560x1440": {
        "x": 53.33,
        "y": 26.67,
        "width": 373.33,
        "height": 88.89
    },
    "progression_screen_title_region_1920x1080": {
        "x": 1540,
        "y": 100,
        "width": 250,
        "height": 25
    },
    "progression_screen_title_region_2560x1440": {
        "x": 1920,
        "y": 133.33,
        "width": 333.33,
        "height": 37.04
    },
    "comp_progress_cards_region_1920x1080": {
        "x": 700,
        "y": 150,
        "width": 550,
        "height": 75
    },
    "comp_progress_cards_region_2560x1440": {
        "x": 853.33,
        "y": 300,
        "width": 733.33,
        "height": 111.11
    }
}


def find_overwatch():
    # Finds Overwatch window.
    while True:
        hwnd = win32gui.FindWindow(None, 'Overwatch')
        if hwnd != 0:
            print(f'Found overwatch...')
            return hwnd
        print(f'Looking for Overwatch...')
        time.sleep(1)


def check_text(image, expected_text, check_all_types):
    # Returns True if expected_text is found in the provided image.
    gray_image = image.convert('L')
    extracted_text = pytesseract.image_to_string(gray_image)

    # If we requested to check all type of matches, we opt for this block check.
    if check_all_types:
        formatted_text = extracted_text.lower()
        result = "Quick Play".lower() in formatted_text or "Competitive".lower() in formatted_text
        return result

    return expected_text.lower() in extracted_text.lower()


class QueueWatcher:
    found_game = False
    # Phase 0: Find Game Found text from screenshot of queue pop box region.
    # Phase 1: Find Entering Game text from screenshot of entering game box region. (To avoid false queues)
    active_queue_phases = [False, False]
    monitor_resolution = None  # (Width, Height)
    overwatch_resolution = None  # (Width, Height)
    overwatch_client = None
    selected_hero = None

    def __init__(self, client_handler):
        self.client_handler = client_handler
        self.run()

    def run(self):
        # Find main monitor resolution.
        self.get_monitor_resolution()

        # While Overwatch window is not found, keep looking before proceeding.
        self.overwatch_client = find_overwatch()

        # When Overwatch window is found, make sure the resolution matches the main monitor resolution.
        self.get_resolution()
        if self.monitor_resolution != self.overwatch_resolution:
            print(f'Terminating program... Resolutions are not matching.')
            self.client_handler.resolutions_not_matching()
            self.client_handler.exit_program()

        # Bring Overwatch to the foreground (active window).
        self.set_overwatch_active_window()

        # Call self.queue_watcher() method, which starts taking screenshots of Overwatch window, and checking if at
        # the top middle of the screen, there is a red bar containing the words "Competitive" and a timer
        queue_watcher_thread = Thread(target=self.run_queue_watcher)
        queue_watcher_thread.start()

    def set_overwatch_active_window(self):
        try:
            if self.overwatch_client is not None:
                win32gui.ShowWindow(self.overwatch_client, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(self.overwatch_client)
            else:
                print(f'Could not set Overwatch as active window because it was not found.')
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

    def get_resolution(self):
        if self.overwatch_client is not None:
            self.set_overwatch_active_window()
            rect = win32gui.GetClientRect(self.overwatch_client)
            self.overwatch_resolution = (rect[2] - rect[0], rect[3] - rect[1])

    def get_region_dimensions(self, region):
        return region_resolution_options[region + f'_{self.overwatch_resolution[0]}x{self.overwatch_resolution[1]}']

    def cancel_queue(self):
        if self.found_game:
            self.client_handler.cancel_queue_failure(1)  # Errno 1: In game.
            return

        # Check if rectangle exists atop. If so, PyAutoGUI to hover over it for 0.5 seconds and then go down 100
        # height and press on cancel. Else, check if rectangle exists top left. If so, press Escape until we see "Menu"
        # and then go to "Leave Game and Queue"
        # Each check must be done 3 times at most,
        # after which, safe to assume not in queue, so we send the server "Not in queue".
        def capture_and_leave(x, y, width, height, attempt):
            if self.capture_region(x, y, width, height, "Competitive"):
                self.leave_queue(attempt)
                # Reset all phases
                self.active_queue_phases[0] = self.active_queue_phases[1] = False

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
        self.set_overwatch_active_window()
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

    def check_available_selection(self):
        # Take screenshot of region of the "Continue"/"Ready" Button.
        if self.overwatch_client is not None:
            left, top, right, bottom = win32gui.GetWindowRect(self.overwatch_client)
            image = pyautogui.screenshot(region=(left, top, right - left, bottom - top))

            # Crop the region by the defined coordinates and save it.
            # todo: Get x,y,width,height for 2560x1440 and send appropriate coordinates.
            region = image.crop((875, 962, 875 + 170, 962 + 55))
            region.save(os.getcwd() + '\\con-bt-scrn.png')

            # Load the image using OpenCV
            image = cv2.imread(os.getcwd() + '\\con-bt-scrn.png')

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
            # consider it an available button
            return percentage_orange > 50  # 50 Threshold was deemed appropriate, considering some backgrounds are
            # orange and the button is actually transparent...
        return False  # Overwatch isn't running...

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
                self.client_handler.reset_select_hero_scheduled()
                self.client_handler.set_select_hero_failure()
                self.selected_hero = None
        else:  # Not in a game. Schedule for it to be selected later through run_queue_watcher().
            self.selected_hero = hero
            self.client_handler.set_select_hero_scheduled()

    def capture_region(self, x, y, width, height, expected_text, check_all_types=False):
        if self.overwatch_client:
            left, top, right, bottom = win32gui.GetWindowRect(self.overwatch_client)
            image = pyautogui.screenshot(region=(left, top, right - left, bottom - top))

            # Crop the region by the defined coordinates
            region = image.crop((x, y, x + width, y + height))

            return check_text(region, expected_text, check_all_types)
        return False  # Overwatch isn't running...

    # We use this only for queue detection, since it's fairly costly when used frequently.
    # This takes a screenshot of a minimized window and recreates it (with a bitmap).
    def capture_region_bitmap(self, x, y, width, height, expected_text, check_all_types=False):
        if self.overwatch_client:
            # Get the window dimensions
            left, top, right, bottom = win32gui.GetWindowRect(self.overwatch_client)

            # Create a device context
            hdesktop = win32gui.GetDesktopWindow()
            desktop_dc = win32gui.GetWindowDC(hdesktop)
            img_dc = win32ui.CreateDCFromHandle(desktop_dc)
            mem_dc = img_dc.CreateCompatibleDC()

            # Create a bitmap to save the screenshot
            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(img_dc, right - left, bottom - top)
            mem_dc.SelectObject(bmp)

            # Capture the window content
            result = windll.user32.PrintWindow(self.overwatch_client, mem_dc.GetSafeHdc(), 3)
            if result == 0:
                return False  # Function failed.

            # Convert the bitmap to a PIL image
            bmpinfo = bmp.GetInfo()
            img = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmp.GetBitmapBits(True),
                'raw',
                'BGRX',
                0,
                1
            )

            # Crop the region by the defined coordinates
            region = img.crop((x, y, x + width, y + height))

            # Clean up
            mem_dc.DeleteDC()
            win32gui.DeleteObject(bmp.GetHandle())
            win32gui.ReleaseDC(hdesktop, desktop_dc)

            return check_text(region, expected_text, check_all_types)

    def capture_and_set_phase(self, region, phase, condition="Competitive", use_bmp=False):
        capture_method = self.capture_region(region["x"], region["y"], region["width"], region["height"], condition)
        if use_bmp:
            capture_method = self.capture_region_bitmap(region["x"], region["y"], region["width"], region["height"], condition)

        if capture_method:
            self.active_queue_phases[phase] = True

    def is_game_finished(self):
        # Take screenshots and if we find one of the end of game menus, we return True. We want to check the first
        # menus that appear at the end of the game first. And if they're present, return True. Otherwise, continue
        # checking the later menus.
        region_to_capture = self.get_region_dimensions("potm_title_region")
        potm_title = self.capture_region(region_to_capture["x"], region_to_capture["y"], region_to_capture["width"],
                                         region_to_capture["height"], "Play of the Match")

        if potm_title:
            return True

        region_to_capture = self.get_region_dimensions("progression_screen_title_region")

        if self.overwatch_client is not None:
            left, top, right, bottom = win32gui.GetWindowRect(self.overwatch_client)
            image = pyautogui.screenshot(region=(left, top, right - left, bottom - top))

            # Crop the region by the defined coordinates
            region = image.crop((region_to_capture["x"], region_to_capture["y"],
                                 region_to_capture["x"] + region_to_capture["width"],
                                 region_to_capture["y"] + region_to_capture["height"]))

            prog_title1 = check_text(region, "Competitive - Role Queue", False)
            prog_title2 = check_text(region, "Competitive - Open Queue", False)
            prog_title3 = check_text(region, "Quick Play - Role Queue", False)
            prog_title4 = check_text(region, "Quick Play - Open Queue", False)

            if prog_title1 or prog_title2 or prog_title3 or prog_title4:
                return True

        region_to_capture = self.get_region_dimensions("comp_progress_cards_region")
        comp_progress = self.capture_region(region_to_capture["x"], region_to_capture["y"], region_to_capture["width"],
                                            region_to_capture["height"], "Competitive Progress")

        if comp_progress:
            return True

        region_to_capture = self.get_region_dimensions("queue_cards_region")
        comp_cards = self.capture_region(region_to_capture["x"], region_to_capture["y"], region_to_capture["width"],
                                         region_to_capture["height"], comp_cards_expected_text)
        quick_cards = self.capture_region(region_to_capture["x"], region_to_capture["y"], region_to_capture["width"],
                                          region_to_capture["height"], quick_cards_expected_text)

        if comp_cards or quick_cards:
            return True

        return False  # Otherwise, return False. None of the menus have been detected.

    def run_queue_watcher(self):
        while True:
            while not self.found_game:
                region_to_capture = self.get_region_dimensions("queue_pop_region")
                print(f'Waiting for match...')
                while not self.active_queue_phases[0]:
                    # If minimized, use BMP, otherwise, take a screenshot.
                    if win32gui.IsIconic(self.overwatch_client):
                        self.capture_and_set_phase(region_to_capture, 0, condition="Game Found!", use_bmp=True)
                    else:
                        self.capture_and_set_phase(region_to_capture, 0, condition="Game Found!")

                # To make sure this isn't a false queue pop, we only confirm the finding of a match
                # after seeing the hero selection screen.
                region_to_capture = self.get_region_dimensions("hero_change_button_region")
                region_to_check = self.get_region_dimensions("queue_region_big")
                while not self.active_queue_phases[1] and self.active_queue_phases[0]:
                    self.capture_and_set_phase(region_to_capture, 1, condition="Ready")

                    # If it is a false queue pop, and we're back in queue, reset all phases.
                    if win32gui.IsIconic(self.overwatch_client):
                        false_queue = self.capture_region_bitmap(region_to_check["x"], region_to_check["y"], region_to_check["width"], region_to_check["height"], expected_text="Competitive", check_all_types=True)
                    else:
                        false_queue = self.capture_region(region_to_check["x"], region_to_check["y"], region_to_check["width"], region_to_check["height"], expected_text="Competitive", check_all_types=True)

                    if false_queue:
                        self.active_queue_phases[0] = self.active_queue_phases[1] = False

                # If the phases haven't been reset, and we've left both loops.
                if self.active_queue_phases[1]:
                    print(f'Found match...')
                    self.found_game = True

            # Game Found
            self.client_handler.game_found(self.selected_hero)
            while self.found_game:
                if self.is_game_finished():
                    self.active_queue_phases[0] = self.active_queue_phases[1] = False
                    self.found_game = False
                    self.client_handler.game_finished()
                    self.selected_hero = None
                    break  # Break to save waiting extra seconds for no reason :)
                time.sleep(1)
