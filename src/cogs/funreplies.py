from discord.ext import commands


class FunReplies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def react(self, message):
        if message.author.bot:
            return

        if ' borgerlønn ' in message.content.lower():
            await message.channel.send('<@267415183931080715> DE SNAKKER OM BORGERLØNN')

        elif ' olof palme ' in message.content.lower():
            await message.channel.send('Jeg vet hvem som drepte Olof Palme 👀')


def setup(bot):
    bot.add_listener(FunReplies(bot).react, 'on_message')
    bot.add_cog(FunReplies(bot))
