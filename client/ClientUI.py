import tkinter as tk


class MainWindow:
    def __init__(self, queue_watcher):
        self.window = tk.Tk()
        self.queue_watcher = queue_watcher
        self.build_client_ui()

    def build_client_ui(self):
        self.window.title('Overwatch Queue Notifier')
        self.window.geometry('700x120')

        rdy_label = tk.Label(self.window, text="Client is launched...")
        txt1 = tk.Text(self.window, height=2)
        txt2 = tk.Text(self.window, height=2)

        txt1.insert('1.0',
                    "Minimize the application and communicate with the discord bot using the commands in the "
                    "information channel.")
        txt2.insert('1.0', "The application will now actively notify you when a game is found.")

        rdy_label.pack()
        txt1.pack()
        txt2.pack()

    def show(self):
        self.window.mainloop()


class DiscordPopUp:
    def __init__(self, queue_watcher, on_success_callback):
        self.queue_watcher = queue_watcher
        self.window = tk.Tk()
        self.name_var = tk.StringVar()
        self.error_var = tk.StringVar()
        self.on_success_callback = on_success_callback
        self.build_popup_ui()

    def submit(self):
        name = self.name_var.get()
        try:
            self.queue_watcher.link_discord_user(name)
            self.on_success_callback()
        except Exception as e:
            self.error_var.set('Failed to connect. Please enter a valid Discord username, and make sure you are in '
                               'the Discord server.')

    def build_popup_ui(self):
        self.window.title('Overwatch Queue Notifier - Discord')
        self.window.geometry('700x200')

        rdy_label = tk.Label(self.window, text="Link your discord, by entering your discord username")
        name_label = tk.Label(self.window, text="Discord Username")
        name_entry = tk.Entry(self.window, textvariable=self.name_var)
        error_entry = tk.Label(self.window, textvariable=self.error_var, bg="#980000")

        submit_button = tk.Button(self.window, text="Connect", command=self.submit)

        rdy_label.pack()
        name_label.pack()
        name_entry.pack()
        submit_button.pack()
        error_entry.pack()
