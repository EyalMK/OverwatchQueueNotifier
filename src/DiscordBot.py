import discord


class DiscordBot(discord.Client):
    async def on_ready(self):
        user = "test"
        print(f"Discord connected as {user}")

    async def on_message(self):
        pass
