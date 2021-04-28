from discord.ext import commands

import re


class FunReplies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def react(self, message):
        if message.author.bot:
            return

        if re.findall(r'(^|\W)borgerlønn(\W|$)', message.clean_content.lower()) != []:
            await message.channel.send('<@267415183931080715> DE SNAKKER OM BORGERLØNN')

        elif re.findall(r'(^|\W)olof palme(\W|$)', message.clean_content.lower()) != []:
            await message.channel.send('Jeg vet hvem som drepte Olof Palme 👀')

        #  The Ultimate spaghetti
        elif (
            re.match(r'(\W|\s)*lesgo{1}(\s|\W)*', message.clean_content.lower()) or
            message.clean_content.lower() == 'lesgo'
        ):
            await message.channel.send('https://cdn.discordapp.com/attachments/750052141346979850/' +
                                       '824764933513281596/3xhpwbakz2361.png')


def setup(bot):
    bot.add_listener(FunReplies(bot).react, 'on_message')
    bot.add_cog(FunReplies(bot))
