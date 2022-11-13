from discord.ext import commands

import aiocron


class RepeatedMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        @aiocron.crontab("0 0 * * 5")
        async def fredag():
            guild = self.bot.get_guild(747542543750660178)
            channel = guild.get_channel(747542544291987597)
            await channel.send(
                "NU ÄR DET FREDAG!\n"
                + "https://cdn.discordapp.com/attachments/750052141346979850/851216786259181578/video0.mp4"
            )

        @aiocron.crontab("0 0 * * 1")
        async def mandag():
            guild = self.bot.get_guild(747542543750660178)
            channel = guild.get_channel(747542544291987597)
            await channel.send(
                "ENDELIG MANDAG!\n\n"
                + "https://cdn.discordapp.com/attachments/678396498089738250/862853827278929940/hvorfor_de_rike_br_spises.mp4"
            )

        @aiocron.crontab("0 0 1 1 *")
        async def new_year():
            guild = self.bot.get_guild(747542543750660178)
            channel = guild.get_channel(747542544291987597)
            await channel.send(
                "GODT NYTTÅR!\n\nNå, meld dere inn i UiO Gaming igjen <:ThisIsAThreat:874998234072903710>\nhttps://youtu.be/5qXkEvHrZ-0"
            )


async def setup(bot):
    await bot.add_cog(RepeatedMessages(bot))
