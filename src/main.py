import DiscordBot
import GUI


class App:
    def __init__(self, discord_bot=None):
        self.discord = discord_bot
        pass

    def init_discord(self):
        discord_bot = DiscordBot()
        return discord_bot

    def init_tkinter(self, discord_bot):
        gui = GUI(discord_bot)


def main():
    # Initialize App object
    client = App()

    # Initialize Discord object
    discord_bot = client.init_discord()

    # Initialize GUI
    client.init_tkinter(discord_bot)


if __name__ == '__main__':
    main()
