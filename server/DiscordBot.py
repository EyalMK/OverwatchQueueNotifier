from dotenv import load_dotenv
import discord
import os

# Set intents for initialization
intents = discord.Intents.default()
intents.message_content = True

# Commands array
cmds = ["[+] !selecthero {HeroName} - To select a hero as soon as a game is found.\n\n",
        "[+] !remindme - Sends you a reminder message to invite your friends after a game is finished.\n\n",
        "[+] !cancelreminder - Cancels the scheduled reminder, if one was planned.\n\n"
        ]


class DiscordBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user.name}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content == '!selecthero':
            await self.select_hero(message.author)

        elif message.content == '!remindme':
            await self.reminder_invitation(message.author)

        elif message.content == '!cancelreminder':
            await self.cancel_reminder_invitation(message.author)

        elif message.content == '!commands':
            await self.send_commands(message.author)

        # Maybe check if author of message has a certain role, and if not, pass.
        elif message.content == '!adminsecret - commands':
            await self.announce_commands()

    async def announce_commands(self):
        # Load .env
        load_dotenv()
        channel = self.get_channel(int(os.getenv('DISCORD_INFORMATION_CHANNEL_ID')))

        # Format the commands in a message.
        msg = ''
        for cmd in cmds:
            msg += cmd

        # Send the formatted commands.
        await channel.send(msg)


    async def send_commands(self, user):
        # Format the commands in a message.
        msg = ''
        for cmd in cmds:
            msg += cmd

        # Send the formatted commands.
        await user.send(msg)

    async def select_hero(self, user):
        await user.send('I will select {TEST} hero for you.')

    async def reminder_invitation(self, user):
        await user.send("I will remind you to invite your friend, after your game.")

    async def cancel_reminder_invitation(self, user):
        await user.send("I won't remind you this time.")
