import asyncio
from datetime import datetime

import discord
import psycopg2
from dateutil.relativedelta import relativedelta
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks

from cogs.utils import discord_utils
from cogs.utils import embed_templates
from cogs.utils import misc_utils


class Birthday(commands.Cog):
    """Save the birthday of Discord users and allow them to see the birthdays of other users"""

    def __init__(self, bot: commands.Bot):
        """
        Parameters
        ----------
        bot (commands.Bot): The bot instance
        """

        self.bot = bot
        self.cursor = self.bot.db_connection.cursor()
        self.init_db()
        self.cursor.execute("SET timezone TO 'Europe/Oslo';")
        self.birthday_check.start()

    def init_db(self):
        """
        Create the necessary tables for the birthday cog to work
        """

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS birthdays (
                discord_id BIGINT PRIMARY KEY,
                birthday DATE
            );
            """
        )

    birthday_group = app_commands.Group(
        name="bursdag", description="Se, endre eller fjern bursdager for brukere på serveren"
    )

    @tasks.loop(hours=24)
    async def birthday_check(self):
        """
        Check if it's someone's birthday every day at midgnight and send a greeting if it is
        """

        await asyncio.sleep(1)  # Prevent sending message before date has really changed

        self.bot.logger.info("Checking for birthdays")

        self.cursor.execute(
            """
            SELECT *
            FROM birthdays
            WHERE EXTRACT(MONTH FROM birthday) = EXTRACT(MONTH FROM current_date)
                AND EXTRACT(DAY FROM birthday) = EXTRACT(DAY FROM current_date);
            """
        )

        birthdays = self.cursor.fetchall()
        self.bot.logger.info(f"Found the following birthdays: {birthdays}")  # TODO: Temporary. Remove
        if birthdays:
            guild = self.bot.get_guild(747542543750660178)
            channel = guild.get_channel(747542544291987597)
            for birthday in birthdays:
                user = await guild.fetch_member(birthday[0])
                if user:
                    await channel.send(f"Gratulerer med dagen {user.mention}! 🥳")
                else:
                    self.bot.logger.warning(f"Could not find user with ID {birthday[0]}")

    @birthday_check.before_loop
    async def before_birthday_check(self):
        """
        Syncs loop with the time of day
        """

        self.bot.logger.info("Postponing birthday check until midnight")
        await discord_utils.sleep_until_midnight(self.bot)

    def cog_unload(self):
        self.birthday_check.cancel()

    def fetch_user_birthday(self, user_id: int) -> datetime | None:
        """
        Fetch the birthday of a user in the database

        Parameters
        ----------
        user_id (int): The Discord user ID

        Returns
        ----------
        (datetime | None): The birthday of the user
        """

        self.cursor.execute("SELECT birthday FROM birthdays WHERE discord_id = (%s)", (user_id,))
        result = self.cursor.fetchone()
        if result:
            birthday = result[0]
            return datetime(birthday.year, birthday.month, birthday.day)

    def fetch_user_next_birthday(self, user_id: int) -> datetime:
        """
        Get date of next birthday for a user

        Parameters
        ----------
        user_id (int): The Discord user ID

        Returns
        ----------
        (datetime): The date of the next birthday
        """

        self.cursor.execute(
            """
            SELECT *, CAST(birthday + ((EXTRACT(YEAR FROM AGE(birthday)) + 1) * interval '1' YEAR) AS DATE) AS next_bday
            FROM birthdays
            WHERE discord_id = %s
            """,
            (user_id,),
        )
        results = self.cursor.fetchone()
        if results:
            birthday = results[2]
            return datetime(birthday.year, birthday.month, birthday.day)
        else:
            # This will never happen unless a database error occurs. Keeping the type checker happy
            return datetime.now()

    def fetch_next_birthdays(self) -> list[tuple[int, datetime, datetime]]:
        """
        Fetch the 5 first future birthdays of all users in the database

        Returns
        ----------
        (list[tuple[int, datetime, datetime]]): List of tuples containing the user ID, date of birth and next birthday
        """

        self.cursor.execute(
            """
            SELECT *, CAST(birthday + ((EXTRACT(YEAR FROM AGE(birthday)) + 1) * interval '1' YEAR) AS DATE) AS next_bday
            FROM birthdays
            ORDER BY next_bday ASC
            """
        )
        results = self.cursor.fetchall()

        # Convert date objects to datetime objects
        birthdays = []
        for result in results:
            discord_id, birthday, next_birthday = result
            birthday = datetime(birthday.year, birthday.month, birthday.day)
            next_birthday = datetime(next_birthday.year, next_birthday.month, next_birthday.day)
            birthdays.append((discord_id, birthday, next_birthday))

        return birthdays

    def set_user_birthday(self, user_id: int, birthday: datetime):
        """
        Set the birthday of a user in the database. If it already exists, update it.

        Parameters
        ----------
        user_id (int): The Discord user ID
        birthday (datetime): The birthday of the user
        """

        try:
            self.cursor.execute(
                """
                INSERT INTO birthdays (discord_id, birthday)
                VALUES (%s, %s)
                """,
                (user_id, birthday),
            )
        except psycopg2.errors.UniqueViolation:
            self.bot.db_connection.rollback()
            self.cursor.execute("UPDATE birthdays SET birthday = %s WHERE discord_id = %s", (birthday, user_id))

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 5)
    @birthday_group.command(name="sett", description="Lagrer din bursdag i databasen")
    async def birthday_set(self, interaction: discord.Interaction, dag: int, måned: int, år: int):
        """
        Allows the user to set their birthday in the database.

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        dag (int): Day of the month
        måned (int): Month of the year
        år (int): Year
        """

        try:
            date = datetime(år, måned, dag)
        except ValueError:
            return await interaction.response.send_message(
                embed=embed_templates.error_warning("ikke en gyldig dato, gjøk!"), ephemeral=True
            )

        if date.year < 1970:
            return await interaction.response.send_message(
                embed=embed_templates.error_warning("Ok boomer, men nei. Hvorfor? Unix timestamps. Google it"),
                ephemeral=True,
            )

        if date > datetime.now():
            return await interaction.response.send_message(
                embed=embed_templates.error_warning("Du kan ikke sette en fremtidig dato!"),
                ephemeral=True,
            )

        self.set_user_birthday(interaction.user.id, date)

        embed = embed_templates.success(f"Bursdag satt til {discord.utils.format_dt(date, style='D')}")
        await interaction.response.send_message(embed=embed)

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 5)
    @birthday_group.command(name="fjern", description="Fjerner bursdagen din fra databasen")
    async def birthday_remove(self, interaction: discord.Interaction):
        """
        Removes the invoking user's birthday from the database

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        """

        self.cursor.execute("DELETE FROM birthdays WHERE discord_id = (%s)", (interaction.user.id,))

        embed = embed_templates.success("Bursdag fjernet")
        await interaction.response.send_message(embed=embed)

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 5)
    @birthday_group.command(name="se", description="Viser bursdagen til en bruker. Om ingen er gitt, vises din egen")
    async def birthday_show(
        self, interaction: discord.Interaction, bruker: discord.Member | discord.User | None = None
    ):
        """
        Shows the birthday of a user. If none is given, shows the invoking user's one.

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        bruker (discord.Member | discord.User | None): The user to show the birthday of. Defaults to None.
        """

        if not bruker:
            bruker = interaction.user

        user = self.fetch_user_birthday(bruker.id)

        if not user:
            return await interaction.response.send_message(
                embed=embed_templates.error_warning("Brukeren har ikke registrert bursdagen sin")
            )

        # Current age information
        birthday = datetime(user.year, user.month, user.day)
        days_old = (datetime.now() - birthday).days
        years_old = relativedelta(datetime.now(), birthday).years

        #  Next birthday information
        next_birthday = self.fetch_user_next_birthday(bruker.id)
        next_birthday_days = (next_birthday - datetime.now()).days

        embed = discord.Embed(description=bruker.mention, color=bruker.color)
        embed.set_thumbnail(url=bruker.display_avatar)
        embed.set_author(name=bruker.name, icon_url=bruker.display_avatar)
        embed.add_field(name="Bursdag", value=discord.utils.format_dt(birthday, style="D"))
        embed.add_field(name="Hvor gammel?", value=f"{years_old} år\n({days_old} dager)", inline=False)
        embed.add_field(
            name="Neste bursdag om",
            value=f'{next_birthday_days} {"dager" if next_birthday_days != 1 else "dag"}',
            inline=False,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 5)
    @birthday_group.command(name="kommende", description="Viser en liste over de kommende bursdager i serveren")
    async def birthdays_upcoming(self, interaction: discord.Interaction):
        """
        Lists up to 5 upcoming birthdays of users in the server.

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        """

        await interaction.response.defer()

        next_birthdays = self.fetch_next_birthdays()

        if not next_birthdays:
            return await interaction.followup.send(embed=embed_templates.error_warning("Ingen bursdager"))

        birthday_strings = []
        for user in next_birthdays:
            user_id, _, next_birthday = user
            try:
                discord_user = await interaction.guild.fetch_member(
                    user_id
                )  # Guild should always be available because of guild_only
            except (discord.NotFound, discord.HTTPException):
                continue

            timestamp = discord.utils.format_dt(next_birthday, style="D")
            relative_timestamp = discord.utils.format_dt(next_birthday, style="R")
            birthday_strings.append(f"* {discord_user.name} - {timestamp} ({relative_timestamp})")

        if not birthday_strings:
            return await interaction.followup.send(embed=embed_templates.error_warning("Ingen bursdager"))

        paginator = misc_utils.Paginator(birthday_strings)
        view = discord_utils.Scroller(paginator, interaction.user)

        embed = view.construct_embed(discord.Embed(title="Kommende bursdager"))
        await interaction.followup.send(embed=embed, view=view)


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    await bot.add_cog(Birthday(bot))
