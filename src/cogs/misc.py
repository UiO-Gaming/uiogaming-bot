from datetime import datetime
import re
from os import remove
import urllib

import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import requests

from cogs.utils import embed_templates
from cogs.utils.misc_utils import ignore_exception


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 2)
    @app_commands.command()
    async def weeb(self, interaction: discord.Interaction):
        """Kjeft på weebs"""
        await interaction.response.send_message("<:sven:762725919604473866> Weebs 👉 <#803596668129509417>")

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 2)
    @app_commands.command()
    async def kweeb(self, interaction: discord.Interaction):
        """Kjeft på weebs"""
        await interaction.response.send_message(
            """
            TBD
            """
        )

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 2)
    @app_commands.command()
    async def owo(self, interaction: discord.Interaction, tekst: str):
        """Oversetter teksten din til owo (we_eb)"""

        owo_rules = {"r": "w", "l": "w", "R": "W", "L": "W", "n": "ny", "N": "Ny", "ove": "uv"}
        for key, value in owo_rules.items():
            tekst = re.sub(key, value, tekst)
        # https://kaomoji.moe/

        if len(tekst) >= 1000:
            embed = embed_templates.error_warning(interaction, text="Teksten er for lang")
            return await interaction.response.send_message(embed=embed)

        embed = discord.Embed(color=interaction.client.user.color, description=tekst)
        embed_templates.default_footer(interaction, embed)
        await interaction.response.send_message(embed=embed)

    @app_commands.checks.cooldown(1, 5)
    @app_commands.command()
    async def emne(self, interaction: discord.Interaction, emnekode: str):
        """For NTNU'ere som ikke kan emnekoder på UiO"""
        data = requests.get(f"https://data.uio.no/studies/v1/course/{emnekode}", timeout=10)
        if data.status_code != 200:
            return await interaction.response.send_message(embed=embed_templates.error_fatal(interaction, text="Fant ikke emnekode"))

        await interaction.response.send_message(data.json()["info"]["name"])

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 2)
    @app_commands.command()
    async def klappifiser(self, interation: discord.Interaction, tekst: str):
        """Klapppifiserer teksten din"""
        if len(tekst) >= 1000:
            embed = embed_templates.error_warning(interation, text="Teksten er for lang")
            return await interation.response.send_message(embed=embed)

        tekst = re.sub(" ", "👏", tekst)

        embed = discord.Embed(color=interation.client.user.color, description=f"**{tekst.upper()}**")
        embed_templates.default_footer(interation, embed)
        await interation.response.send_message(embed=embed)

    @app_commands.checks.cooldown(1, 5)
    @app_commands.command()
    async def imdb(self, interaction: discord.Interaction, tittel: str):
        """Se informasjon om en film eller serie"""
        # Search for movie/show
        url = "http://www.omdbapi.com/?" + urllib.parse.urlencode({"s": tittel, "apikey": self.bot.api_keys["omdb"]})
        search = requests.get(url, timeout=10).json()

        try:
            best_result_id = search["Search"][0]["imdbID"]
        except KeyError:
            embed = embed_templates.error_fatal(interaction, text="Fant ikke filmen!")
            return await interaction.response.send_message(embed=embed)

        # Get movie/show info
        data = requests.get(f'http://www.omdbapi.com/?i={best_result_id}&apikey={self.bot.api_keys["omdb"]}', timeout=10).json()
        acceptable_media_types = ["movie", "series", "episode"]
        if data["Type"] not in acceptable_media_types:
            embed = embed_templates.error_fatal(interaction, text="Fant ikke filmen!")
            return await interaction.response.send_message(embed=embed)

        embed = discord.Embed(
            title=f'{data["Title"]} ({data["Year"]})',
            color=0xF5C518,
            url=f'https://www.imdb.com/title/{data["imdbID"]}/',
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar)
        embed.add_field(name="Type", value=data["Type"].title())
        embed.add_field(name="Sjanger", value=data["Genre"])
        embed.add_field(name="Spilletid", value=data["Runtime"])
        embed.add_field(name="Vurdering på IMDb", value=f'{data["imdbRating"]}/10')
        release_date = datetime.strptime(data["Released"], "%d %b %Y")
        embed.add_field(name="Utgitt", value=discord.utils.format_dt(release_date, style="D"))
        embed_templates.default_footer(interaction, embed)

        if data["Poster"] != "N/A":
            embed.set_thumbnail(url=data["Poster"])
        if data["Director"] != "N/A":
            embed.description = data["Director"]
        if data["Plot"] != "N/A" and len(data["Plot"]) < 1024:
            embed.add_field(name="Sammendrag", value=data["Plot"], inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 5)
    @app_commands.command()
    async def helligdager(self, interaction: discord.Interaction, *, land: str = "NO", år: int = None):
        """Se hellidagene i et land"""
        land = land.upper()
        aar = datetime.now().year if not år else int(år)

        data = requests.get(f"https://date.nager.at/api/v2/publicholidays/{aar}/{land}", timeout=10)
        if data.status_code != 200:
            embed = embed_templates.error_fatal(
                interaction, text="Ugyldig land\nHusk å bruke landskoder\n" + "For eksempel: `NO`"
            )
            return await interaction.response.send_message(embed=embed)

        data = data.json()

        country = data[0]["countryCode"].lower()

        # Construct output
        holiday_str = ""
        for day in data:
            date = discord.utils.format_dt(datetime.strptime(day["date"], "%Y-%m-%d"), style="D")
            holiday_str += f'**{date}**: {day["localName"]}\n'

        embed = discord.Embed(color=interaction.client.user.color, title=f":flag_{country}: Helligdager {aar} :flag_{country}:")
        embed.description = holiday_str
        embed_templates.default_footer(interaction, embed)
        await interaction.response.send_message(embed=embed)

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 5)
    @app_commands.command()
    async def match(self, interaction: discord.Interaction, bruker: discord.Member):
        """Se hvor mye du matcher med en annen"""
        if bruker == interaction.user:
            embed = embed_templates.error_warning(
                interaction, text="Jeg vet du er ensom, men du kan " "ikke matche med deg selv"
            )
            return await interaction.response.send_message(embed=embed)

        invoker_id = int(str(interaction.user.id)[11:14])
        user_id = int(str(bruker.id)[11:14])

        match_percent = int((invoker_id + user_id) % 100)

        if bruker.id == self.bot.user.id:
            match_percent = 100

        await interaction.user.display_avatar.save(fp=f"./src/assets/temp/{interaction.user.id}_raw.png")
        await bruker.display_avatar.save(fp=f"./src/assets/temp/{bruker.id}_raw.png")

        invoker = Image.open(f"./src/assets/temp/{interaction.user.id}_raw.png").convert("RGBA")
        invoker = invoker.resize((389, 389), Image.ANTIALIAS)
        user = Image.open(f"./src/assets/temp/{bruker.id}_raw.png").convert("RGBA")
        user = user.resize((389, 389), Image.ANTIALIAS)
        heart = Image.open("./src/assets/misc/heart.png")
        mask = Image.open("./src/assets/misc/heart.png", "r")

        image = Image.new("RGBA", (1024, 576))
        image.paste(invoker, (0, 94))
        image.paste(user, (635, 94))
        image.paste(heart, (311, 94), mask=mask)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("./src/assets/fonts/RobotoMono-Medium.ttf", 86)
        font_size = font.getsize(f"{match_percent}%")
        font_size = ((image.size[0] - font_size[0]) / 2, (image.size[1] - font_size[1]) / 2)
        draw.text(font_size, f"{match_percent}%", font=font, fill=(255, 255, 255, 255))

        image.save(f"./src/assets/temp/{interaction.user.id}_{bruker.id}_edit.png")

        f = discord.File(f"./src/assets/temp/{interaction.user.id}_{bruker.id}_edit.png")
        embed = discord.Embed()
        embed.set_image(url=f"attachment://{interaction.user.id}_{bruker.id}_edit.png")
        embed_templates.default_footer(interaction, embed)
        await interaction.response.send_message(embed=embed, file=f)

        with ignore_exception(OSError):
            remove(f"./src/assets/temp/{bruker.id}_raw.png")
            remove(f"./src/assets/temp/{interaction.user.id}_raw.png")
            remove(f"./src/assets/temp/{interaction.user.id}_{bruker.id}_edit.png")


async def setup(bot):
    await bot.add_cog(Misc(bot))
