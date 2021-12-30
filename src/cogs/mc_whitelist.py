from discord.ext import commands

import requests
import json
from mcrcon import MCRcon

from cogs.utils import embed_templates


class MCWhitelist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cursor = self.bot.db_connection.cursor()
        self.init_db()

    def init_db(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS mc_whitelist (
                discord_id BIGINT PRIMARY KEY,
                minecraft_id TEXT NOT NULL
            );
            """
        )
        self.bot.db_connection.commit()

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command()
    async def whitelist(self, ctx, minecraftbrukernavn):

        # fetch minecraft uuid from api
        data = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{minecraftbrukernavn}")
        if data.status_code != 200:
            return await ctx.send(
                embed=embed_templates.error_fatal(ctx, text=f"Brukeren `{minecraftbrukernavn}` finnes ikk på minecraft")
            )

        data = data.json()

        # check if the discord user or minecraft user is in the db
        self.cursor.execute(
            "SELECT * FROM mc_whitelist WHERE minecraft_id = %s OR discord_id = %s", (data["id"], ctx.author.id)
        )
        if self.cursor.fetchone():
            return await ctx.send(
                embed=embed_templates.error_fatal(
                    ctx, text="Du har allerede whitelisted en bruker eller så er brukeren du oppga whitelisted"
                )
            )

        with MCRcon(host="192.168.0.24", password="hallaballayeet", port=25575) as mcr:
            mcr.command(f"whitelist add {data['name']}")
            mcr.command("whitelist reload")

        self.cursor.execute(
            """
            INSERT INTO mc_whitelist (discord_id, minecraft_id)
            VALUES (%s, %s)
            """,
            (ctx.author.id, data["id"]),
        )
        self.bot.db_connection.commit()

        await ctx.send(
            embed=embed_templates.success(
                ctx, text=f"`{data['name']}` er nå tilknyttet din discordbruker og whitelisted!"
            )
        )


def setup(bot):
    bot.add_cog(MCWhitelist(bot))
