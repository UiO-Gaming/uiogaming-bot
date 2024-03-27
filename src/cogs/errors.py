import traceback

import discord
from discord import app_commands
from discord.ext import commands

from cogs.utils import embed_templates


class Errors(commands.Cog):
    """Error handlers for commands"""

    def __init__(self, bot: commands.Bot):
        """
        Parameters
        ----------
        bot (commands.Bot): The bot instance
        """

        self.bot = bot
        bot.tree.on_error = self.on_app_command_error  # Set error handler for slash commands

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        """
        Logs prefix command execution metadata

        Parameters
        ----------
        ctx (commands.Context): Context object
        """

        self.bot.logger.info(
            f'{"❌ " if ctx.command_failed else "✔ "} {ctx.command} | '
            + f"{ctx.author.name} ({ctx.author.id}) | "
            + f"{ctx.guild.id}-{ctx.channel.id}-{ctx.message.id}"
        )

    @commands.Cog.listener()
    async def on_app_command_completion(
        self, interaction: discord.Interaction, command: app_commands.Command | app_commands.ContextMenu
    ):
        """
        Logs slash command execution metadata

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        command (app_commands.Command | app_commands.ContextMenu): Command object
        """

        self.bot.logger.info(
            f'{"❌ " if interaction.command_failed else "✔ "} {command.name} | '
            + f"{interaction.user.name} ({interaction.user.id}) | "
            + f"{interaction.guild_id}-{interaction.channel_id}-{interaction.id}"
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """
        Handle prefix command errors

        Parameters
        ----------
        ctx (commands.Context): Context object
        error (commands.CommandError): Eror context object
        """

        # Reset cooldown if command throws AttributeError
        try:
            self.bot.get_command(f"{ctx.command}").reset_cooldown(ctx)
        except AttributeError:
            pass

        # Ignore command's own error handling
        if hasattr(ctx.command, "on_error"):
            return

        # Ignored errors
        ignored = commands.CommandNotFound
        error = getattr(error, "original", error)
        if isinstance(error, ignored):
            return

        send_help = (commands.MissingRequiredArgument, commands.TooManyArguments, commands.BadArgument)
        if isinstance(error, send_help):
            self.bot.get_command(f"{ctx.command}").reset_cooldown(ctx)
            return await ctx.send_help(ctx.command)

        elif isinstance(error, commands.BotMissingPermissions):
            permissions = ", ".join(error.missing_permissions)
            text = "Jeg mangler følgende tillatelser:\n\n" + f"```\n{permissions}\n```"
            return await ctx.reply(text)

        elif isinstance(error, commands.MissingPermissions):
            permissions = ", ".join(error.missing_permissions)
            text = "Du mangler følgende tillatelser\n\n" + f"```\n{permissions}\n```"
            return await ctx.reply(text)

        elif isinstance(error, commands.NotOwner):
            text = "Bare boteieren kan gjøre dette"
            return await ctx.reply(text)

        elif isinstance(error, commands.CommandOnCooldown):
            text = "Kommandoen har nettopp blitt brukt\n" + f"Prøv igjen om `{error.retry_after:.1f}` sekunder."
            return await ctx.reply(text)

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                text = "Denne kommandoen kan bare utføres i servere"
                return await ctx.reply(text)
            except discord.errors.Forbidden:  # Thrown if bot is blocked by the user or if the user has closed their DMs
                self.bot.logger.info("DM Blocked!")

        elif isinstance(error, commands.DisabledCommand):
            self.bot.logger.info("Command disabled. Ignoring")

        elif isinstance(error, commands.CheckFailure):
            self.bot.logger.info("CheckFailure")

        embed = embed_templates.error_fatal(ctx, text="En ukjent feil oppstod!")
        await ctx.reply(embed=embed)

        # Log full exception to file
        self.bot.logger.error("".join(traceback.format_exception(type(error), error, error.__traceback__)))

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """
        Handle slash command errors

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        error (app_commands.AppCommandError): Eror context object
        """

        # TODO: add support for defered interactions

        # Log command usage, just in case
        await self.on_app_command_completion(interaction, interaction.command)

        if isinstance(error, app_commands.BotMissingPermissions):
            permissions = ", ".join(error.missing_permissions)
            embed = embed_templates.error_warning(
                interaction, text="Jeg mangler følgende tillatelser:\n\n" + f"```\n{permissions}\n```"
            )

        elif isinstance(error, app_commands.MissingPermissions):
            permissions = ", ".join(error.missing_permissions)
            embed = embed_templates.error_warning(
                interaction, text="Du mangler følgende tillatelser\n\n" + f"```\n{permissions}\n```"
            )

        # TODO: figure this shit out. app_commands does not support this check
        # elif isinstance(error, app_commands.NotOwner):
        #     embed = embed_templates.error_fatal(interaction, text='Bare boteieren kan gjøre dette')
        #     return await interaction.response.send_message(embed=embed)

        elif isinstance(error, app_commands.CommandOnCooldown):
            embed = embed_templates.error_warning(
                interaction,
                text="Kommandoen har nettopp blitt brukt\n" + f"Prøv igjen om `{error.retry_after:.1f}` sekunder.",
            )

        else:
            embed = embed_templates.error_fatal(interaction, text="En ukjent feil oppstod!")

        if interaction.response.is_done():
            await interaction.followup.send(embed=embed)
        else:
            await interaction.response.send_message(embed=embed)

        # Log full exception to file
        self.bot.logger.error("".join(traceback.format_exception(type(error), error, error.__traceback__)))


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    await bot.add_cog(Errors(bot))
