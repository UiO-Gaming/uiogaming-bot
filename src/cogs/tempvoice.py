from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks

from cogs.utils import embed_templates


class TempVoice(commands.Cog):
    """Allows users to create a temporary channel that will be deleted after 5 minutes of inactivity"""

    def __init__(self, bot: commands.Bot):
        """
        Parameters
        ----------
        bot (commands.Bot): The bot instance
        """

        self.bot = bot
        self.temp_vc_channels = {}
        self.check_temp_vc_channels.start()

    @commands.Cog.listener()
    async def on_voice_state_update(
        self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState
    ):
        """
        Listen for disconnects from the temporary voice channels
        """

        for channel in (before.channel, after.channel):
            if channel not in self.temp_vc_channels:
                continue

            if len(channel.members) == 0:
                self.temp_vc_channels[channel]["no_members_since"] = datetime.now()
                self.bot.logger.info(f"Temporary voice channel {channel} has no members. Will be deleted in 5 minutes")

    @tasks.loop(minutes=1)
    async def check_temp_vc_channels(self):
        """
        Check for temporary voice channels that have been inactive for 5 minutes
        """

        for channel, data in self.temp_vc_channels.copy().items():
            if not data["no_members_since"]:
                continue

            if (datetime.now() - data["no_members_since"]).total_seconds() >= 300:
                try:
                    await channel.delete(reason="tempvoice kanal inaktiv i 5 minutter")
                except discord.Forbidden:
                    self.bot.logger.error(f"Failed to delete temporary voice channel {channel}")
                else:
                    self.bot.logger.info(f"Deleted temporary voice channel {channel}")
                finally:
                    del self.temp_vc_channels[channel]

    @commands.cooldown(1, 300, commands.BucketType.guild)
    @app_commands.command(name="tempvoice")
    async def tempvoice(self, interaction: discord.Interaction, name: str, limit: int = 0):
        """
        Create a temporary voice channel

        Parameters
        ----------
        interaction (discord.Interaction): The interaction object
        name (str): The name of the channel
        limit (int): The user limit of the channel
        """

        # Get the UiO Gaming server's VC category. If the command is not invoked in that server it should still be fine
        # since the it will return None if not found.
        vc_category = interaction.guild.get_channel(747542544291987601)

        try:
            channel = await interaction.guild.create_voice_channel(
                name=name,
                user_limit=limit,
                category=vc_category,
                reason=f"tempvoice kommando av {interaction.user.name}",
            )
        except discord.Forbidden:
            self.bot.logger.error(f"Failed to create temporary voice channel in {interaction.guild}")
            return await interaction.response.send_message(
                embed=embed_templates.error_fatal(interaction, text="Jeg har ikke tilgang til å opprette en talekanal")
            )

        self.bot.logger.info(f"Created temporary voice channel {channel} in {interaction.guild}")

        self.temp_vc_channels[channel] = {"created": datetime.now(), "no_members_since": None}

        try:
            await interaction.user.move_to(channel)
        except discord.Forbidden:
            self.bot.logger.error(
                f"Failed to move {interaction.user} to temporary voice channel {channel}. Missing permissions"
            )
        except discord.HTTPException:
            self.bot.logger.error(
                f"Failed to move {interaction.user} to temporary voice channel {channel}. User not connected to voice"
            )

        await interaction.response.send_message(
            embed=embed_templates.success(
                interaction,
                text=f"{channel.mention} ble opprettet. Den vil bli slettet etter cirka 5 minutter uten aktivitet.",
            )
        )


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    await bot.add_cog(TempVoice(bot))
