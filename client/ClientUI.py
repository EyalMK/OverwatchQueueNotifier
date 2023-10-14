import tkinter as tk


class GUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('Overwatch Queue Notifier')
        self.window.geometry('600x500')
        grt = tk.Label(text="Hello, world!")
        grt.pack()

    def run_window(self):
        self.window.mainloop()
