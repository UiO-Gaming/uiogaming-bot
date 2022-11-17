import aiocron
from discord.ext import commands


class RepeatedMessages(commands.Cog):
    """Send messages at specific points of time"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.uiog_server = self.bot.get_guild(747542543750660178)

        @aiocron.crontab('0 0 * * 5')
        async def fredag():
            """Sends a message on Friday at 00:00"""

            channel = await self.uiog_server.fetch_channel(747542544291987597)
            await channel.send(
                'NU ÄR DET FREDAG!\n' +
                'https://cdn.discordapp.com/attachments/750052141346979850/851216786259181578/video0.mp4'
            )

        @aiocron.crontab('0 0 * * 1')
        async def mandag():
            """Sends a message on Monday at 00:00"""

            channel = await self.uiog_server.fetch_channel(747542544291987597)
            await channel.send(
                'ENDELIG MANDAG!\n\n' +
                'https://cdn.discordapp.com/attachments/678396498089738250/862853827278929940/hvorfor_de_rike_br_spises.mp4'
            )

        @aiocron.crontab('0 0 1 1 *')
        async def new_year():
            """Sends a message on New Year's Day at 00:00"""

            channel = await self.uiog_server.fetch_channel(747542544291987597)
            await channel.send(
                'GODT NYTTÅR!\n\nNå, meld dere inn i UiO Gaming igjen <:ThisIsAThreat:874998234072903710>'
            )


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    await bot.add_cog(RepeatedMessages(bot))
