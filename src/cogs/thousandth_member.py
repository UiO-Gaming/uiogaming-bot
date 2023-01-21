import discord
from discord.ext import commands


class ThousanthMember(commands.Cog):
    """Greet the thousandth member of the server"""

    def __init__(self, bot: commands.Bot):
        """
        Parameters
        ----------
        bot (commands.Bot): The bot instance
        """

        self.bot = bot
        self.announced = False

    async def on_member_join(self, member: discord.Member):
        """
        Replies to messages that trigger certain key words/phrases

        Parameters
        ----------
        member (discord.Member): The member that joined
        """

        if member.guild.member_count == 1000 and not self.announced:
            self.announced = True
            channel = member.guild.get_channel(747542544291987597)
            await channel.send("Vi er nå 1000 brukere på serveren! <:LETSFUCKINGGOOOOOO:814477215868649492>")

async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    bot.add_listener(ThousanthMember(bot).on_member_join, 'on_member_join')
    await bot.add_cog(ThousanthMember(bot))

