import re
from datetime import datetime

import discord
from discord.ext import commands


class FunReplies(commands.Cog):
    """Reply to messages that trigger certain key words/phrases"""

    def __init__(self, bot: commands.Bot):
        """
        Parameters
        ----------
        bot (commands.Bot): The bot instance
        """

        self.bot = bot

        # Cooldowns for trigger words
        #
        # This is kind of a shitty way to do it but I'm too lazy to implement anything good right now
        self.cooldown_seconds = 120
        initial_datetime = datetime(
            2000, 9, 11
        )  # Set initial datetime far in the past to allow triggering right after boot
        self.previous_invokations = {
            "borgerlønn": initial_datetime,
            "olof palme": initial_datetime,
            "lesgo": initial_datetime,
            "yeet": initial_datetime,
            "drikke": initial_datetime,
            "sivert": initial_datetime,
            "spam": initial_datetime,
        }

    async def reply_to_triggers(self, message: discord.Message):
        """
        Replies to messages that trigger certain key words/phrases

        Parameters
        ----------
        message (discord.Message): Message object to check for triggers to
        """

        if message.author.bot:
            return

        message_content = message.content.lower()

        if re.search(r"(^|\W)olof palme(\W|$)", message_content, flags=re.IGNORECASE):
            if (datetime.now() - self.previous_invokations["olof palme"]).seconds > self.cooldown_seconds:
                await message.reply("Jeg vet hvem som drepte Olof Palme 👀")
                self.previous_invokations["olof palme"] = datetime.now()

        elif re.search(r"(\W|\s)*le+s+go+(\s|\W)*", message_content):
            if (datetime.now() - self.previous_invokations["lesgo"]).seconds > self.cooldown_seconds:
                await message.reply(
                    "https://cdn.discordapp.com/attachments/750052141346979850/"
                    + "824764933513281596/3xhpwbakz2361.png"
                )
                self.previous_invokations["lesgo"] = datetime.now()

        elif re.search(r"(^|\W)+ye+et($|\W)+", message_content, flags=re.IGNORECASE):
            if (datetime.now() - self.previous_invokations["yeet"]).seconds > self.cooldown_seconds:
                await message.reply("<:Nei:826593267642662912>")
                self.previous_invokations["yeet"] = datetime.now()

        elif re.search(r"(^|\W)skal? aldri drikke?[\w\s]*igjen($|\W)+", message_content, flags=re.IGNORECASE):
            if (datetime.now() - self.previous_invokations["drikke"]).seconds > self.cooldown_seconds:
                await message.reply(":billed_cap:")
                self.previous_invokations["drikke"] = datetime.now()

        elif re.search(r"(^|\W)(jeg?|(e|æ)(g|j)?|i) er? sivert arntzen($|\W)+", message_content, flags=re.IGNORECASE):
            if (datetime.now() - self.previous_invokations["sivert"]).seconds > self.cooldown_seconds:
                await message.reply("Nei, jeg er Sivert Arntzen!")
                self.previous_invokations["sivert"] = datetime.now()

        elif re.search(r"(^|\W)spam($|\W)+", message_content, flags=re.IGNORECASE):
            if (datetime.now() - self.previous_invokations["spam"]).seconds > self.cooldown_seconds:
                await message.reply("https://www.youtube.com/watch?v=zLih-WQwBSc")
                self.previous_invokations["spam"] = datetime.now()


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    bot.add_listener(FunReplies(bot).reply_to_triggers, "on_message")
    await bot.add_cog(FunReplies(bot))
