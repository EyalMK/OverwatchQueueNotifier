import os
import sys
import time
import tkinter as tk
from ctypes import windll
from threading import Thread, Event

import cv2
import numpy as np
import pyautogui
import pytesseract
import win32con
import win32gui
import win32ui
from PIL import Image

from game_info import get_map_key, get_hero_coordinates
from screen_capture import screen_capture_data

_path = r'C:/Program Files/Tesseract-OCR/tesseract.exe'  # Dev env default path
if getattr(sys, 'frozen', False):
    _path = os.path.join(sys._MEIPASS, './Tesseract-OCR/tesseract.exe')  # Client path

pytesseract.pytesseract.tesseract_cmd = _path


def check_text(image, expected_text, check_all_types):
    # Returns True if expected_text is found in the provided image.
    image = np.array(image)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    extracted_text_regular = pytesseract.image_to_string(gray_image)

    # Apply a slight Gaussian Blur
    blur = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # Use adaptive thresholding
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 31, 2)

    # Dilate the text to make it more contiguous
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    dilate = cv2.dilate(thresh, kernel, iterations=1)

    custom_config = r'--oem 3 --psm 6'
    cv2.imwrite(os.getcwd() + '\\playground\\test.png', dilate)
    extracted_text_pre_processed = pytesseract.image_to_string(dilate, config=custom_config)

    # If we requested to check all type of matches, we opt for this block check.
    if check_all_types:
        formatted_text = extracted_text_regular.lower()
        formatted_text += " "
        formatted_text += extracted_text_pre_processed.lower()
        result = "Quick Play".lower() in formatted_text or "Competitive".lower() in formatted_text
        return result

    return expected_text.lower() in extracted_text_regular.lower() or expected_text.lower() in extracted_text_pre_processed.lower()


def get_obj_mode(image):
    image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)

    # Apply a slight Gaussian Blur
    blur = cv2.GaussianBlur(image, (5, 5), 0)

    # Use adaptive thresholding
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 31, 2)

    # Dilate the text to make it more contiguous
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    dilate = cv2.dilate(thresh, kernel, iterations=1)

    custom_config = r'--oem 3 --psm 6'
    extracted_text = pytesseract.image_to_string(dilate, config=custom_config)
    formatted_extracted_text = extracted_text.lower()

    if "def" in formatted_extracted_text or "end" in formatted_extracted_text or "efe" in formatted_extracted_text:
        return "defending"
    return "attacking"


def get_map_name(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)

    # Apply a slight Gaussian Blur
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Use adaptive thresholding
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 31, 4)

    # Dilate the text to make it more contiguous
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    dilate = cv2.dilate(thresh, kernel, iterations=1)

    custom_config = r'--oem 3 --psm 6'
    cv2.imwrite(os.getcwd() + '\\playground\\test.png', dilate)
    extracted_text_pre_processed = pytesseract.image_to_string(dilate, config=custom_config)

    extracted_text_regular = pytesseract.image_to_string(gray)
    return get_map_key(extracted_text_pre_processed.lower().strip()) or get_map_key(
        extracted_text_regular.lower().strip())


class QueueWatcher(Thread):
    # Phase 0: Find Game Found text from screenshot of queue pop box region.
    # Phase 1: Find Entering Game text from screenshot of entering game box region. (To avoid false queues)
    active_queue_phases = [False, False]
    found_game = False
    monitor_resolution = None  # (Width, Height)
    overwatch_resolution = None  # (Width, Height)
    overwatch_client = None
    has_selected_hero = False

    # Singleton instance
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(QueueWatcher, cls).__new__(cls)
        return cls._instance

    def __init__(self, client_handler):
        super().__init__()
        self.game_finished_event = None
        self.running = Event()
        self.running.set()
        self.client_handler = client_handler

    def start(self):
        # Find main monitor resolution.
        self.get_monitor_resolution()

        # While Overwatch window is not found, keep looking before proceeding.
        self.overwatch_client = self.find_overwatch()

        # When Overwatch window is found, make sure the resolution matches the main monitor resolution.
        self.get_resolution()
        if self.monitor_resolution != self.overwatch_resolution:
            self.set_queue_watcher_var_safe(
                'Queue Watcher is running: Error - resolutions do not match. Terminating...')
            self.client_handler.resolutions_not_matching()

        # Bring Overwatch to the foreground (active window).
        self.set_overwatch_active_window()

        # Call self.queue_watcher() method, which starts taking screenshots of Overwatch window, and checking if at
        # the top middle of the screen, there is a red bar containing the words "Competitive" and a timer
        queue_detector_thread = Thread(target=self.run_queue_watcher)
        queue_detector_thread.setDaemon(True)
        queue_detector_thread.start()

    def stop(self):
        self.running.clear()

    def set_overwatch_active_window(self):
        if not self.running.is_set():
            return

        try:
            if self.overwatch_client is not None:
                win32gui.ShowWindow(self.overwatch_client, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(self.overwatch_client)
        except Exception as e:
            print(f'Error setting Overwatch as active window. {e}')

    def find_overwatch(self):
        # Finds Overwatch window.
        while self.running.is_set():
            hwnd = win32gui.FindWindow(None, 'Overwatch')
            if hwnd != 0:
                self.set_queue_watcher_var_safe('Queue Watcher is running: Found Overwatch...')
                time.sleep(1.5)  # Precaution to avoid issues with resolution retrieval.
                return hwnd
            self.set_queue_watcher_var_safe('Queue Watcher is running: Looking for Overwatch...')
            time.sleep(0.5)

        self.set_queue_watcher_var_safe('Queue Watcher is not running.')

    def get_monitor_resolution(self):
        # Gets main monitor resolution by running Tkinter (which launches on the main monitor) and utilizing library
        # methods.
        root = tk.Tk()
        height = root.winfo_screenheight()
        width = root.winfo_screenwidth()
        root.destroy()

        self.monitor_resolution = width, height

    def get_resolution(self):
        if not self.running.is_set():
            return

        if self.overwatch_client is not None:
            self.set_overwatch_active_window()
            rect = win32gui.GetClientRect(self.overwatch_client)
            self.overwatch_resolution = (rect[2] - rect[0], rect[3] - rect[1])

    def get_region_dimensions(self, region, coordinates=False):
        if not self.running.is_set():
            return

        if coordinates:
            return screen_capture_data['coordinates_resolution_options'][
                region + f'_{self.overwatch_resolution[0]}x{self.overwatch_resolution[1]}']
        return screen_capture_data['region_resolution_options'][
            region + f'_{self.overwatch_resolution[0]}x{self.overwatch_resolution[1]}']

    def get_coordinates(self, region, hero):
        if not self.running.is_set():
            return

        res_coordinates = region + f'_{self.overwatch_resolution[0]}x{self.overwatch_resolution[1]}'
        coordinates = get_hero_coordinates(res_coordinates)
        return coordinates[hero]

    def set_queue_watcher_var_safe(self, text):
        self.client_handler.main_app.get_client_ui().set_queue_watcher_var(text)

    def cancel_queue(self):
        if not self.running.is_set():
            return

        if self.found_game:
            self.client_handler.cancel_queue_failure(1)  # Errno 1: In game.
            return

        # Check if rectangle exists atop. If so, PyAutoGUI to hover over it for 0.5 seconds and then go down 100
        # height and press on cancel. Else, check if rectangle exists top left. If so, press Escape until we see "Menu"
        # and then go to "Leave Game and Queue"
        # Each check must be done 3 times at most,
        # after which, safe to assume not in queue, so we send the server "Not in queue".
        def capture_and_leave(x, y, width, height, attempt):
            if not self.running.is_set():
                return

            if self.capture_region(x, y, width, height, "Competitive"):
                self.leave_queue(attempt)
                # Reset all phases
                self.active_queue_phases[0] = self.active_queue_phases[1] = False
                return True

            return False

        def attempt_to_leave(attempt, region):
            if not self.running.is_set():
                return

            reg = self.get_region_dimensions(region)
            return capture_and_leave(reg["x"],
                                     reg["y"],
                                     reg["width"],
                                     reg["height"],
                                     attempt)

        left_queue = False

        attempts = 0
        max_attempts = 6

        while attempts < max_attempts and not left_queue:
            if not self.running.is_set():
                return

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
        if not self.running.is_set():
            return

        # Calculate the actual coordinates based on the screen resolution
        actual_x = int((x / 1920) * self.monitor_resolution[0])

        actual_y = int((y / 1080) * self.monitor_resolution[1])

        # Move the mouse to the specified coordinates
        pyautogui.moveTo(actual_x, actual_y, duration=0.3)

    def leave_queue(self, action):
        if not self.running.is_set():
            return

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
            try:
                left, top, right, bottom = win32gui.GetWindowRect(self.overwatch_client)
                image = pyautogui.screenshot(region=(left, top, right - left, bottom - top))
                # Crop the region by the defined coordinates and save it.
                region_to_capture = self.get_region_dimensions("available_selection")
                region = image.crop((region_to_capture["x"], region_to_capture["y"],
                                     region_to_capture["x"] + region_to_capture["width"],
                                     region_to_capture["y"] + region_to_capture["height"]))
                region.save(os.getcwd() + '\\hs-btn-scrn.png')

                # Convert the image to the HSV color space
                image_to_process = cv2.imread(os.getcwd() + '\\hs-btn-scrn.png')
                hsv = cv2.cvtColor(image_to_process, cv2.COLOR_BGR2HSV)

                # Define the range for orange color in HSV
                lower_orange = np.array([5, 50, 50])
                upper_orange = np.array([15, 255, 255])

                # Create a mask for the orange color
                mask = cv2.inRange(hsv, lower_orange, upper_orange)

                # Calculate the percentage of orange pixels
                total_pixels = image_to_process.shape[0] * image_to_process.shape[1]
                orange_pixels = np.sum(mask > 0)
                percentage_orange = (orange_pixels / total_pixels) * 100

                # If more than a certain percentage of the image is orange,
                # consider it an available button
                return percentage_orange > 60  # 60 Threshold was deemed appropriate, considering some backgrounds are
                # orange and the button is actually transparent...
            except Exception as e:
                print(f'Error on checking if hero is selectable - {e}')
                self.client_handler.main_app.get_client_ui().on_close()
        return False  # Overwatch isn't running...

    def select_hero(self, hero):
        if not self.running.is_set():
            return
        self.set_overwatch_active_window()
        if self.found_game:
            self.move_mouse(920, 250)  # To not block text
            # Enter hero select screen, if not there.
            hero_details_region = self.get_region_dimensions(
                "hero_select_details_region")  # Hero selection screen exclusive
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

            select_hero_button = self.get_region_dimensions("select_hero_button", coordinates=True)
            # Now we check if we've already picked a hero.
            if self.has_selected_hero:
                # Now select Change Hero button
                self.move_mouse(select_hero_button["x"], select_hero_button["y"])
                time.sleep(0.3)
                pyautogui.click()
                # Now we're in the hero selection screen. Continue outside the function to select the hero.
            # Otherwise, we haven't picked a hero, the button is "Ready" or "Continue", so we're already in the
            # hero selection screen.
            coordinates = self.get_coordinates("heroes_coordinates", hero)
            self.move_mouse(coordinates[0], coordinates[1])
            time.sleep(0.3)
            pyautogui.click()
            # Now select Ready/Continue button
            self.move_mouse(select_hero_button["x"], select_hero_button["y"])
            # Check if "Continue" button is greyed out.
            if self.check_available_selection():
                self.client_handler.set_hero_select_failure(False)
                pyautogui.click()
                self.has_selected_hero = True
            else:
                self.client_handler.set_hero_select_failure(True)
                self.client_handler.scheduled_hero = None
                self.has_selected_hero = False

    def capture_region(self, x, y, width, height, expected_text, check_all_types=False):
        if self.overwatch_client:
            try:
                left, top, right, bottom = win32gui.GetWindowRect(self.overwatch_client)
                image = pyautogui.screenshot(region=(left, top, right - left, bottom - top))

                # Crop the region by the defined coordinates
                region = image.crop((x, y, x + width, y + height))

                return check_text(region, expected_text, check_all_types)
            except Exception as e:
                print(f'Error capturing region - {e}')
                self.client_handler.main_app.get_client_ui().on_close()
        return False  # Overwatch isn't running...

    # We use this only for queue detection, since it's fairly costly when used frequently.
    # This takes a screenshot of a minimized window and recreates it (with a bitmap).
    def capture_region_bitmap(self, x, y, width, height, expected_text, check_all_types=False):
        if self.overwatch_client:
            # Get the window dimensions
            try:
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
            except Exception as e:
                print(f'Error capturing region BMP - {e}')
                self.client_handler.main_app.get_client_ui().on_close()
        return False

    def capture_and_set_phase(self, region, phase, condition="Competitive", use_bmp=False):
        if self.active_queue_phases[phase]:
            return  # Phase is already set...
        capture_method = self.capture_region(region["x"], region["y"], region["width"], region["height"], condition)
        if use_bmp:
            capture_method = self.capture_region_bitmap(region["x"], region["y"], region["width"], region["height"],
                                                        condition)
        if capture_method:
            self.active_queue_phases[phase] = True

    def scan_progression_screen(self):
        while not self.game_finished_event.is_set() and self.running.is_set():
            # Progression screen region
            region_to_capture = self.get_region_dimensions("progression_screen_title_region")
            if self.overwatch_client is not None:
                try:
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
                        self.game_finished_event.set()
                    time.sleep(1)
                except:
                    self.game_finished_event.set()  # One here is enough, because it'll cause all other threads doing capture_region to stop anyway.
                    self.client_handler.main_app.get_client_ui().on_close()

    def scan_potm_title(self):
        while not self.game_finished_event.is_set() and self.running.is_set():
            # Play of the Match title
            region_to_capture = self.get_region_dimensions("potm_title_region")
            potm_title = self.capture_region(region_to_capture["x"], region_to_capture["y"], region_to_capture["width"],
                                             region_to_capture["height"], "Play of the Match")
            if potm_title:
                self.game_finished_event.set()
            time.sleep(1)

    def scan_comp_progression_cards(self):
        while not self.game_finished_event.is_set() and self.running.is_set():
            # Competitive progression cards
            region_to_capture = self.get_region_dimensions("comp_progress_cards_region")
            comp_progress = self.capture_region(region_to_capture["x"], region_to_capture["y"],
                                                region_to_capture["width"],
                                                region_to_capture["height"], "Competitive Progress")
            if comp_progress:
                self.game_finished_event.set()
            time.sleep(1)

    def scan_game_mode_card_title(self):
        while not self.game_finished_event.is_set() and self.running.is_set():
            # Competitive/Quick play cards title
            region_to_capture = self.get_region_dimensions("play_mode_region")
            comp_cards = self.capture_region(region_to_capture["x"], region_to_capture["y"], region_to_capture["width"],
                                             region_to_capture["height"], "Competitive")
            quick_cards = self.capture_region(region_to_capture["x"], region_to_capture["y"],
                                              region_to_capture["width"],
                                              region_to_capture["height"], "Unranked")

            if comp_cards or quick_cards:
                self.game_finished_event.set()
            time.sleep(1)

    def scan_play_title_menu(self):
        while not self.game_finished_event.is_set() and self.running.is_set():
            # Play menu
            region_to_capture = self.get_region_dimensions("menu_play_sign")
            if self.capture_region(region_to_capture["x"], region_to_capture["y"], region_to_capture["width"],
                                   region_to_capture["height"], "Play"):
                self.game_finished_event.set()
            time.sleep(1)

    def scan_landing_page_menu(self):
        while not self.game_finished_event.is_set() and self.running.is_set():
            # Landing page menu
            region_to_capture = self.get_region_dimensions("landing_menu_region")
            if self.capture_region(region_to_capture["x"], region_to_capture["y"], region_to_capture["width"],
                                   region_to_capture["height"], "Exit"):
                self.game_finished_event.set()
            time.sleep(1)

    def is_game_finished(self):
        # Create a thread for each menu/end game check.
        threads = [Thread(target=self.scan_progression_screen), Thread(target=self.scan_potm_title),
                   Thread(target=self.scan_comp_progression_cards), Thread(target=self.scan_game_mode_card_title),
                   Thread(target=self.scan_play_title_menu), Thread(target=self.scan_landing_page_menu)]

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

    def run_queue_watcher(self):
        while self.running.is_set():
            while not self.found_game:
                region_to_capture = self.get_region_dimensions("queue_pop_region")
                self.set_queue_watcher_var_safe('Queue Watcher is running: Looking for a match...')
                while not self.active_queue_phases[0]:
                    if not self.running.is_set():
                        break
                    self.capture_and_set_phase(region_to_capture, 0, condition="Game Found!", use_bmp=True)
                    self.capture_and_set_phase(region_to_capture, 0, condition="Game Found!")
                try:
                    self.set_overwatch_active_window()
                except:
                    pass
                # To make sure this isn't a false queue pop, we only confirm the finding of a match
                # after we see the hero selection screen.
                region_to_capture_1 = self.get_region_dimensions("hero_change_button_region")
                region_to_capture_2 = self.get_region_dimensions("assemble_team_region")
                region_to_check = self.get_region_dimensions("queue_region_big")
                while not self.active_queue_phases[1] and self.active_queue_phases[0]:
                    if not self.running.is_set():
                        break
                    self.capture_and_set_phase(region_to_capture_1, 1, condition="Ready")
                    if self.active_queue_phases[1]:
                        break
                    self.capture_and_set_phase(region_to_capture_1, 1, condition="Ready", use_bmp=True)
                    if self.active_queue_phases[1]:
                        break
                    self.capture_and_set_phase(region_to_capture_2, 1, condition="Assemble")
                    if self.active_queue_phases[1]:
                        break
                    self.capture_and_set_phase(region_to_capture_2, 1, condition="Assemble", use_bmp=True)
                    if self.active_queue_phases[1]:
                        break

                    # If it is a false queue pop, and we're back in queue, reset all phases.
                    if self.capture_region(region_to_check["x"], region_to_check["y"],
                                           region_to_check["width"], region_to_check["height"],
                                           expected_text="Competitive", check_all_types=True):
                        self.active_queue_phases[0] = self.active_queue_phases[1] = False

                # If the phases haven't been reset, and we've left both loops.
                if self.active_queue_phases[1]:
                    region_to_capture = self.get_region_dimensions("obj_mode_region")
                    objective = map_name = ""
                    try:
                        left, top, right, bottom = win32gui.GetWindowRect(self.overwatch_client)
                        image = pyautogui.screenshot(region=(left, top, right - left, bottom - top))

                        # Crop the region by the defined coordinates
                        region_obj = image.crop((region_to_capture["x"], region_to_capture["y"],
                                                 region_to_capture["x"] + region_to_capture["width"],
                                                 region_to_capture["y"] + region_to_capture["height"]))
                        objective = get_obj_mode(region_obj)

                        region_to_capture = self.get_region_dimensions("map_name_region")
                        region_map = image.crop((region_to_capture["x"], region_to_capture["y"],
                                                 region_to_capture["x"] + region_to_capture["width"],
                                                 region_to_capture["y"] + region_to_capture["height"]))
                        map_name = get_map_name(region_map)
                    except Exception as e:
                        print(f'Error retrieving obj/map: {e}')

                    self.set_queue_watcher_var_safe('Queue Watcher is running: Found a match...')
                    self.found_game = True
                    self.client_handler.game_found(objective, map_name)

            # Game Found
            if self.found_game:
                if not self.running.is_set():
                    break

                # Select hero
                self.has_selected_hero = False
                hero = self.client_handler.scheduled_hero
                if hero is not None:
                    self.has_selected_hero = self.client_handler.schedule_hero(
                        hero)  # Returns select_hero return value in this case...

                # If we couldn't select the scheduled hero, select a default one.
                if not self.has_selected_hero:
                    for hero in self.client_handler.get_default_heroes():
                        if self.client_handler.select_hero(hero, manual=False):
                            break  # A default hero was selected.

                # If we couldn't select any default heroes, then we send a message.
                if not self.has_selected_hero:
                    self.client_handler.client_socket.send(b'!select_default_hero_unavailable')

                # Set up the event for the threads, and start the monitoring threads.
                self.game_finished_event = Event()
                self.is_game_finished()
                self.game_finished_event.wait()  # Wait for the event to finish (one of the threads to spot end game).

                if not self.running.is_set():
                    break

                # Reset phases, flags and trigger client_handler game finished event.
                self.active_queue_phases[0] = self.active_queue_phases[1] = False
                self.found_game = False
                self.has_selected_hero = False
                self.client_handler.game_finished()

        # Disconnected...
        self.set_queue_watcher_var_safe('Queue Watcher is not running.')
