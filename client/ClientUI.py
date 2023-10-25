import configparser
import tkinter as tk
from dotenv import load_dotenv
import webbrowser
from tkinter import ttk
import os
import sys

favicon_path = os.getcwd() + '\\assets\\images\\favicon.ico'  # Dev env default path
if getattr(sys, 'frozen', False):
    favicon_path = os.path.join(sys._MEIPASS, './assets/images/favicon.ico')  # Client path


class LoginScreen:
    def __init__(self, client_handler):
        self.client_handler = client_handler
        self.window = tk.Tk()
        self.id_var = tk.StringVar()
        self.wait_var = tk.StringVar()
        self.response_var = tk.StringVar()
        self.remember_var = tk.BooleanVar(value=False)  # Default value is False
        self.load_saved_username()
        self.build_popup_ui()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)  # To terminate the socket connection through the
        # client handler.

    def load_saved_username(self):
        try:
            home_dir = os.path.expanduser("~")
            config_path = os.path.join(home_dir, 'Documents', 'OverwatchQueueNotifier', 'Config_v0.ini')
            config = configparser.ConfigParser()
            config.read(config_path)

            saved_username = config['Default.1']['DiscordUserName'].split('"')[1]
            if saved_username != '':
                self.remember_var.set(True)
            self.id_var.set(saved_username)
        except KeyError:
            # If config file doesn't exist, create it.
            home_dir = os.path.expanduser("~")
            config_path = os.path.join(home_dir, 'Documents', 'OverwatchQueueNotifier', 'Config_v0.ini')
            config = configparser.ConfigParser()
            config['Default.1'] = {}

            config['Default.1']['DiscordUserName'] = '""'

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


    def submit(self):
        username = self.id_var.get()
        if username == '':
            self.response_var.set(f'Invalid username.')
            return
        try:
            self.response_var.set('')
            self.wait_var.set(f'Please message the Discord bot {chr(33)}connect to establish a secure '
                              f'connection...')
            self.client_handler.link_discord_user(username)
            # Check if "Remember Me" is selected
            if self.remember_var.get():
                self.save_username()
        except Exception as e:
            self.response_var.set('Failed to connect. Please enter a valid Discord username, and ensure you are in '
                                  f'the Discord server. {e}')

    def on_hover(self, event):
        event.widget.config(bg='#357ABD', fg='white')  # Darker blue on hover

    def on_leave(self, event):
        event.widget.config(bg='#4287f5', fg='white')  # Blue button

    def open_discord_invite(self):
        # Read DISCORD_INVITATION_LINK from .env file
        load_dotenv()

        # Open the link in the default web browser
        webbrowser.open(os.getenv('DISCORD_INVITATION_LINK'))

    def build_popup_ui(self):
        self.window.title('Overwatch Queue Notifier - Discord Bot Edition')
        path = favicon_path
        self.window.iconbitmap(path)
        self.window.geometry('900x450')
        self.window.configure(bg='#F4F4F4')  # Light gray background

        rdy_label = tk.Label(self.window,
                             text="Welcome to Overwatch Queue Notifier",
                             font=('Arial', 20, 'bold'),
                             bg='#F4F4F4',  # Light gray background
                             fg='#333333')  # Dark text
        rdy_label.pack(pady=(20, 0))

        join_discord_text = tk.Label(self.window,
                                     text="Join our Discord server to unlock access to the Discord bot:",
                                     font=('Arial', 12),
                                     bg='#F4F4F4',
                                     fg='#333333')
        join_discord_text.pack(pady=(20, 0))

        join_discord_button = tk.Button(self.window, text="Join Discord Server",
                                        command=self.open_discord_invite,
                                        bg='#4287f5',
                                        fg='white',
                                        font=('Arial', 12),
                                        padx=20, pady=5,
                                        bd=0,
                                        activebackground='#3c77c8',
                                        activeforeground='#ffffff')
        join_discord_button.pack(pady=(5, 20))

        instruction_label = tk.Label(self.window,
                                     text="Please enter your official Discord username ",
                                     font=('Arial', 12),
                                     bg='#F4F4F4',  # Light gray background
                                     fg='#333333',  # Dark text
                                     wraplength=600,
                                     justify='center')
        instruction_label.pack(pady=(10, 20))  # Increased padding

        id_label = tk.Label(self.window, text="Discord Username", font=('Arial', 12), bg='#F4F4F4', fg='#333333')
        id_entry = ttk.Entry(self.window, textvariable=self.id_var, font=('Arial', 12), width=40)

        remember_checkbox = ttk.Checkbutton(self.window, text="Remember me", variable=self.remember_var,
                                            onvalue=True, offvalue=False, style='TCheckbutton')

        wait_label = tk.Label(self.window, textvariable=self.wait_var, font=('Arial', 12), bg='#F4F4F4', fg='#333333')
        response_label = tk.Label(self.window, textvariable=self.response_var, font=('Arial', 12), bg='#F4F4F4',
                                  fg='#FF5733')  # Red Text

        id_label.pack(pady=(0, 5))  # Moved Discord Username label up
        id_entry.pack(pady=(0, 10))  # Moved entry field up
        remember_checkbox.pack(pady=(0, 10))
        wait_label.pack()
        response_label.pack()

        self.link_button = tk.Button(self.window, text="Link",
                                     command=self.submit,
                                     bg='#4287f5',  # Blue button
                                     fg='white',
                                     font=('Arial', 14, 'bold'),
                                     padx=30, pady=10,  # Increased padding
                                     bd=0,
                                     activebackground='#3c77c8',  # Darker blue on hover
                                     activeforeground='#ffffff')

        self.link_button.pack(pady=(0, 5))  # Align to the left with some padding

        # Hover Effects
        self.link_button.bind("<Enter>", self.on_hover)
        self.link_button.bind("<Leave>", self.on_leave)
        join_discord_button.bind("<Enter>", self.on_hover)
        join_discord_button.bind("<Leave>", self.on_leave)

    def show(self):
        self.window.mainloop()

    def on_closing(self):
        self.client_handler.exit_program()
