import tkinter as tk
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
        self.build_popup_ui()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)  # To terminate the socket connection through the
        # client handler.

    def submit(self):
        username = self.id_var.get()
        try:
            self.wait_var.set(f'Waiting for discord user to message bot with !connect.')
            self.client_handler.link_discord_user(username)
        except Exception as e:
            self.response_var.set('Failed to connect. Please enter a valid Discord username, and make sure you are in '
                                  f'the Discord server. {e}')

    def build_popup_ui(self):
        self.window.title('Overwatch Queue Notifier - Discord Bot Edition')

        path = favicon_path
        self.window.iconbitmap(path)
        self.window.geometry('700x200')

        rdy_label = tk.Label(self.window, text="Link your discord, by entering your discord username (Not display name) and messaging the "
                                               "discord bot !connect")
        id_label = tk.Label(self.window, text="Discord Username")
        id_entry = tk.Entry(self.window, textvariable=self.id_var)
        wait_label = tk.Label(self.window, textvariable=self.wait_var)
        response_label = tk.Label(self.window, textvariable=self.response_var)

        submit_button = tk.Button(self.window, text="Link User", command=self.submit)

        rdy_label.pack()
        id_label.pack()
        id_entry.pack()
        wait_label.pack()
        submit_button.pack()
        response_label.pack()

    def show(self):
        self.window.mainloop()

    def on_closing(self):
        self.client_handler.exit_program()
