from discord.ext import commands
import discord

from re import sub
from datetime import datetime
import requests
import json
from asyncio import sleep
from PIL import Image, ImageDraw, ImageFont
from os import remove
import urllib

from cogs.utils import embed_templates
from cogs.utils.misc_utils import ignore_exception


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command()
    async def weeb(self, ctx):
        """
        Kjeft på weebs
        """

        await ctx.send('<:sven:762725919604473866> Weebs 👉 <#803596668129509417>')

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command(aliases=['owoify', 'uwu'])
    async def owo(self, ctx, *, tekst: str):
        """
        Oversetter teksten din til owo
        """

        owo_rules = {
            'r': 'w',
            'l': 'w',
            'R': 'W',
            'L': 'W',
            'n': 'ny',
            'N': 'Ny',
            'ove': 'uv'
        }
        for key, value in owo_rules.items():
            tekst = sub(key, value, tekst)
        # https://kaomoji.moe/

        if not tekst or len(tekst) >= 1000:
            embed = embed_templates.error_warning(ctx, text='Teksten er for lang')
            return await ctx.send(embed=embed)

        embed = discord.Embed(color=ctx.me.color, description=tekst)
        embed = embed_templates.default_footer(ctx, embed)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command(aliases=['clapify'])
    async def klappifiser(self, ctx, *, tekst):
        """
        Klapppifiserer teksten din
        """

        if not tekst or len(tekst) >= 1000:
            embed = embed_templates.error_warning(ctx, text='Teksten er for lang')
            return await ctx.send(embed=embed)

        tekst = sub(' ', '👏', tekst)

        embed = discord.Embed(color=ctx.me.color, description=f'**{tekst.upper()}**')
        embed = embed_templates.default_footer(ctx, embed)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(aliases=['filmsøk'])
    async def imdb(self, ctx, *, film):
        """
        Se informasjon om en film eller serie
        """

        url = 'http://www.omdbapi.com/?' + urllib.parse.urlencode({'s': film, 'apikey': self.bot.api_keys['omdb']})
        search = requests.get(url).json()

        try:
            best_result_id = search['Search'][0]['imdbID']
        except KeyError:
            embed = embed_templates.error_fatal(ctx, text="Fant ikke filmen!")
            return await ctx.send(embed=embed)

        data = requests.get(f'http://www.omdbapi.com/?i={best_result_id}&apikey={self.bot.api_keys["omdb"]}').json()

        acceptable_media_types = ['movie', 'series', 'episode']
        if data['Type'] not in acceptable_media_types:
            embed = embed_templates.error_fatal(ctx, text="Fant ikke filmen!")
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title=f'{data["Title"]} ({data["Year"]})', 
            color=0xF5C518, 
            url=f'https://www.imdb.com/title/{data["imdbID"]}/'
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name='Type', value=data['Type'].title())
        embed.add_field(name='Sjanger', value=data['Genre'])
        embed.add_field(name='Spilletid', value=data['Runtime'])
        embed.add_field(name='Vurdering på IMDb', value=f'{data["imdbRating"]}/10')
        embed.set_footer(text=f'Utgitt: {data["Released"]}')

        if data['Poster'] != 'N/A':
            embed.set_thumbnail(url=data['Poster'])
        if data['Director'] != 'N/A':
            embed.description = data['Director']
        if data['Plot'] != 'N/A' and len(data['Plot']) < 1024:
            embed.add_field(name='Sammendrag', value=data['Plot'], inline=False)

        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.command(aliases=['identify'])
    async def identifiser(self, ctx, bilde=None):
        """
        Beskriver hva som er på bildet
        """

        if ctx.message.attachments != []:
            bilde = ctx.message.attachments[0].url

        if bilde is None:
            embed = embed_templates.error_fatal(ctx, text='Du må gi meg et bilde!')

        async with ctx.channel.typing():

            payload = {'inputs': [{'data': {'image': {'url': bilde}}}]}
            header = {'Authorization': f'Key {self.bot.api_keys["clarifai"]}'}
            url = 'https://api.clarifai.com/v2/models/aaa03c23b3724a16a56b629203edc62c' + \
                  '/versions/aa7f35c01e0642fda5cf400f543e7c40/outputs'
            data = requests.post(url, data=json.dumps(payload), headers=header)
            if data.status_code != 200:
                embed = embed_templates.default_footer('API request feilet')
                return await ctx.send(embed=embed)

            data = data.json()

            words = []
            for i, concepts in enumerate(data['outputs'][0]['data']['concepts']):
                words.append(concepts['name'])
                if i >= 5:
                    break

            words = ', '.join(words)

            await sleep(2)

            embed = discord.Embed(color=ctx.me.color)
            embed.set_author(name='Clarifai AI', icon_url='https://github.com/Clarifai.png')
            embed.description = f'**Ord som beskriver dette bildet:**\n\n{words}'
            embed.set_image(url=bilde)
            embed = embed_templates.default_footer(ctx, embed)
            await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.command(aliases=['holidays', 'fridager', 'ferie'])
    async def helligdager(self, ctx, land=None, aar=None):
        """
        Se hellidagene i et land
        """

        if not land:
            land = 'NO'
        else:
            land = land.upper()

        if not aar:
            aar = datetime.now().year
        else:
            int(aar)

        data = requests.get(f'https://date.nager.at/api/v2/publicholidays/{aar}/{land}')
        if data.status_code != 200:
            embed = embed_templates.error_fatal(ctx, text='Ugyldig land\nHusk å bruke landskoder\n' +
                                                          'For eksempel: `NO`')
            return await ctx.send(embed=embed)

        data = data.json()

        country = data[0]['countryCode'].lower()
        holiday_str = ''
        for day in data:
            date = day['date']
            date = datetime.strptime(date, '%Y-%m-%d').strftime('%d. %B')
            holiday_str += f'**{date}**: {day["localName"]}\n'

        embed = discord.Embed(color=ctx.me.color, title=f':flag_{country}: Helligdager {aar} :flag_{country}:')
        embed.description = holiday_str
        embed = embed_templates.default_footer(ctx, embed)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.command()
    async def match(self, ctx, *, bruker: discord.Member = None):
        """
        Se hvor mye du matcher med en annen
        """

        if not bruker:
            embed = embed_templates.error_warning(ctx, text='Du må gi meg en bruker')
            return await ctx.send(embed=embed)
        if bruker == ctx.author:
            embed = embed_templates.error_warning(ctx, text='Jeg vet du er ensom, men du kan '
                                                            'ikke matche med deg selv')
            return await ctx.send(embed=embed)

        async with ctx.channel.typing():

            invoker_id = int(str(ctx.author.id)[11:14])
            user_id = int(str(bruker.id)[11:14])

            match_percent = int((invoker_id + user_id) % 100)

            if bruker.id == self.bot.user.id:
                match_percent = 100

            await ctx.author.avatar_url_as(format='png').save(fp=f'./src/assets/temp/{ctx.author.id}_raw.png')
            await bruker.avatar_url_as(format='png').save(fp=f'./src/assets/temp/{bruker.id}_raw.png')

            invoker = Image.open(f'./src/assets/temp/{ctx.author.id}_raw.png').convert('RGBA')
            invoker = invoker.resize((389, 389), Image.ANTIALIAS)
            user = Image.open(f'./src/assets/temp/{bruker.id}_raw.png').convert('RGBA')
            user = user.resize((389, 389), Image.ANTIALIAS)
            heart = Image.open('./src/assets/misc/heart.png')
            mask = Image.open('./src/assets/misc/heart.png', 'r')

            image = Image.new('RGBA', (1024, 576))
            image.paste(invoker, (0, 94))
            image.paste(user, (635, 94))
            image.paste(heart, (311, 94), mask=mask)
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype('./src/assets/fonts/RobotoMono-Medium.ttf', 86)
            font_size = font.getsize(f'{match_percent}%')
            font_size = ((image.size[0] - font_size[0]) / 2, (image.size[1] - font_size[1]) / 2)
            draw.text(font_size, f'{match_percent}%', font=font, fill=(255, 255, 255, 255))

            image.save(f'./src/assets/temp/{ctx.author.id}_{bruker.id}_edit.png')

            f = discord.File(f'./src/assets/temp/{ctx.author.id}_{bruker.id}_edit.png')
            embed = discord.Embed()
            embed.set_image(url=f'attachment://{ctx.author.id}_{bruker.id}_edit.png')
            embed = embed_templates.default_footer(ctx, embed)
            await ctx.send(embed=embed, file=f)

            with ignore_exception(OSError):
                remove(f'./src/assets/temp/{bruker.id}_raw.png')
                remove(f'./src/assets/temp/{ctx.author.id}_raw.png')
                remove(f'./src/assets/temp/{ctx.author.id}_{bruker.id}_edit.png')


def setup(bot):
    bot.add_cog(Misc(bot))
