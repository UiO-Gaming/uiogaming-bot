import asyncio
import random

import aiocron
from discord.ext import commands


class RepeatedMessages(commands.Cog):
    """Send messages at specific points of time"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.general_channel = 747542544291987597

        # Yes we have to have these inside the constructor
        # Probably could've implemented the waiting functions myself
        # but that sounds like work and I don't like to work

        @aiocron.crontab("0 0 * * 5")
        async def fredag():
            """
            Sends a message on Friday at 00:00
            """

            guild = self.bot.get_guild(self.bot.UIO_GAMING_GUILD_ID)
            channel = guild.get_channel(self.general_channel)

            videos = [
                "https://cdn.discordapp.com/attachments/750052141346979850/851216786259181578/video0.mp4",
                "https://cdn.discordapp.com/attachments/878368386671849582/1043133798512070666/durk_durk_fredag.mp4",
                "https://cdn.discordapp.com/attachments/878368386671849582/1043133820079177808/finfredag.png",
                "https://cdn.discordapp.com/attachments/878368386671849582/1043133832360120340/fredag_1.mp4",
                "https://cdn.discordapp.com/attachments/878368386671849582/1043133914316816424/shutup_friday.mp4",
                "https://cdn.discordapp.com/attachments/878368386671849582/1043133934915031040/uboot_fredag.mp4",
                "https://cdn.discordapp.com/attachments/747542544291987597/1037864063901909043/fredag_whole_store4.mp4",
                "https://cdn.discordapp.com/attachments/747542544291987597/1037864293154168863/fredag_wholesome.mp4",
                "https://cdn.discordapp.com/attachments/747542544291987597/1055835511366877244/received_914083109578582.gif",
                "https://cdn.discordapp.com/attachments/747542544291987597/1037866542328713256/fredag_i_norge.mp4",
            ]

            await asyncio.sleep(1)  # try to mitigate the same video being queued two weeks in a row
            video = random.choice(videos)

            await channel.send("NU ÄR DET FREDAG!\n" + video)

        @aiocron.crontab("0 0 * * 1")
        async def mandag():
            """
            Sends a message on Monday at 00:00
            """

            guild = self.bot.get_guild(self.bot.UIO_GAMING_GUILD_ID)
            channel = guild.get_channel(self.general_channel)
            await channel.send(
                "ENDELIG MANDAG!\n\n"
                # + "https://cdn.discordapp.com/attachments/678396498089738250/862853827278929940/hvorfor_de_rike_br_spises.mp4"  # noqa: E501
                + "https://cdn.discordapp.com/attachments/678396498089738250/1168644637687283762/Snapchat-1787493720.mp4"  # noqa: E501
            )

        @aiocron.crontab("0 0 1 1 *")
        async def new_year():
            """
            Sends a message on New Year's Day at 00:00
            """

            guild = self.bot.get_guild(self.bot.UIO_GAMING_GUILD_ID)
            channel = guild.get_channel(self.general_channel)
            await channel.send(
                "GODT NYTTÅR!\n\nNå, meld dere inn i UiO Gaming igjen <:ThisIsAThreat:874998234072903710>"
            )


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    await bot.add_cog(RepeatedMessages(bot))
