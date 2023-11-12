import os

import discord
import docker
from dotenv import load_dotenv

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
        ]


async def restart_server():
    load_dotenv()
    image_name = os.getenv('IMAGE_NAME')
    cl = docker.from_env()

    container = None
    for c in cl.containers.list():
        if image_name in c.image.tags:
            container = c
            break

    if container:
        container.stop()
        container.remove()
        cl.containers.run(image=image_name, detach=True)
        print(f"Container '{container.name}' restarted successfully.")
    else:
        print(f"No container found with image '{image_name}'.")


class DiscordBot(discord.Client):
    def __init__(self, server):
        super().__init__(intents=intents)
        self.server = server

    async def on_ready(self):
        print(f'Bot is logged in as {self.user.name}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if not message.content.startswith('!'):
            return

        user_id = str(message.author.id)
        clients = self.server.get_connected_clients()

        # Connection messages.
        if message.content == '!connect':
            awaiting_connections = self.server.get_awaiting_connections()
            if user_id in awaiting_connections:
                if user_id in clients:
                    await message.author.send('User ID already connected from a client.')
                    clients[user_id].send(b'$user_already_logged_in')
                    return
                else:
                    try:
                        self.server.add_client(user_id)
                        response = f'!authorized_login {message.author.global_name} {user_id}'.encode()

                        new_clients = self.server.get_connected_clients()  # Updated Clients
                        new_clients[user_id].get_socket().send(response)
                        print(f'Received authorization from {user_id}')
                        await message.author.send(f'Connection authorized.')
                        print(f'Client connected.')
                        print(f'Active connections: {len(new_clients)}')
                    except OSError as e:
                        self.server.remove_client(awaiting_connections[user_id])
                        self.server.remove_client(clients[user_id])
                        await message.author.send(f'Client is not connected to server. Restart client and try again!')
                        print(f'Socket not found. Error: {e}')
            else:
                await message.author.send(f"You're not connected and cannot communicate with the Overwatch Queue Notifier at this time.")

        if user_id in clients:
            client_socket = clients[user_id].get_socket()
            if message.content == '!remindme':
                try:
                    client_socket.send(b'set_reminder_true')
                    await self.reminder_invitation(message.author)
                    clients[user_id].set_reminder(True)
                except Exception as e:
                    await message.author.send(f'Error communicating with client, make sure client is running. {e}')

            elif message.content == '!cancelreminder':
                try:
                    client_socket.send(b'set_reminder_false')
                    await self.cancel_reminder_invitation(message.author)
                    clients[user_id].set_reminder(False)
                except Exception as e:
                    await message.author.send(f'Error communicating with client, make sure client is running. {e}')

            elif message.content == '!cancelqueue':
                try:
                    client_socket.send(b'cancel_queue')
                except Exception as e:
                    await message.author.send(f'Error communicating with client, make sure client is running. {e}')

            elif message.content.startswith('!selecthero'):
                try:
                    parts = message.content.split(' ')[1::]
                    hero = " ".join(parts)
                    client_socket.send(f'!select_hero {hero}'.encode())
                except Exception as e:
                    await message.author.send(f'Error communicating with client, make sure client is running. {e}')

            elif message.content == '!exitgame':
                try:
                    client_socket.send(b'exit_game')
                except Exception as e:
                    await message.author.send(f'Error communicating with client, make sure client is running. {e}')

            elif message.content == '!commands':
                await self.send_commands(message.author)

            # Admin Zone
            if message.guild and message.author == message.guild.owner:
                if message.content == '!admin-cmd':
                    await self.announce_commands()
                elif message.content == '!admin-restart':
                    await restart_server()
                elif message.content == '!admin-connections':
                    await self.get_number_active_connections(message.guild.owner)

    async def send_user_message(self, user_id, message):
        user = self.get_user(int(user_id))
        if user:
            await user.send(message)
        else:
            print('Error - user not found. Make sure to provide the correct user id.')

    async def send_user_reminder(self, user_id):
        await self.send_user_message(user_id, f'<@{user_id}> Reminder - Invite your friend/s :)')

    async def notify_user_game_found(self, user_id, obj_mode=None, map_name=None):
        msg = f'<@{user_id}> Your match has been found!'
        if obj_mode is not None:
            msg += f" You're {obj_mode}"
        if map_name is not None:
            msg += f" {map_name}"
        msg += "."
        await self.send_user_message(user_id, msg)

    async def inform_user_select_hero_invalid(self, user_id):
        await self.send_user_message(user_id, "The hero you requested does not exist. Invalid input.")

    async def inform_user_select_hero_unavailable(self, user_id):
        await self.send_user_message(user_id, "The hero you requested is not available. It's either taken or it's not "
                                              "the role you've "
                                              "queued for.")

    async def inform_user_select_default_hero_unavailable(self, user_id):
        await self.send_user_message(user_id, "None of the default heroes are available for selection.")

    async def inform_user_cancel_queue_failure(self, user_id, errno):
        if errno == '1':
            await self.send_user_message(user_id, "Cannot cancel queue because you're in a match!")
        elif errno == '2':
            await self.send_user_message(user_id, "You're not in queue.")

    async def inform_user_cancel_queue_success(self, user_id):
        await self.send_user_message(user_id, "Queue has been cancelled.")

    async def inform_user_select_hero_success(self, user_id, hero=None):
        if hero is None:
            await self.send_user_message(user_id, "Hero has been selected.")
        else:  # If hero is not None, it means, a default hero was selected.
            await self.send_user_message(user_id, f'Default hero {hero} has been selected.')

    async def inform_user_select_hero_scheduled(self, user_id, hero):
        await self.send_user_message(user_id, f'{hero} has been scheduled for selection when a game is found.')

    async def inform_user_resolution_error(self, user_id):
        await self.send_user_message(user_id, "Your monitor's resolution does not match the specified Overwatch "
                                              "client resolution. This version currently does not support this "
                                              "feature.")

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

    async def send_socket_user_id_by_username(self, username):
        user = discord.utils.get(self.users, name=username)
        if user is not None:
            return user.id
        return None

    async def send_commands(self, user):
        # Send the formatted commands.
        await user.send(await self.format_commands())

    async def get_number_active_connections(self, user):
        clients = self.server.get_connected_clients()
        future_clients = self.server.get_awaiting_connections()
        await user.send(f'Current active connected clients: {len(clients) + len(future_clients)}')

    async def reminder_invitation(self, user):
        try:
            # Activate reminder bool in client.
            # If the reminder bool in client is already activated, send a different message.
            clients = self.server.get_connected_clients()
            if clients[str(user.id)].get_reminder():
                await user.send("Reminder is already set. I will remind you to invite your friend, after your game.")
            else:
                await user.send("I will remind you to invite your friend, after your game.")
        except Exception as e:
            print(f'Something went wrong with the reminder. {e}')

    async def cancel_reminder_invitation(self, user):
        try:
            # Deactivate reminder bool in client.
            # If the reminder bool in client is not activated, send a different message.
            clients = self.server.get_connected_clients()
            if clients[str(user.id)].get_reminder():
                clients[str(user.id)].set_reminder(False)
                await user.send("Reminder cancelled.")
            else:
                await user.send("There are no reminders scheduled.")
        except Exception as e:
            print(f'Something went wrong with the reminder. {e}')
