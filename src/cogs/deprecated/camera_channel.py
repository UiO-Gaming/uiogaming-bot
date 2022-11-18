from discord.ext import commands

import asyncio


class CameraChannel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def on_voice_state_update(self, member, before, after):
        if after.channel is None:
            return

        if member.voice.channel.id != 817125310491131949:
            return

        if not member.voice.self_video:
            await asyncio.sleep(10)
            if not member.voice.self_video and member.voice.channel.id == 817125310491131949:
                await member.move_to(channel=None)


async def setup(bot: commands.Bot):
    #bot.add_listener(CameraChannel(bot).on_voice_state_update, 'on_voice_state_update')
    #await bot.add_cog(CameraChannel(bot))
    pass
