import discord
from discord import app_commands
from discord.ext import commands

from cogs.utils import discord_utils, embed_templates


class Streak(commands.Cog):
    """Cog for handling message streaks on the server"""

    def __init__(self, bot: commands.Bot):
        """
        Parameters
        ----------
        bot (commands.Bot): The bot instance
        """

        self.bot = bot
        self.cursor = self.bot.db_connection.cursor()
        self.init_db()

    def init_db(self):
        """Create the necessary tables for the streak cog to work."""

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS streak (
                discord_id BIGINT PRIMARY KEY,
                streak INT NOT NULL DEFAULT 0,
                last_post timestamp NOT NULL
            );
            """
        )

    @commands.command()


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    bot.add_listener(Streak(bot).gullkorn_listener, 'on_message')
    await bot.add_cog(Streak(bot))
