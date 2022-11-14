import aiocron
from discord.ext import commands


class RepeatedMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        uio_gaming = self.bot.get_guild(747542543750660178)
        self.uiog_general = uio_gaming.get_channel(747542544291987597)

        @aiocron.crontab("0 0 * * 5")
        async def fredag():
            await self.uiog_general.send(
                "NU ÄR DET FREDAG!\n" + \
                "https://cdn.discordapp.com/attachments/750052141346979850/851216786259181578/video0.mp4"
            )

        @aiocron.crontab("0 0 * * 1")
        async def mandag():
            await self.uiog_general.send(
                "ENDELIG MANDAG!\n\n" + \
                "https://cdn.discordapp.com/attachments/678396498089738250/862853827278929940/hvorfor_de_rike_br_spises.mp4"
            )

        @aiocron.crontab("0 0 1 1 *")
        async def new_year():
            await self.uiog_general.send(
                "GODT NYTTÅR!\n\nNå, meld dere inn i UiO Gaming igjen <:ThisIsAThreat:874998234072903710>"
            )


async def setup(bot):
    await bot.add_cog(RepeatedMessages(bot))
