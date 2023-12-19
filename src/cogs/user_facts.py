import discord
from discord import app_commands
from discord.ext import commands

from cogs.utils import discord_utils
from cogs.utils import embed_templates
from cogs.utils import misc_utils


class UserFacts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cursor = self.bot.db_connection.cursor()
        self.init_db()

    def init_db(self):
        """Create the necessary tables for the birthday cog to work"""

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_facts (
                discord_id BIGINT PRIMARY KEY,
                mbti CHAR(4),
                height INT
            );
            """
        )

    height_group = app_commands.Group(name="høyde", description="Se, endre eller fjern høyde for brukere på serveren")

    @height_group.command(name="se", description="Se høyden til en bruker")
    async def height_see(self, interaction: discord.Interaction, bruker: discord.Member = None):
        """
        See the height of a user

        Parameters
        ----------
        interaction (discord.Interaction): The interaction object
        bruker (discord.Member): The user to see the height of
        """

        if not bruker:
            bruker = interaction.user

        self.cursor.execute(
            """
            SELECT height FROM user_facts
            WHERE discord_id = %s and height IS NOT NULL;
            """,
            (bruker.id,),
        )
        height = self.cursor.fetchone()

        if not height:
            return await interaction.response.send_message(
                embed=embed_templates.error_warning(interaction, text="Brukeren har ikke lagt inn høyden sin")
            )
        
        height = height[0]

        inches = height * (1 / 2.54)
        feet = int(inches * (1 / 12))
        inches = int(inches - (feet * 12))

        embed = discord.Embed(color=bruker.color)
        embed.add_field(name="Høyde", value=f"{height} cm")
        embed.add_field(name="Høyde (🦅🦅🇺🇸🦅🦅)", value=f"{feet}'{inches}\"")
        embed.set_author(name=bruker.global_name, icon_url=bruker.avatar)

        await interaction.response.send_message(embed=embed)

    @height_group.command(name="sett", description="Sett høyden din")
    @app_commands.rename(height_cm="høyde_cm")
    async def height_set(self, interaction: discord.Interaction, height_cm: app_commands.Range[int, 50, 250]):
        """
        Set your height

        Parameters
        ----------
        interaction (discord.Interaction): The interaction object
        height_cm (int): The height of the user
        """

        self.cursor.execute(
            """
            INSERT INTO user_facts (discord_id, height)
            VALUES (%s, %s)
            ON CONFLICT (discord_id) DO UPDATE
                SET height = %s;
            """,
            (interaction.user.id, height_cm, height_cm),
        )

        await interaction.response.send_message(embed=embed_templates.success(interaction, text="Høyde satt!"))

    @height_group.command(name="fjern", description="Fjern høyden din")
    async def height_remove(self, interaction: discord.Interaction):
        """
        Remove your height

        Parameters
        ----------
        interaction (discord.Interaction): The interaction object
        """

        self.cursor.execute(
            """
            UPDATE user_facts
            SET height = NULL
            WHERE discord_id = %s;
            """,
            (interaction.user.id,),
        )

        if self.cursor.rowcount == 0:
            return await interaction.response.send_message(
                embed=embed_templates.success(
                    interaction, text="Du hadde ikke lagt inn høyden din fra før av men ok :)"
                )
            )

        await interaction.response.send_message(embed=embed_templates.success(interaction, text="Høyde fjernet!"))

    @height_group.command(name="leaderboard", description="Se en leaderboard over høyder")
    async def height_leaderboard(self, interaction: discord.Interaction):
        """
        See a leaderboard of heights

        Parameters
        ----------
        interaction (discord.Interaction): The interaction object
        """

        self.cursor.execute(
            """
            SELECT discord_id, height FROM user_facts
            WHERE height IS NOT NULL
            ORDER BY height DESC;
            """
        )

        if not (result := self.cursor.fetchall()):
            return await interaction.response.send_message(
                embed=embed_templates.error_warning(interaction, text="Ingen har lagt inn høyden sin enda")
            )

        result_formatted = list(
            map(
                lambda s: f"**#{s[0]+1}** <@{s[1][0]}> - `{s[1][1]}` cm",
                enumerate(result),
            )
        )

        paginator = misc_utils.Paginator(result_formatted)
        view = discord_utils.Scroller(paginator, interaction.user)

        embed = view.construct_embed(discord.Embed(title="Våre høyeste og laveste (👑)"))
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    await bot.add_cog(UserFacts(bot))
