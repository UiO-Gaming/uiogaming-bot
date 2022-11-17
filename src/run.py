import codecs
from os import listdir
from time import time

import discord
from discord.ext import commands
import psycopg2
import yaml

from logger import BotLogger


# Load config file
with codecs.open("./src/config/config.yaml", "r", encoding="utf8") as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)


class Bot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or(config["bot"]["prefix"]),
            case_insensitive=True,
            intents=discord.Intents.all()
        )

        self.logger = BotLogger().logger  # Initialize logger

        # Connect to database
        db = config.get("database", {})
        self.db_connection = psycopg2.connect(
            host=db["host"],
            dbname=db["dbname"],
            user=db["username"],
            password=db["password"],
        )

        # Fetch misc config values
        self.mc_rcon_password = config["minecraft"]["rcon_password"]
        self.presence = config["bot"].get("presence", {})
        self.api_keys = config.get("api", {})
        self.emoji = config.get("emoji", {})
        self.misc = config.get("misc", {})
        self.config_mode = config.get("mode")

    async def setup_hook(self) -> None:
        # Load cogs
        for file in listdir("./src/cogs"):
            if file.endswith(".py"):
                name = file[:-3]
                await bot.load_extension(f"cogs.{name}")

        # Sync slash commands to Discord
        if self.config_mode == 'prod':
            await self.tree.sync()
        else:
            self.tree.copy_global_to(guild=discord.Object(id=412646636771344395))
            await self.tree.sync(guild=discord.Object(id=412646636771344395))


# Create bot instance
bot = Bot()


@bot.event
async def on_ready():
    if not hasattr(bot, "uptime"):
        bot.uptime = time()

    # Print bot info
    print(f"Username:        {bot.user.name}")
    print(f"ID:              {bot.user.id}")
    print(f"Version:         {discord.__version__}")
    print("." * 50 + "\n")

    # Set initial presence
    # Presence status
    status_types = {
        "online": discord.Status.online,
        "dnd": discord.Status.dnd,
        "idle": discord.Status.idle,
        "offline": discord.Status.offline,
    }
    status_type = status_types.get(bot.presence["type"].lower(), discord.Status.online)

    # Presence actitivity
    activities = {"playing": 0, "listening": 2, "watching": 3}
    activity_type = activities.get(bot.presence["activity"].lower(), 0)

    await bot.change_presence(
        activity=discord.Activity(type=activity_type, name=bot.presence["message"]),
        status=status_type
    )


bot.run(config["bot"]["token"], reconnect=True, log_handler=None)
