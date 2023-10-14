from ClientUI import GUI
from QueueWatcher import QueueWatcher

class App:
    def __init__(self):
        self.client = None
        self.queue_watcher = None

    def init_gui(self):
        self.client = GUI()
        self.client.run_window()

    def init_queue_watcher(self):
        self.queue_watcher = QueueWatcher()


def main():
    # Initialize App Object
    client = App()

    # Initialize Window Object
    client.init_gui()


if __name__ == '__main__':
    main()
