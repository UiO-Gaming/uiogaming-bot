"""
------ GJORT ------
- score for skriving om morgenen (kl. 5-9)
+ score for skriving på natta (01-05)
- score for å skrive i politikk
+ score for å skrive i medlemschat
- score for å bli pinged i uio gullkorn
+ score for å få melding på stjernetavla/bli stjerna. multiplier per stjerne
- score hver dag med weebrolle (lite)
"""

"""
------ TO-DO ------
+ score for guten tag

- score sitte i afk
+ score for å sitte i voice per time

---------------
- score for winiie the pooh
- score for memes i general
- score for å snakke negativt om borgerlønn
- score for å snakke negativt om styret
* hvis lav score, spiller av kinesisk nasjonalsang på voicechannel når joiner

daglig uthengig av laveste score
"""


from discord.ext import commands, tasks
import discord
from discord import app_commands

from random import randint

from cogs.utils import discord_utils, embed_templates, misc_utils
from dataclasses import dataclass


@dataclass
class CreditUser:
    user_id: int
    credit_score: int


class SocialCredit(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.fuck_uwu.start()

        self.START_POINTS = 1000
        self.cursor = self.bot.db_connection.cursor()
        self.init_db()

    def init_db(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS social_credit (
                user_id BIGINT PRIMARY KEY,
                credit_score SMALLINT NOT NULL
            );
            """
        )

    def add_new_citizen(func):
        async def wrapper(*args, **kwargs):
            self = args[0]
            self.cursor.execute('SELECT user_id FROM social_credit WHERE user_id = %s', (args[1],))
            if not self.cursor.fetchone():
                self._add_citizen(args[1])
            await func(*args, **kwargs)

        return wrapper

    def roll(percent=50):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                if randint(0, 100) <= percent:  # 25% chance
                    await func(*args, **kwargs)

            return wrapper

        return decorator

    def _add_citizen(self, user_id):
        self.cursor.execute(
            """
            INSERT INTO social_credit
            (user_id, credit_score)
            VALUES (%s, %s)
            """,
            (user_id, self.START_POINTS),
        )

    @tasks.loop(hours=24.0, reconnect=True)
    async def fuck_uwu(self):

        await self.bot.wait_until_ready()

        weeb_role = self.bot.get_guild(747542543750660178).get_role(803629993539403826)
        for weeb in weeb_role.members:
            await self.social_punishment(weeb.id, 1)

    @add_new_citizen
    async def social_punishment(self, user_id, points):
        print(f'{points} points deducted from {user_id}')
        self.cursor.execute(
            """
            UPDATE social_credit
            SET credit_score = credit_score - %s
            WHERE user_id = %s
            """,
            (points, user_id),
        )

    @add_new_citizen
    async def social_reward(self, user_id, points):
        print(f'{points} points given to {user_id}')
        self.cursor.execute(
            """
            UPDATE social_credit
            SET credit_score = credit_score + %s
            WHERE user_id = %s
            """,
            (points, user_id),
        )

    social_credit_group = app_commands.Group(name="socialcredit", description="Trenger dette å forklares?")

    @social_credit_group.command(name="credits", descrption="Sjekk hvor dårlig menneske du er")
    async def credits(self, interaction: discord.Interaction, *, bruker: discord.Member | None = None):

        if not bruker:
            bruker = interaction.user

        self.cursor.execute('SELECT * FROM social_credit WHERE user_id = %s', (bruker.id,))
        result = self.cursor.fetchone()

        if not result:
            return await interaction.response.send_message(
                embed=embed_templates.error_fatal(interaction, f'{bruker.mention} er ikke registrert i databasen')
            )

        db_user = CreditUser(*result)

        embed = discord.Embed(description=(f'{bruker.mention} har `{db_user.credit_score}` social credits'))
        await interaction.response.send_message(embed=embed)

    @social_credit_group.command(name="leaderboard", description="")
    async def leaderboard(self, interaction: discord.Interaction):

        self.cursor.execute(
            f"""
            SELECT * FROM social_credit
            ORDER BY credit_score DESC
            """
        )

        if not (result := self.cursor.fetchall()):
            return await interaction.send(embed=embed_templates.error_fatal(interaction, 'Ingen brukere er registrert i databasen'))
        
        leaderboard_formatted = list(
            map(
                lambda s: f"**#{s[0]+1}** <@{s[1][0]}> - {s[1][1]} poeng",
                enumerate(result),
            )
        )

        paginator = misc_utils.Paginator(leaderboard_formatted)
        view = discord_utils.Scroller(paginator, self.__construct_ranking_embed, interaction.user)

        embed = discord.Embed(title="Våre beste og verste borgere")
        embed = self.__construct_ranking_embed(paginator, paginator.get_current_page(), embed)
        await interaction.followup.send(embed=embed, view=view)

    @commands.Cog.listener('on_message')
    async def on_message(self, message):
        if message.author.bot:
            return

        await self.gullkorn(message)
        await self.politcal_content(message)
        await self.chad_message(message)
        await self.early_bird(message)
        await self.night_owl(message)

    @roll(percent=50)
    async def politcal_content(self, message):
        if message.channel.id == 754706204349038644:
            await self.social_punishment(message.author.id, 25)

    @roll(percent=50)
    async def chad_message(self, message):
        if message.channel.id == 811606213665357824:
            await self.social_reward(message.author.id, 25)

    @roll(percent=50)
    async def early_bird(self, message):
        illegal_hours = [5, 6, 7, 8, 9]

        if message.created_at.hour in illegal_hours:
            await self.social_punishment(message.author.id, 10)

    @roll(percent=50)
    async def night_owl(self, message):
        happy_hours = [1, 2, 3, 4]

        if message.created_at.hour in happy_hours:
            await self.social_reward(message.author.id, 10)

    async def gullkorn(self, message):
        if message.channel.id == 865970753748074576:
            if message.mentions:
                for mention in message.mentions:
                    await self.social_punishment(mention.id, 10)

    @commands.Cog.listener('on_reaction_add')
    async def on_star_add(self, reaction, user):
        if user.bot:
            return

        if reaction.emoji == '⭐':
            if reaction.message.author == user:
                await self.social_punishment(user.id, 100)
            else:
                if len(reaction.message.reactions) >= 3:
                    await self.social_punishment(user.id, (len(reaction.message.reactions) - 1) * 25)
                    await self.social_reward(user.id, 25 * len(reaction.message.reactions))

    @commands.Cog.listener('on_reaction_remove')
    async def on_star_remove(self, reaction, user):
        if user.bot:
            return

        if reaction.emoji == '⭐':
            if len(reaction.message.reactions) >= 3:
                await self.social_punishment(user.id, 25)


async def setup(bot: commands.Bot):
    await bot.add_cog(SocialCredit(bot))
