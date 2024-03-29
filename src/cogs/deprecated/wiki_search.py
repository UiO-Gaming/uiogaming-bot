import discord
import wikipedia
from discord.ext import commands

from cogs.utils import embed_templates


class Wiki(commands.Cog):
    @commands.command()
    async def wiki_search(self, ctx, *search_term):
        search_term = " ".join(search_term)

        search = wikipedia.search(search_term)
        search = search[0]
        search = wikipedia.page(search)
        summary = wikipedia.summary(search_term, sentences=5)
        url = search.url

        embed = discord.Embed(title=f"Wikipediasøk for {search_term}", url=url)
        embed.add_field(name=search_term, value=summary)

        embed_templates.default_footer(ctx, embed)
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Wiki(bot))
