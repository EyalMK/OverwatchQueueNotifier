import tkinter as tk


class MainWindow:
    def __init__(self):
        self.window = tk.Tk()
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


class LoginScreen:
    def __init__(self, client_handler, on_success_callback):
        self.client_handler = client_handler
        self.on_success_callback = on_success_callback
        self.window = tk.Tk()
        self.id_var = tk.StringVar()
        self.wait_var = tk.StringVar()
        self.response_var = tk.StringVar()
        self.build_popup_ui()

    def submit(self):
        id = self.id_var.get()
        try:
            self.wait_var.set(f'Waiting for discord user to message bot with !connect.')
            self.client_handler.link_discord_user(id)
        except Exception as e:
            self.response_var.set('Failed to connect. Please enter a valid Discord username, and make sure you are in '
                                  f'the Discord server. {e}')

    def build_popup_ui(self):
        self.window.title('Overwatch Queue Notifier - Discord')
        self.window.geometry('700x200')

        rdy_label = tk.Label(self.window, text="Link your discord, by entering your discord ID and messaging the "
                                               "discord bot !connect")
        id_label = tk.Label(self.window, text="Discord User ID")
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
