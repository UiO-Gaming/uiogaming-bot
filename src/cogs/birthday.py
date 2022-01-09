from discord.ext import commands
import discord

import psycopg2
import aiocron
import asyncio
from datetime import datetime
from dateutil.relativedelta import relativedelta

from cogs.utils import embed_templates, discord_utils


class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cursor = self.bot.db_connection.cursor()

    def init_db(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS birthdays (
                discord_id BIGINT PRIMARY KEY,
                birthday DATE
            );
            """
        )
        self.bot.db_connection.commit()

    def _fetch_user_birthday(self, user_id):
        self.cursor.execute("SELECT birthday FROM birthdays WHERE discord_id = (%s)", (user_id,))
        return self.cursor.fetchone()

    def _fetch_user_next_birthday(self, user_id):
        self.cursor.execute(
            """
                SELECT *, CAST(birthday + ((EXTRACT(YEAR FROM AGE(birthday)) + 1) * interval '1' YEAR) AS DATE) AS next_birthday
                FROM birthdays
                WHERE discord_id = %s
            """,
            (user_id,),
        )
        return self.cursor.fetchone()

    def _fetch_next_birthdays(self):
        self.cursor.execute(
            """
                SELECT *, CAST(birthday + ((EXTRACT(YEAR FROM AGE(birthday)) + 1) * interval '1' YEAR) AS DATE) AS next_birthday
                FROM birthdays
                ORDER BY next_birthday ASC
                LIMIT 5
            """
        )
        return self.cursor.fetchall()

    def _set_user_birthday(self, user_id, birthday):
        try:
            self.cursor.execute("INSERT INTO birthdays (discord_id, birthday) VALUES (%s, %s)", (user_id, birthday))
            self.bot.db_connection.commit()
        except psycopg2.errors.UniqueViolation:
            self.bot.db_connection.rollback()
            self.cursor.execute("UPDATE birthdays SET birthday = %s WHERE discord_id = %s", (birthday, user_id))
            self.bot.db_connection.commit()

    @aiocron.crontab("0 0 * * *")
    async def _check_birthdays(self):
        await asyncio.sleep(1)
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

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def settbursdag(self, ctx, date):

        try:
            date = datetime.strptime(date, "%d.%m.%Y")
        except ValueError:
            return await ctx.send(embed=embed_templates.error_fatal(ctx, text="Feil format, gjøk!"))

        if date.year < 1970:
            return await ctx.send(
                embed=embed_templates.error_fatal(ctx, text="Ok boomer, men nei. Hvorfor? Unix timestamps. Google it")
            )

        self._set_user_birthday(ctx.author.id, date)

        embed = embed_templates.success(ctx, text=f"Bursdag satt til <t:{int(date.timestamp())}:D>")
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def fjernbursdag(self, ctx):

        self.cursor.execute("DELETE FROM birthdays WHERE discord_id = (%s)", (ctx.author.id,))
        self.bot.db_connection.commit()

        embed = embed_templates.success(ctx, text="Bursdag fjernet")
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def bursdag(self, ctx, *, bruker: discord.Member = None):

        if not bruker:
            bruker = ctx.author

        user = self._fetch_user_birthday(bruker.id)

        if not user:
            return await ctx.send(
                embed=embed_templates.error_fatal(ctx, text="Brukeren har ikke registrert bursdagen sin")
            )

        birthday = datetime(user[0].year, user[0].month, user[0].day)
        days_old = (datetime.now() - birthday).days
        years_old = relativedelta(datetime.now(), birthday).years

        #  Next birthday
        birthday_current_year = birthday.replace(year=datetime.now().year)
        if (datetime.now() - birthday_current_year).days < 0:
            next_birthday = birthday_current_year
        else:
            next_birthday = birthday_current_year.replace(year=datetime.now().year + 1)
        next_birthday_days = (next_birthday - datetime.now()).days

        embed = discord.Embed(description=bruker.mention, color=discord_utils.get_user_color(bruker))
        embed.set_thumbnail(url=bruker.avatar_url)
        embed.set_author(name=bruker.name, icon_url=bruker.avatar_url)
        embed.add_field(name="Bursdag", value=f"<t:{int(birthday.timestamp())}:D>")
        embed.add_field(name="Hvor gammel?", value=f"{years_old} år\n({days_old} dager)", inline=False)
        embed.add_field(name="Neste bursdag om", value=f"{next_birthday_days} dager", inline=False)
        embed_templates.default_footer(ctx, embed)
        await ctx.send(embed=embed)

    @commands.command()
    async def kommendebursdager(self, ctx):

        next_birthdays = self._fetch_next_birthdays()

        if not next_birthdays:
            return await ctx.send(embed=embed_templates.error_fatal(ctx, text="Ingen bursdager"))

        birthday_string = ""
        for user in next_birthdays:
            discord_user = ctx.guild.get_member(user[0])
            if not discord_user:
                continue

            next_birthday = datetime(user[2].year, user[2].month, user[2].day)
            next_birthday_days = (next_birthday - datetime.now()).days
            birthday_string += f"{discord_user.name}#{discord_user.discriminator} - <t:{int(next_birthday.timestamp())}:D> ({next_birthday_days} dager)\n"

        embed = discord.Embed(title="Kommende bursdager", description=birthday_string)
        embed_templates.default_footer(ctx, embed)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Birthday(bot))
