import random
import re
from datetime import datetime

import discord
from discord.ext import commands


class FunReplies(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Cooldowns for trigger words
        #
        # This is kind of a shitty way to do it but I'm too lazy to implement anything good right now
        self.cooldown_seconds = 120
        initial_datetime = datetime(2000, 9, 11)  # Set initial datetime far in the past to allow triggering right after boot
        self.previous_invokations = {
            'borgerlønn': initial_datetime,
            'olof palme': initial_datetime,
            'lesgo': initial_datetime,
            'neuf': initial_datetime,
            'yeet': initial_datetime
        }

    async def reply_to_triggers(self, message: discord.Message):
        """Replies to messages that trigger certain key words/phrases"""
        if message.author.bot:
            return

        message_content = message.content.lower()

        if re.search(r'(^|\W)borgerlønn(\W|$)', message_content, flags=re.IGNORECASE):
            if (datetime.now() - self.previous_invokations['borgerlønn']).seconds > self.cooldown_seconds:
                await message.channel.send('<@267415183931080715> DE SNAKKER OM BORGERLØNN')
                self.previous_invokations['borgerlønn'] = datetime.now()

        elif re.search(r'(^|\W)olof palme(\W|$)', message_content, flags=re.IGNORECASE):
            if (datetime.now() - self.previous_invokations['olof palme']).seconds > self.cooldown_seconds:
                await message.channel.send('Jeg vet hvem som drepte Olof Palme 👀')
                self.previous_invokations['olof palme'] = datetime.now()

        elif re.search(r'(\W|\s)*le+s+go+(\s|\W)*', message_content):
            if (datetime.now() - self.previous_invokations['lesgo']).seconds > self.cooldown_seconds:
                await message.channel.send('https://cdn.discordapp.com/attachments/750052141346979850/' +
                                           '824764933513281596/3xhpwbakz2361.png')
                self.previous_invokations['lesgo'] = datetime.now()

        elif re.search(r'^((er det|hvor)\s+)*(noen|folk|mange)\s+på\s+(rommet|neuf|kontoret)\?*$', message_content, flags=re.IGNORECASE):
            if (datetime.now() - self.previous_invokations['neuf']).seconds > self.cooldown_seconds:
                # Choose a random user to ping
                pingable = ["<@554977854971183125>", "<@276061121776058370>"]
                to_be_pinged = random.choice(pingable)
                await message.channel.send(f'Ja, {to_be_pinged} bor der')

                self.previous_invokations['neuf'] = datetime.now()

        elif re.search(r'(^|\W)+ye+et($|\W)+', message_content, flags=re.IGNORECASE):
            if (datetime.now() - self.previous_invokations['yeet']).seconds > self.cooldown_seconds:
                await message.channel.send('<:Nei:826593267642662912>')
                self.previous_invokations['yeet'] = datetime.now()


async def setup(bot: commands.Bot):
    bot.add_listener(FunReplies(bot).reply_to_triggers, 'on_message')
    await bot.add_cog(FunReplies(bot))
