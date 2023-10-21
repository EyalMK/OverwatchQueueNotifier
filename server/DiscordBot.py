from dotenv import load_dotenv
import discord
import os

# Set intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Commands array
cmds = ["[+] !selecthero {HeroName} - To select a hero as soon as a game is found.\n\n",
        "[+] !remindme - Sends you a reminder message to invite your friends after a game is finished.\n\n",
        "[+] !cancelreminder - Cancels the scheduled reminder, if one was planned.\n\n",
        "[+] !cancelqueue - Cancels your Overwatch queue.\n\n",
        "[+] !exitgame - Terminates your active Overwatch game client.\n\n",
        "[+] !exit - Terminates your active Overwatch Queue Notifier client.\n\n",
        ]


class DiscordBot(discord.Client):
    def __init__(self, server):
        super().__init__(intents=intents)
        self.server = server
        self.__reminder = False  # To reduce unnecessary communication between client-server, we'll hold this to keep
        # track of the reminder flag in the server. todo: this won't work with multiple clients, need to hold a reminder flag for each socket OR getter method from the socket.

    async def on_ready(self):
        print(f'Bot is logged in as {self.user.name}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        user_id = str(message.author.id)
        clients = self.server.get_connected_clients()

        # Connection messages.
        if message.content == '!connect':
            awaiting_connections = self.server.get_awaiting_connections()
            if user_id in awaiting_connections:
                if user_id in clients:
                    await message.author.send('User ID already connected from a client. Exiting client...')
                    clients[user_id].send(b'$user_already_logged_in')
                    return
                else:
                    try:
                        self.server.add_client(user_id, awaiting_connections[user_id])  # (
                        # discord id, socket connection)
                        response = f'!authorized_login {message.author.global_name}'.encode()
                        clients[user_id].send(response)
                        print(f'Received authorization from {user_id}')
                        await message.author.send(f'Connection authorized.')
                        self.server.remove_awaiting_connection(user_id)
                        print(f'Client connected.')
                        print(f'Active connections: {len(clients)}')
                    except OSError as e:
                        self.server.remove_client(user_id, awaiting_connections[user_id])
                        await message.author.send(f'Client is not connected to server. Restart client and try again!')
                        print(f'Socket not found. Error: {e}')
            else:
                await message.author.send(f'Connection failed. Invalid ID.')

        if user_id in clients:
            client_socket = clients[user_id]
            if message.content == '!remindme':
                try:
                    client_socket.send(b'set_reminder_true')
                    await self.reminder_invitation(message.author)
                    self.__reminder = True
                except Exception as e:
                    await message.author.send(f'Error communicating with client, make sure client is running. {e}')

            elif message.content == '!cancelreminder':
                try:
                    client_socket.send(b'set_reminder_false')
                    await self.cancel_reminder_invitation(message.author)
                    self.__reminder = False
                except Exception as e:
                    await message.author.send(f'Error communicating with client, make sure client is running. {e}')

            elif message.content == '!testgamefinished':
                try:
                    client_socket.send(b'test_game_finished')
                except Exception as e:
                    await message.author.send(f'Error communicating with client, make sure client is running. {e}')

            elif message.content == '!testcancelqueue':
                try:
                    client_socket.send(b'test_cancel_queue')
                except Exception as e:
                    await message.author.send(f'Error communicating with client, make sure client is running. {e}')

            elif message.content.startswith('!testselecthero'):
                try:
                    parts = message.content.split(' ')[1::]
                    hero = " ".join(parts)
                    client_socket.send(f'!test_select_hero {hero}'.encode())
                except Exception as e:
                    await message.author.send(f'Error communicating with client, make sure client is running. {e}')

            elif message.content == '!exit':
                try:
                    client_socket.send(b'test_exit')
                except Exception as e:
                    await message.author.send(f'Error communicating with client, make sure client is running. {e}')

            elif message.content == '!exitgame':
                try:
                    client_socket.send(b'exit_game')
                except Exception as e:
                    await message.author.send(f'Error communicating with client, make sure client is running. {e}')

            elif message.content == '!commands':
                await self.send_commands(message.author)

            if message.content == '!selecthero':
                await self.select_hero(message.author)

            # Admin Zone
            if message.guild and message.author == message.guild.owner:
                if message.content == '!admin-cmd':
                    await self.announce_commands()

    async def send_user_reminder(self, user_id):
        user = self.get_user(int(user_id))
        if user:
            await user.send("Reminder - Invite your friend/s :)")
        else:
            print('Error - user not found. Make sure to provide the correct user id.')

    async def send_socket_user_id_by_username(self, username):
        user = discord.utils.get(self.users, name=username)
        if user is not None:
            return user.id
        return None

    async def notify_user_game_found(self, user_id):
        user = self.get_user(int(user_id))
        if user:
            await user.send("Your competitive match has been found!")
        else:
            print('Error - user not found. Make sure to provide the correct user id.')

    async def inform_user_select_hero_invalid(self, user_id):
        user = self.get_user(int(user_id))
        if user:
            await user.send("The hero you requested does not exist. Invalid input.")
        else:
            print('Error - user not found. Make sure to provide the correct user id.')

    async def inform_user_select_hero_success(self, user_id):
        user = self.get_user(int(user_id))
        if user:
            await user.send("Hero has been selected.")
        else:
            print('Error - user not found. Make sure to provide the correct user id.')

    async def format_commands(self):
        # Format the commands in a message.
        msg = ''
        for cmd in cmds:
            msg += cmd

        return msg

    async def announce_commands(self):
        # Load .env
        load_dotenv()
        channel = self.get_channel(int(os.getenv('DISCORD_INFORMATION_CHANNEL_ID')))

        # Send the formatted commands.
        await channel.send(await self.format_commands())

    async def send_commands(self, user):
        # Send the formatted commands.
        await user.send(await self.format_commands())

    async def select_hero(self, user):
        # Send hero name to client for selection.
        await user.send('I will select {TEST} hero for you.')

    async def reminder_invitation(self, user):
        # Activate reminder bool in client.
        # If the reminder bool in client is already activated, send a different message.
        if self.__reminder:
            await user.send("Reminder is already set. I will remind you to invite your friend, after your game.")
        else:
            await user.send("I will remind you to invite your friend, after your game.")

    async def cancel_reminder_invitation(self, user):
        # Deactivate reminder bool in client.
        # If the reminder bool in client is not activated, send a different message.
        if not self.__reminder:
            await user.send("There are no reminders scheduled.")
        else:
            await user.send("Reminder cancelled.")
