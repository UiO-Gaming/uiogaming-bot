from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command()
    async def norskeuniversiteter(self, ctx):
        await ctx.send('<https://imgur.com/a/uGopaSq>')

    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command()
    async def informatikkuio(self, ctx):
        await ctx.send('https://i.imgur.com/ypyK1mi.jpg')
    
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command()
    async def informatikkuio2(self, ctx):
        await ctx.send('https://i.imgur.com/ZqgZEEA.jpg')

    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command()
    async def informatikkuio3(self, ctx):
        await ctx.send('https://i.imgur.com/Gx9DQE5.jpg')

    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command()
    async def uio(self, ctx):
        await ctx.send('https://i.imgur.com/188MoIV.jpg')

    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command()
    async def ntnu(self, ctx):
        await ctx.send('https://twitter.com/NTNU/status/970667413564993536')

    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command()
    async def ntnu2(self, ctx):
        await ctx.send('https://i.imgur.com/h84fknj.jpg')


def setup(bot):
    bot.add_cog(Fun(bot))
