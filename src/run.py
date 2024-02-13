import codecs
from os import listdir
from time import time

import discord
import psycopg2
import yaml
from discord.ext import commands

from logger import BotLogger

UIO_GAMING_GUILD_ID = 747542543750660178
DATABASE_RELIANT_COGS = {
    "birthday.py",
    "gullkorn.py",
    "mc_whitelist.py",
    "social_credit.py",
    "streak.py",
    "user_facts.py",
    "word_cloud.py",
}
SANITY_RELIANT_COGS = {"website_events.py"}


# Load config file
with codecs.open("./src/config/config.yaml", "r", encoding="utf8") as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)


class Bot(commands.Bot):
    """UiO Gaming Bot"""

    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(config["bot"]["prefix"]),
            case_insensitive=True,
            intents=discord.Intents.all(),
            allowed_mentions=discord.AllowedMentions(everyone=False),
        )

        self.logger = BotLogger().logger  # Initialize logger

        self.guild_id = config.get("dev_guild", UIO_GAMING_GUILD_ID)

        # Connect to database
        # We assume the config file is valid and contains the needed keys, even if they are empty
        db = config.get("database")

        for db_credential in db.values():
            if not db_credential:
                self.db_connection = None
                self.logger.warning(
                    f"No database credentials specified. Disabling db reliant cogs:\n{DATABASE_RELIANT_COGS}"
                )
                break
        else:
            self.db_connection = psycopg2.connect(
                host=db["host"],
                dbname=db["dbname"],
                user=db["username"],
                password=db["password"],
            )
            self.db_connection.autocommit = True

        for sanity_credential in config.get("sanity").values():
            if not sanity_credential:
                self.has_sanity_credentials = False
                self.logger.warning(
                    f"No Sanity credentials specified. Disabling sanity reliant cogs\n{SANITY_RELIANT_COGS}"
                )
                break
            else:
                self.has_sanity_credentials = True

        # Fetch misc config values
        self.mc_rcon_password = config["minecraft"]["rcon_password"]
        self.sanity = config["sanity"]
        self.presence = config["bot"].get("presence", {})
        self.emoji = config.get("emoji", {})
        self.misc = config.get("misc", {})
        self.config_mode = config.get("config_mode")

    async def setup_hook(self):
        cog_files = listdir("./src/cogs")

        if self.db_connection is None:
            cog_files = set(cog_files) - DATABASE_RELIANT_COGS
        if not self.has_sanity_credentials:
            cog_files = set(cog_files) - SANITY_RELIANT_COGS

        # Load cogs
        for file in cog_files:
            if file.endswith(".py"):
                name = file[:-3]
                await bot.load_extension(f"cogs.{name}")

        # Sync slash commands to Discord
        if self.config_mode == "prod":
            await self.tree.sync()
        else:
            self.tree.copy_global_to(guild=discord.Object(id=self.guild_id))
            await self.tree.sync(guild=discord.Object(id=self.guild_id))


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
        activity=discord.Activity(type=activity_type, name=bot.presence["message"]), status=status_type
    )


bot.run(config["bot"]["token"], reconnect=True, log_handler=None)
