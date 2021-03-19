from discord.ext import commands
import discord

from codecs import open
import yaml

from os import listdir
import locale
from time import time


locale.setlocale(locale.LC_ALL, '')

with open('./src/config/config.yaml', 'r', encoding='utf8') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

intents = discord.Intents.default()
intents.members = True
intents.presences = True


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(config['bot']['prefix']),
                         case_insensitive=True, intents=intents)

        self.prefix = config['bot']['prefix']
        self.presence = config['bot'].get('presence', {})

        self.api_keys = config.get('api', {})

        self.emoji = config.get('emoji', {})
        self.misc = config.get('misc', {})


bot = Bot()


activities = {
    'playing': 0,
    'listening': 2,
    'watching': 3
}
if bot.presence['activity'].lower() in activities:
    activity_type = activities[bot.presence['activity'].lower()]
else:
    activity_type = 0

status_types = {
    'online': discord.Status.online,
    'dnd': discord.Status.dnd,
    'idle': discord.Status.idle,
    'offline': discord.Status.offline
}
if bot.presence['type'].lower() in status_types:
    status_type = status_types[bot.presence['type'].lower()]
else:
    status_type = discord.Status.online


@bot.event
async def on_ready():
    if not hasattr(bot, 'uptime'):
        bot.uptime = time()

    for file in listdir('./src/cogs'):
        if file.endswith('.py'):
            name = file[:-3]
            bot.load_extension(f'cogs.{name}')

    print(f'Username:        {bot.user.name}')
    print(f'ID:              {bot.user.id}')
    print(f'Version:         {discord.__version__}')
    print('.' * 50 + '\n')
    await bot.change_presence(
        activity=discord.Activity(type=activity_type, name=bot.presence['message']),
        status=status_type
    )


bot.run(config['bot']['token'], bot=True, reconnect=True)
