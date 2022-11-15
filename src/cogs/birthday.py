from datetime import datetime

from dateutil.relativedelta import relativedelta
import discord
from discord import app_commands
from discord.ext import commands
import psycopg2

from cogs.utils import discord_utils, embed_templates


class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cursor = self.bot.db_connection.cursor()

    def init_db(self):
        """Create the necessary tables for the birthday cog to work."""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS birthdays (
                discord_id BIGINT PRIMARY KEY,
                birthday DATE
            );
            """
        )
        self.bot.db_connection.commit()

    def __fetch_user_birthday(self, user_id: int) -> datetime | None:
        """Fetch the birthday of a user from the database"""
        self.cursor.execute("SELECT birthday FROM birthdays WHERE discord_id = (%s)", (user_id,))
        result = self.cursor.fetchone()
        if result:
            birthday = result[0]
            return datetime(birthday.year, birthday.month, birthday.day)

    def __fetch_user_next_birthday(self, user_id: int) -> datetime:
        """Get date of next birthday of a user"""
        self.cursor.execute(
            """
                SELECT *, CAST(birthday + ((EXTRACT(YEAR FROM AGE(birthday)) + 1) * interval '1' YEAR) AS DATE) AS next_birthday
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
            return datetime.now()  # This will never happen unless a database error occurs. Keeping the type checker happy

    def __fetch_next_birthdays(self) -> list[tuple[int, datetime, datetime]]:
        """Fetch the 5 first future birthdays of all users in the database"""
        self.cursor.execute(
            """
                SELECT *, CAST(birthday + ((EXTRACT(YEAR FROM AGE(birthday)) + 1) * interval '1' YEAR) AS DATE) AS next_birthday
                FROM birthdays
                ORDER BY next_birthday ASC
                LIMIT 5
            """
        )
        results = self.cursor.fetchall()

        # Convert date objects to datetime objects
        for result in results:
            _, birthday, next_birthday = result
            birthday = datetime(birthday.year, birthday.month, birthday.day)
            next_birthday = datetime(next_birthday.year, next_birthday.month, next_birthday.day)

        return results

    def __set_user_birthday(self, user_id: int, birthday: datetime) -> None:
        """Iset the birthday of a user in the database. If it already exists, update it."""
        try:
            self.cursor.execute(
                """
                INSERT INTO birthdays (discord_id, birthday)
                VALUES (%s, %s)
                """, (user_id, birthday))
            self.bot.db_connection.commit()
        except psycopg2.errors.UniqueViolation:
            self.bot.db_connection.rollback()
            self.cursor.execute("UPDATE birthdays SET birthday = %s WHERE discord_id = %s", (birthday, user_id))
            self.bot.db_connection.commit()

    '''
    @aiocron.crontab("0 0 * * *")
    async def __check_birthdays(self):
        """Check if it's someone's birthday every day at midgnight and send a greeting if it is."""
        await asyncio.sleep(1)  # Prevent sending message before date has really changed

        self.cursor.execute(
            """
                SELECT *
                FROM birthdays
                WHERE EXTRACT(MONTH FROM birthday) = EXTRACT(MONTH FROM current_date)
                    AND EXTRACT(DAY FROM birthday) = EXTRACT(DAY FROM current_date);
            """
        )

        birthdays = self.cursor.fetchall()
        if birthdays:
            guild = self.bot.get_guild(747542543750660178)
            channel = guild.get_channel(747542544291987597)
            for birthday in birthdays:
                user = self.bot.get_user(birthday[0])
                if user:
                    await channel.send(f"Gratulrer med dagen {user.mention}!")
    '''

    @app_commands.checks.cooldown(1, 5)
    @app_commands.command()
    async def settbursdag(self, interaction: discord.Interaction, dag: int, måned: int, år: int):
        """Lagrer din bursdag i databasen"""
        try:
            date = datetime(år, måned, dag)
        except ValueError:
            return await interaction.response.send_message(
                embed=embed_templates.error_fatal(interaction, text="ikke en gyldig dato, gjøk!"),
                ephemeral=True
            )

        if date.year < 1970:
            return await interaction.response.send_message(
                embed=embed_templates.error_fatal(interaction, text="Ok boomer, men nei. Hvorfor? Unix timestamps. Google it"),
                ephemeral=True
            )

        if date > datetime.now():
            return await interaction.response.send_message(
                embed=embed_templates.error_fatal(interaction, text="Du kan ikke sette en fremtidig dato!"),
                ephemeral=True
            )

        self.__set_user_birthday(interaction.user.id, date)

        embed = embed_templates.success(interaction, text=f"Bursdag satt til {discord.utils.format_dt(date, style='D')}")
        await interaction.response.send_message(embed=embed)

    @app_commands.checks.cooldown(1, 5)
    @app_commands.command()
    async def fjernbursdag(self, interaction: discord.Interaction):
        """Fjerner bursdagen din fra databasen"""
        self.cursor.execute("DELETE FROM birthdays WHERE discord_id = (%s)", (interaction.user.id,))
        self.bot.db_connection.commit()

        embed = embed_templates.success(interaction, text="Bursdag fjernet")
        await interaction.response.send_message(embed=embed)

    @app_commands.checks.cooldown(1, 5)
    @app_commands.command()
    async def bursdag(self, interaction: discord.Interaction, bruker: discord.Member | discord.User | None = None):
        """Viser bursdagen til en bruker. Om ingen er gitt, vises din egen bursdag."""
        if not bruker:
            bruker = interaction.user

        user = self.__fetch_user_birthday(bruker.id)

        if not user:
            return await interaction.response.send_message(
                embed=embed_templates.error_fatal(interaction, text="Brukeren har ikke registrert bursdagen sin")
            )

        # Current age information
        birthday = datetime(user.year, user.month, user.day)
        days_old = (datetime.now() - birthday).days
        years_old = relativedelta(datetime.now(), birthday).years

        #  Next birthday information
        next_birthday = self.__fetch_user_next_birthday(bruker.id)
        next_birthday_days = (next_birthday - datetime.now()).days

        embed = discord.Embed(description=bruker.mention, color=discord_utils.get_user_color(bruker))
        embed.set_thumbnail(url=bruker.display_avatar)
        embed.set_author(name=bruker.name, icon_url=bruker.display_avatar)
        embed.add_field(name="Bursdag", value=discord.utils.format_dt(birthday, style="D"))
        embed.add_field(name="Hvor gammel?", value=f"{years_old} år\n({days_old} dager)", inline=False)
        embed.add_field(name="Neste bursdag om", value=f"{next_birthday_days} dager", inline=False)
        embed_templates.default_footer(interaction, embed)
        await interaction.response.send_message(embed=embed)

    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 5)
    @app_commands.command()
    async def kommendebursdager(self, interaction: discord.Interaction):
        """Se opptil de 5 neste bursdagene i UiO Gaming"""
        next_birthdays = self.__fetch_next_birthdays()

        if not next_birthdays:
            return await interaction.response.send_message(embed=embed_templates.error_fatal(interaction, text="Ingen bursdager"))

        birthday_string = ""
        for user in next_birthdays:
            user_id, _, next_birthday = user
            try:
                discord_user = await interaction.guild.fetch_member(user_id)  # Guild should always be available because of guild_only
            except (discord.NotFound, discord.HTTPException):
                continue

            timestamp = discord.utils.format_dt(next_birthday, style="D")
            relative_timestamp = discord.utils.format_dt(next_birthday, style="R")
            birthday_string += f"{discord_user.name}#{discord_user.discriminator} - {timestamp} ({relative_timestamp})\n"

        if not birthday_string:
            return await interaction.response.send_message(embed=embed_templates.error_fatal(interaction, text="Ingen bursdager"))

        embed = discord.Embed(title="Kommende bursdager", description=birthday_string)
        embed_templates.default_footer(interaction, embed)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Birthday(bot))