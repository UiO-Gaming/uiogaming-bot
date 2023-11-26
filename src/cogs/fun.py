from discord.ext import commands


class Fun(commands.Cog):
    """Simple commands that return short strings for the memes"""

    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command(name="norskeuniversiteter")
    async def norskeuniversiteter(self, ctx: commands.Context):
        """
        Sends a link to university meme image album

        Parameters
        ----------
        ctx (commands.Context): Context object
        """

        await ctx.reply("<https://imgur.com/a/uGopaSq>")

    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command(name="ifi")
    async def ifi(self, ctx: commands.Context):
        """
        ifi meme 1

        Parameters
        ----------
        ctx (commands.Context): Context object
        """

        await ctx.reply("https://i.imgur.com/ypyK1mi.jpg")

    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command(name="ifi2")
    async def ifi2(self, ctx: commands.Context):
        """
        ifi meme 2

        Parameters
        ----------
        ctx (commands.Context): Context object
        """

        await ctx.reply("https://i.imgur.com/ZqgZEEA.jpg")

    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command()
    async def ifi3(self, ctx: commands.Context):
        """
        ifi meme 3

        Parameters
        ----------
        ctx (commands.Context): Context object
        """

        await ctx.reply("https://i.imgur.com/Gx9DQE5.jpg")

    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command()
    async def uio(self, ctx: commands.Context):
        """
        uio meme 1

        Parameters
        ----------
        ctx (commands.Context): Context object
        """

        await ctx.reply("https://i.imgur.com/188MoIV.jpg")

    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command()
    async def ntnu(self, ctx: commands.Context):
        """
        ntnu meme 1

        Parameters
        ----------
        ctx (commands.Context): Context object
        """

        await ctx.reply("https://twitter.com/NTNU/status/970667413564993536")

    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command()
    async def ntnu2(self, ctx: commands.Context):
        """
        ntnu meme 2

        Parameters
        ----------
        ctx (commands.Context): Context object
        """

        await ctx.reply("https://i.imgur.com/h84fknj.jpg")

    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command()
    async def erna(self, ctx: commands.Context):
        """
        erna, vil ikke

        Parameters
        ----------
        ctx (commands.Context): Context object
        """

        await ctx.reply("https://twitter.com/erna_solberg/status/1075333228779765760")

    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command()
    async def snake(self, ctx: commands.Context):
        """
        snake

        Parameters
        ----------
        ctx (commands.Context): Context object
        """

        await ctx.reply("A snake eating its own tail indicates that its excrement provides food for it")


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    await bot.add_cog(Fun(bot))
