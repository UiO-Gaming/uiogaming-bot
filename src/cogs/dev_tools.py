import asyncio
from os import listdir
import requests

import discord
from discord.ext import commands

from cogs.utils import embed_templates


class DevTools(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.is_owner()
    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def custommsg(self, ctx: commands.Context, channel: int, *text: tuple[str]):
        """Send a message to a specified channel"""
        # Send message to the requested channel
        channel = self.bot.get_channel(channel)
        custommessage = ' '.join(text)
        await channel.send(custommessage)

        # Send confirmation message to the invoker
        embed = discord.Embed(color=ctx.me.color)
        embed.add_field(name='Sent', value=custommessage)
        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.command()
    async def changepresence(self, ctx: commands.Context, activity_type: str, message: str, status_type: str):
        """Changes the bot's presence status"""
        activities = {
            'playing': 0,
            'listening': 2,
            'watching': 3
        }
        activity_type = activities.get(activity_type, 0)

        status_types = {
            'online': discord.Status.online,
            'dnd': discord.Status.dnd,
            'idle': discord.Status.idle,
            'offline': discord.Status.offline
        }
        status_type = status_types.get(status_type, discord.Status.online)

        await self.bot.change_presence(
            status=status_type,
            activity=discord.Activity(type=activity_type, name=message)
        )
        embed = discord.Embed(color=ctx.me.color, description='Endret Presence!')
        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    @commands.command()
    async def leave(self, ctx: commands.Context, *guild_id: int):
        """Leaves a specified guild"""
        # If no guild id is specified, leave the current guild
        guild_id = guild_id if guild_id else ctx.guild.id

        # Get guild
        try:
            guild = await self.bot.fetch_guild(guild_id)
        except discord.errors.Forbidden:
            embed = embed_templates.error_fatal(ctx, text='Bot is not a member of this guild')
            return await ctx.send(embed=embed)

        # Send confirmation message for leaving
        confirmation_msg = await ctx.send(f'Do you want to leave {guild.name} (`{guild.id}`)?')
        await confirmation_msg.add_reaction('✅')

        # Check confirmation
        def comfirm(reaction, user):
            return user == ctx.author and str(reaction.emoji) == '✅'

        try:
            await self.bot.wait_for('reaction_add', timeout=15.0, check=comfirm)
        except asyncio.TimeoutError:
            await ctx.message.delete()
            await confirmation_msg.delete()
        else:
            await guild.leave()
            try:
                embed = discord.Embed(color=ctx.me.color, description='Guild left!')
                await ctx.send(embed=embed)
            except discord.errors.Forbidden:
                pass

    @commands.is_owner()
    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def publicip(self, ctx: commands.Context):
        """Sends WAN IP-address. inb4 I leak my IP-address"""
        data = requests.get('https://wtfismyip.com/json', timeout=10).json()
        ip = data['YourFuckingIPAddress']
        location = data['YourFuckingLocation']
        isp = data['YourFuckingISP']

        embed = discord.Embed(color=ctx.me.color)
        embed.add_field(name='WAN IP-address', value=f'{ip}\n{location}\n{isp}')
        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.bot_has_permissions(embed_links=True)
    @commands.group()
    async def cogs(self, ctx: commands.Context):
        """Cog management commands"""
        if not ctx.invoked_subcommand:
            await ctx.send_help(ctx.command)

    @cogs.command()
    async def unload(self, ctx: commands.Context, cog: str):
        """Disables a specified cog"""
        for file in listdir('./src/cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                if name == cog:
                    await self.bot.unload_extension(f'cogs.{name}')
                    embed = discord.Embed(color=ctx.me.color, description=f'{cog} has been disabled')
                    return await ctx.send(embed=embed)

        embed = embed_templates.error_fatal(ctx, text=f'{cog} does not exist')
        await ctx.send(embed=embed)

    @cogs.command()
    async def load(self, ctx: commands.Context, cog: str):
        """Enables a speicifed cog"""
        for file in listdir('./src/cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                if name == cog:
                    await self.bot.load_extension(f'cogs.{name}')
                    embed = discord.Embed(color=ctx.me.color, description=f'{cog} loaded')
                    return await ctx.send(embed=embed)

        embed = embed_templates.error_fatal(ctx, text=f'{cog} does not exist')
        await ctx.send(embed=embed)

    @cogs.command()
    async def reload(self, ctx: commands.Context, cog: str):
        """Reloads a specified cog"""
        for file in listdir('./src/cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                if name == cog:
                    await self.bot.reload_extension(f'cogs.{name}')
                    embed = discord.Embed(color=ctx.me.color, description=f'{cog} has been reloaded')
                    return await ctx.send(embed=embed)

        embed = embed_templates.error_fatal(ctx, text=f'{cog} does not exist')
        await ctx.send(embed=embed)

    @cogs.command()
    async def reloadunloaded(self, ctx: commands.Context):
        """Reloads all cogs, including previously disabled ones"""
        # Unload all cogs
        for file in listdir('./src/cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                await self.bot.unload_extension(f'cogs.{name}')

        # Load all cogs
        for file in listdir('./src/cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                await self.bot.load_extension(f'cogs.{name}')

        embed = discord.Embed(color=ctx.me.color, description='Reloaded all cogs')
        await ctx.send(embed=embed)

    @cogs.command()
    async def reloadall(self, ctx: commands.Context):
        """Reloads all previously enabled cogs"""
        for file in listdir('./src/cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                await self.bot.reload_extension(f'cogs.{name}')

        embed = discord.Embed(color=ctx.me.color, description='Reloaded all previously enabled cogs')
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(DevTools(bot))
