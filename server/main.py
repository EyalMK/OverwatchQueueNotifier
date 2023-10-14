from dotenv import load_dotenv
import os
from DiscordBot import DiscordBot


class App:
    def __init__(self):
        self.discord_bot = None

    def init_discord(self):
        self.discord_bot = DiscordBot()
        self.discord_bot.run(os.getenv('DISCORD_BOT_TOKEN'))

    def get_discord_bot(self):
        return self.discord_bot


def main():
    # Load .env
    load_dotenv()

    # Initialize App object
    server = App()

    # Initialize Discord object
    server.init_discord()


if __name__ == '__main__':
    main()
