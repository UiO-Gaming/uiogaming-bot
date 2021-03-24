import discord
from discord.ext import commands
import discord

from datetime import datetime

from cogs.utils import embed_templates


class Mod(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    @commands.command()
    async def hackban(self, ctx, brukerid, *, melding=None):
        """
        Bannlys en bruker før de i det hele tatt har blitt med i serveren
        """

        try:
            brukerid = int(brukerid)
        except ValueError:
            embed = embed_templates.error_warning(ctx, text='Du må gi meg en bruker-id')
            return await ctx.send(embed=embed)

        user = discord.Object(id=brukerid)

        for banentry in await ctx.guild.bans():
            if banentry.user.id == user.id:
                embed = embed_templates.error_warning(ctx, text='Denne brukeren er allerede bannlyst fra serveren!')
                return await ctx.send(embed=embed)

        if melding is None:
            melding = 'Ingen grunn angitt'

        date = datetime.now().strftime('%d. %b. %Y - %H:%M')

        try:
            await ctx.guild.ban(
                user,
                reason=f'{date} | {ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id}): {melding}'
            )
        except discord.errors.NotFound:
            embed = embed_templates.error_warning(ctx, text='Bruker finnes ikke!')
            return await ctx.send(embed=embed)

        user_object = self.bot.get_user(brukerid)

        embed = discord.Embed(color=discord.Color.red(), title='🔨 Bruker utestengt!')
        if melding != 'Ingen grunn angitt':
            embed.description = f'`{melding}`'
        if user_object:
            user = user_object
            embed.set_thumbnail(url=user.avatar_url)
            embed.set_author(name=f'{user.name}#{user.discriminator}', icon_url=user.avatar_url)
            embed.add_field(name='Bruker', value=f'{user.name}#{user.discriminator}\n{user.mention}', inline=False)
        else:
            embed.add_field(name='Bruker', value=f'`{user.id}`', inline=False)
        embed.add_field(name='Av', value=f'{ctx.author.name}#{ctx.author.discriminator}\n{ctx.author.mention}')
        embed = embed_templates.default_footer(ctx, embed)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Mod(bot))
