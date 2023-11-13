import configparser
import tkinter as tk
import webbrowser
from ctypes import windll, byref, sizeof, c_int

import requests
from customtkinter import *

from game_info import game_data

favicon_path = os.getcwd() + '\\assets\\images\\favicon.ico'  # Dev env default path
if getattr(sys, 'frozen', False):
    favicon_path = os.path.join(sys._MEIPASS, './assets/images/favicon.ico')  # Client path


def get_patch_status():
    try:
        response = requests.get('https://overnotifier.com/api/patch')
        response.raise_for_status()
        if response.json():
            return "There is an update available. Download the new client from the website."
        return ""
    except requests.RequestException as e:
        print(f'Error fetching : {e}')
        return ""


def open_discord_invite():
    # Open the link in the default web browser
    webbrowser.open('https://discord.gg/nzgwsvtzXW')


class ClientScreen:
    def __init__(self, main_app):
        self.main_app = main_app
        self.window = tk.Tk()
        self.width = 900
        self.height = 500
        self.id_var = tk.StringVar()
        self.wait_var = tk.StringVar()
        self.response_var = tk.StringVar()
        self.connection_var = tk.StringVar(value="You are not connected.")
        self.connection_label = None
        self.connected = False
        self.queue_watcher_var = tk.StringVar(value="Queue Watcher is not running.")
        self.reminder_var = tk.StringVar(value="Reminder is not set.")
        self.default_tank = tk.StringVar()
        self.default_dps = tk.StringVar()
        self.default_support = tk.StringVar()
        self.remember_var = tk.BooleanVar(value=False)  # Default value is False
        self.live_patch_var = tk.StringVar(value=get_patch_status())
        self.load_saved_settings()
        self.build_popup_ui()
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)  # To terminate the socket connection through the
        # client handler.

    def load_saved_settings(self):
        try:
            home_dir = os.path.expanduser("~")
            config_path = os.path.join(home_dir, 'Documents', 'OverwatchQueueNotifier', 'Config_v0.ini')
            config = configparser.ConfigParser()
            config.read(config_path)

            saved_username = config['Default.1']['DiscordUserName'].split('"')[1]
            default_tank = config['Default.1']['DefaultTank'].split('"')[1]
            default_dps = config['Default.1']['DefaultDPS'].split('"')[1]
            default_support = config['Default.1']['DefaultSupport'].split('"')[1]

            if saved_username != '':
                self.remember_var.set(True)
            self.id_var.set(saved_username)

            self.default_tank.set(default_tank)
            self.default_dps.set(default_dps)
            self.default_support.set(default_support)

        except KeyError:
            # If config file doesn't exist, create it.
            home_dir = os.path.expanduser("~")
            config_path = os.path.join(home_dir, 'Documents', 'OverwatchQueueNotifier', 'Config_v0.ini')
            config = configparser.ConfigParser()
            config['Default.1'] = {}

            config['Default.1']['DiscordUserName'] = '""'
            config['Default.1']['DefaultTank'] = '"Choose Hero"'
            config['Default.1']['DefaultDPS'] = '"Choose Hero"'
            config['Default.1']['DefaultSupport'] = '"Choose Hero"'

            with open(config_path, 'w') as configfile:
                config.write(configfile)

    def save_username(self):
        home_dir = os.path.expanduser("~")
        config_path = os.path.join(home_dir, 'Documents', 'OverwatchQueueNotifier', 'Config_v0.ini')
        config = configparser.ConfigParser()

        if os.path.exists(config_path):
            config.read(config_path)
        else:
            config['Default.1'] = {}

        saved_username = self.id_var.get()
        config['Default.1']['DiscordUserName'] = f'"{saved_username}"'

        with open(config_path, 'w') as configfile:
            config.write(configfile)

    def save_heroes(self, tank, dps, support):
        home_dir = os.path.expanduser("~")
        config_path = os.path.join(home_dir, 'Documents', 'OverwatchQueueNotifier', 'Config_v0.ini')
        config = configparser.ConfigParser()

        if os.path.exists(config_path):
            config.read(config_path)
        else:
            config['Default.1'] = {}

        config['Default.1']['DefaultTank'] = f'"{tank}"'
        config['Default.1']['DefaultDPS'] = f'"{dps}"'
        config['Default.1']['DefaultSupport'] = f'"{support}"'

        with open(config_path, 'w') as configfile:
            config.write(configfile)

    def set_default_heroes(self):
        tank = self.default_tank.get()
        dps = self.default_dps.get()
        support = self.default_support.get()

        if tank != 'Choose Hero':
            self.main_app.client_handler.set_default_tank(tank)
        if dps != 'Choose Hero':
            self.main_app.client_handler.set_default_dps(dps)
        if support != 'Choose Hero':
            self.main_app.client_handler.set_default_support(support)

    def clear_hero_selection(self, val):
        tank = self.default_tank.get()
        dps = self.default_dps.get()
        support = self.default_support.get()

        if dps == 'Clear':
            self.default_dps.set('Choose Hero')
        elif support == 'Clear':
            self.default_support.set('Choose Hero')
        elif tank == 'Clear':
            self.default_tank.set('Choose Hero')

        self.set_default_heroes()

    def submit(self):
        username = self.id_var.get()
        tank = self.default_tank.get()
        dps = self.default_dps.get()
        support = self.default_support.get()

        if username == '' or username == ' ':
            self.wait_var.set('')
            self.response_var.set(f'Invalid username.')
            return

        if self.connected:
            self.wait_var.set('Already connected.')
            return
        try:
            self.response_var.set('')
            self.wait_var.set(f'Please message the Discord bot {chr(33)}connect to establish a secure '
                              f'connection...')
            self.connection_var.set('Awaiting authorization...')
            self.main_app.client_handler.link_discord_user(username)
            # Check if "Remember Me" is selected
            if self.remember_var.get():
                self.save_username()

            self.save_heroes(tank, dps, support)
            self.set_default_heroes()
        except Exception as e:
            self.response_var.set('Failed to connect. Please enter a valid Discord username, and ensure you are in '
                                  f'the Discord server. {e}')

    def disconnect(self):
        if self.queue_watcher_var.get() not in ['Queue Watcher is running: Looking for Overwatch...',
                                                'Queue Watcher is not running.']:
            self.response_var.set('Cannot disconnect while Overwatch is active. Exit client or Overwatch.')
            return

        self.connection_var.set("You are not connected.")
        self.reminder_var.set("Reminder is not set.")
        self.wait_var.set('')
        self.response_var.set('')
        self.connected = False
        self.main_app.client_handler.stop_queue_watcher()
        self.main_app.client_handler.send_disconnect()

    def set_connected(self, username):
        self.connection_var.set(f'Connected as {username}')
        self.connected = True

    def set_queue_watcher_var(self, text):
        self.window.after(0, lambda: self.queue_watcher_var.set(text))

    def set_reminder_var(self, text):
        self.reminder_var.set(text)

    def configure_connection_label_color(self, *args):
        var = self.connection_var.get()
        if var == "You are not connected.":
            self.connection_label.configure(text_color='#FA113D')
        elif var == "Awaiting authorization...":
            self.connection_label.configure(text_color='#FFFFFF')
        else:
            self.connection_label.configure(text_color='#198754')
            self.wait_var.set('')
            self.response_var.set('')
            self.queue_watcher_var.set('Queue Watcher is running: ')

    def build_popup_ui(self):
        self.window.title('Overwatch Queue Notifier')

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        standard_width = 900
        standard_height = 500
        scale_width = standard_width / screen_width
        scale_height = standard_height / screen_height
        self.width = int(screen_width * scale_width)
        self.height = int(screen_height * scale_height)

        self.window.geometry(f'{self.width}x{self.height}')
        self.window.resizable(False, False)
        self.window.configure(bg='#2a2b2e')  # Overwatch 2 dark theme background color
        self.window.iconbitmap(favicon_path)
        hwnd = windll.user32.GetParent(self.window.winfo_id())
        windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, byref(c_int(0x2a2b2e)), sizeof(c_int))

        # Custom style for Overwatch 2 dark theme
        custom_style = {'bg_color': '#2a2b2e', 'fg_color': '#2a2b2e'}

        # Header
        header_frame = CTkFrame(self.window, **custom_style)
        header_frame.pack(fill='x', pady=10)
        header_label = CTkLabel(header_frame, text="Welcome to Overwatch Queue Notifier",
                                font=('Montserrat Medium', 20, 'bold'))
        header_label.pack(side='top', fill='x')

        self.connection_label = CTkLabel(header_frame, textvariable=self.connection_var,
                                         font=('Montserrat Regular', 16))
        self.connection_label.pack(side='top')

        self.configure_connection_label_color()
        self.connection_var.trace_add('write', self.configure_connection_label_color)

        # Form Section
        form_frame = CTkFrame(self.window, corner_radius=10, **custom_style, border_color='#004aad')
        form_frame.pack(fill='x', padx=50, pady=5)
        instruction_label = CTkLabel(form_frame, text="Discord username", **custom_style,
                                     font=('Montserrat Regular', 14))
        instruction_label.pack(side='left')

        id_entry = CTkEntry(form_frame, textvariable=self.id_var, placeholder_text="Enter your username",
                            **custom_style, border_color='#555555')
        id_entry.pack(side='left', padx=5)

        action_btts_frame = CTkFrame(self.window, corner_radius=10, **custom_style, border_color='#004aad')
        action_btts_frame.pack(fill='x', padx=165, pady=5)

        # Remember Me Checkbox
        remember_checkbox = CTkCheckBox(action_btts_frame, text="Remember me", variable=self.remember_var,
                                        fg_color='#0060FF',
                                        checkmark_color='#FFFFFF', hover_color='#CEE0FF', onvalue=True, offvalue=False)
        remember_checkbox.pack(side='left', padx=20)

        # Connect Button
        link_button = CTkButton(action_btts_frame, text="Connect", command=self.submit, fg_color='#007AFF',
                                hover_color='#0052AC')
        link_button.pack(side='left', padx=5)

        # Disconnect Button
        disconnect_button = CTkButton(action_btts_frame, text="Disconnect", command=self.disconnect, fg_color='#2a2b2e',
                                      hover_color='#3A3B3E', text_color='#FA113D')
        disconnect_button.pack(side='left')

        # Status Messages
        wait_label = CTkLabel(self.window, textvariable=self.wait_var, font=('Montserrat Regular', 16))
        response_label = CTkLabel(self.window, textvariable=self.response_var, font=('Montserrat Regular', 16))
        wait_label.pack()
        response_label.pack()

        # Client Functionality Section
        client_functions_frame = CTkFrame(self.window, corner_radius=10, **custom_style, border_color='#004aad')
        client_functions_frame.pack(fill='x', padx=50)
        # Queue Watcher Section
        queue_watcher_frame = CTkFrame(client_functions_frame, corner_radius=10, **custom_style, border_color='#004aad')
        queue_watcher_frame.pack(fill='x')
        queue_watcher_text = CTkLabel(queue_watcher_frame, textvariable=self.queue_watcher_var, **custom_style,
                                      font=('Montserrat Regular', 14))
        queue_watcher_text.pack(side='left')

        reminder_text = CTkLabel(client_functions_frame, textvariable=self.reminder_var, **custom_style,
                                 font=('Montserrat Regular', 14))
        reminder_text.pack(side='left', fill='x')

        # Discord Server Join Section
        discord_frame = CTkFrame(self.window, corner_radius=10, **custom_style, border_color='#004aad')
        discord_frame.pack(fill='x', padx=50, pady=45)
        join_discord_text = CTkLabel(discord_frame, text="Join our Discord server to access the bot:", **custom_style,
                                     font=('Montserrat Regular', 14))
        join_discord_button = CTkButton(discord_frame, text="Open Invitation",
                                        command=open_discord_invite, fg_color='#007AFF', hover_color='#0052AC')
        join_discord_text.pack(side='left')
        join_discord_button.pack(side='left', padx=5, pady=5)

        # Hero Selection Section divided by role
        hero_label_frame = CTkFrame(self.window, corner_radius=10, **custom_style, border_color='#004aad')
        hero_label_frame.pack(fill='x', padx=50, pady=0)

        default_hero_text = CTkLabel(hero_label_frame,
                                     text="Choose your default heroes, whom will automatically be selected when your games are found.",
                                     **custom_style,
                                     font=('Montserrat Regular', 14))
        default_hero_text.pack(side='top')

        # Tank Heroes Option Menu
        tank_hero_frame = CTkFrame(hero_label_frame, corner_radius=10, **custom_style, border_color='#004aad')
        tank_hero_frame.pack(side='left', expand=True, fill='both', padx=5)
        tank_hero_label = CTkLabel(tank_hero_frame, text="Tank Hero", **custom_style, font=('Montserrat Regular', 12))
        tank_hero_label.pack(side='left')
        tank_hero_choices = ['Clear'] + list(game_data['tanks'].keys())
        tank_hero_menu = CTkOptionMenu(tank_hero_frame, variable=self.default_tank, values=tank_hero_choices,
                                       command=self.clear_hero_selection,
                                       **custom_style, button_color='#555555')
        tank_hero_menu.pack(side='left', padx=10)

        # DPS Heroes Option Menu
        dps_hero_frame = CTkFrame(hero_label_frame, corner_radius=10, **custom_style, border_color='#004aad')
        dps_hero_frame.pack(side='left', expand=True, fill='both', padx=5)
        dps_hero_label = CTkLabel(dps_hero_frame, text="DPS Hero", **custom_style, font=('Montserrat Regular', 12))
        dps_hero_label.pack(side='left', padx=5)
        dps_hero_choices = ['Clear'] + list(game_data['dps'].keys())
        dps_hero_menu = CTkOptionMenu(dps_hero_frame, variable=self.default_dps, values=dps_hero_choices,
                                      command=self.clear_hero_selection,
                                      **custom_style, button_color='#555555')
        dps_hero_menu.pack(side='left', padx=10)

        # Support Heroes Option Menu
        support_hero_frame = CTkFrame(hero_label_frame, corner_radius=10, **custom_style, border_color='#004aad')
        support_hero_frame.pack(side='left', expand=True, fill='both', padx=5)
        support_hero_label = CTkLabel(support_hero_frame, text="Support Hero", **custom_style,
                                      font=('Montserrat Regular', 12))
        support_hero_label.pack(side='left', padx=5)
        support_hero_choices = ['Clear'] + list(game_data['supports'].keys())
        support_hero_menu = CTkOptionMenu(support_hero_frame, variable=self.default_support,
                                          values=support_hero_choices, command=self.clear_hero_selection,
                                          **custom_style, button_color='#555555')
        support_hero_menu.pack(side='left', padx=10)

        live_patch_label = CTkLabel(self.window, textvariable=self.live_patch_var, font=('Montserrat Regular', 16), text_color='#1C9000')
        live_patch_label.pack(side='top', pady=10)

    def show(self):
        self.window.mainloop()

    def on_close(self):
        self.main_app.client_handler.stop_queue_watcher()
        self.main_app.client_handler.send_disconnect()
        self.main_app.client_handler.close_connection()
        self.window.destroy()
