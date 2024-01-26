import re
import urllib
from datetime import datetime
from hashlib import md5
from io import BytesIO

import discord
import requests
from discord import app_commands
from discord.ext import commands
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from cogs.utils import discord_utils
from cogs.utils import embed_templates


class Misc(commands.Cog):
    """Miscellaneous commands that don't fit anywhere else"""

    def __init__(self, bot: commands.Bot):
        """
        Parameters
        ----------
        bot (commands.Bot): The bot instance
        """

        self.bot = bot

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 2)
    @app_commands.command(name="weeb", description="Kjeft på weebs")
    async def weeb(self, interaction: discord.Interaction):
        """
        Call out weebs

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        """

        await interaction.response.send_message("<:sven:762725919604473866> Weebs 👉 <#803596668129509417>")

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 2)
    @app_commands.command(name="owo", description="Oversetter teksten din til owo (we_eb)")
    async def owo(self, interaction: discord.Interaction, tekst: str):
        """
        Translate text into owo (we_eb)

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        tekst (str): Text to translate
        """

        owo_rules = {"r": "w", "l": "w", "R": "W", "L": "W", "n": "ny", "N": "Ny", "ove": "uv"}
        for key, value in owo_rules.items():
            tekst = re.sub(key, value, tekst)
        # https://kaomoji.moe/

        if len(tekst) >= 1000:
            embed = embed_templates.error_warning(interaction, text="Teksten er for lang")
            return await interaction.response.send_message(embed=embed)

        embed = discord.Embed(color=interaction.client.user.color, description=tekst)
        await interaction.response.send_message(embed=embed)

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 2)
    @app_commands.command(name="dicksize", description="Se hvor liten pikk du har")
    async def dicksize(self, interaction: discord.Interaction, bruker: discord.Member | discord.User | None = None):
        """
        Get a totally accurate meassurement of a user's dick

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        bruker (discord.Member | discord.User | None): The user you want to see the dicksize of. Defaults to author
        """

        if not bruker:
            bruker = interaction.user

        # Må jo gi meg selv en stor kuk
        if bruker.id == 170506717140877312:
            dick_size = 69
        elif bruker.id == 327207142681608192:
            dick_size = 1
        else:
            dick_hash = md5(str(bruker.id).encode("utf-8")).hexdigest()
            dick_size = (
                int(dick_hash[11:13], 16) * (25 - 2) // 255 + 2
            )  # This is 5 year old code. I have no fucking idea what's going on

        dick_drawing = "=" * dick_size

        embed = discord.Embed(color=bruker.color)
        embed.set_author(name=bruker.global_name, icon_url=bruker.avatar)
        embed.add_field(name="Kukstørrelse", value=f"{dick_size} cm\n8{dick_drawing}D")
        await interaction.response.send_message(embed=embed)

    @app_commands.checks.cooldown(1, 5)
    @app_commands.command(name="emne", description="For NTNU'ere som ikke kan emnekoder på UiO")
    async def course_code(self, interaction: discord.Interaction, emnekode: str):
        """
        Translate UiO course codes to their respective course names

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        emnekode (str): UiO course code
        """

        data = requests.get(f"https://data.uio.no/studies/v1/course/{emnekode}", timeout=10)
        if data.status_code != 200:
            return await interaction.response.send_message(
                embed=embed_templates.error_fatal(interaction, text="Fant ikke emnekode")
            )

        await interaction.response.send_message(data.json()["info"]["name"])

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 2)
    @app_commands.command(name="klappifiser", description="Klappifiser tekst")
    async def clapify(self, interation: discord.Interaction, tekst: str):
        """
        Add clap emoji between every word of a string

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        tekst (str): Text to clapify
        """

        if len(tekst) >= 1000:
            embed = embed_templates.error_warning(interation, text="Teksten er for lang")
            return await interation.response.send_message(embed=embed)

        tekst = re.sub(" ", "👏", tekst)

        embed = discord.Embed(color=interation.client.user.color, description=f"**{tekst.upper()}**")
        await interation.response.send_message(embed=embed)

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 5)
    @app_commands.command(name="imdb", description="Søk etter filmer på IMDB")
    async def imdb(self, interaction: discord.Interaction, tittel: str):
        """
        Search for movies on IMDB and displays information about the first result

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        tittel (str): Movie title
        """

        # Search for movie/show
        url = "http://www.omdbapi.com/?" + urllib.parse.urlencode({"s": tittel, "apikey": self.bot.api_keys["omdb"]})
        search = requests.get(url, timeout=10).json()

        try:
            best_result_id = search["Search"][0]["imdbID"]
        except KeyError:
            embed = embed_templates.error_fatal(interaction, text="Fant ikke filmen!")
            return await interaction.response.send_message(embed=embed)

        # Get movie/show info
        data = requests.get(
            f'http://www.omdbapi.com/?i={best_result_id}&apikey={self.bot.api_keys["omdb"]}', timeout=10
        ).json()
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

        if data["Poster"] != "N/A":
            embed.set_thumbnail(url=data["Poster"])
        if data["Director"] != "N/A":
            embed.description = data["Director"]
        if data["Plot"] != "N/A" and len(data["Plot"]) < 1024:
            embed.add_field(name="Sammendrag", value=data["Plot"], inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 5)
    @app_commands.command(name="helligdager", description="Se helligdager i et land for et år")
    async def holidays(self, interaction: discord.Interaction, *, land: str = "NO", år: int = None):
        """
        Get holidays for a country for a given year

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        land (str): Country code
        år (int): Year
        """

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
            holiday_str += f'* **{date}**: {day["localName"]}\n'

        embed = discord.Embed(
            color=interaction.client.user.color, title=f":flag_{country}: Helligdager {aar} :flag_{country}:"
        )
        embed.description = holiday_str
        await interaction.response.send_message(embed=embed)

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 5)
    @app_commands.command(name="match", description="Se hvor mye du matcher med en annen")
    async def match(self, interaction: discord.Interaction, bruker: discord.Member):
        """
        Get dating compatibility with another user

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        bruker (discord.Member): User to match with
        """

        if bruker == interaction.user:
            embed = embed_templates.error_warning(
                interaction, text="Jeg vet du er ensom, men du kan ikke matche med deg selv"
            )
            return await interaction.response.send_message(embed=embed)

        invoker_id = int(str(interaction.user.id)[11:14])
        user_id = int(str(bruker.id)[11:14])

        match_percent = int((invoker_id + user_id) % 100)

        if bruker.id == self.bot.user.id:
            match_percent = 100

        # Prepare invoker avatar
        invoker_avatar = await discord_utils.get_file_bytesio(interaction.user.display_avatar)
        invoker = Image.open(invoker_avatar).convert("RGBA")
        invoker = invoker.resize((389, 389))

        # Prepare user avatar
        user_avatar = await discord_utils.get_file_bytesio(bruker.display_avatar)
        user = Image.open(user_avatar).convert("RGBA")
        user = user.resize((389, 389))

        # Prepare heart image
        heart = Image.open("./src/assets/misc/heart.png")
        mask = Image.open("./src/assets/misc/heart.png", "r")

        # Putting it all together
        image = Image.new("RGBA", (1024, 576))
        image.paste(invoker, (0, 94))
        image.paste(user, (635, 94))
        image.paste(heart, (311, 94), mask=mask)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("./src/assets/fonts/RobotoMono-Medium.ttf", 86)
        font_size = font.getbbox(f"{match_percent}%")
        font_size = ((image.size[0] - font_size[2]) / 2, (image.size[1] - font_size[3]) / 2)
        draw.text(font_size, f"{match_percent}%", font=font, fill=(255, 255, 255, 255))

        # Save image
        output = BytesIO()
        image.save(output, format="PNG")
        output.seek(0)

        # Send
        f = discord.File(output, filename=f"{interaction.user.id}_{bruker.id}_match.png")
        embed = discord.Embed()
        embed.set_image(url=f"attachment://{interaction.user.id}_{bruker.id}_match.png")
        await interaction.response.send_message(embed=embed, file=f)


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    await bot.add_cog(Misc(bot))
