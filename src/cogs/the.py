import traceback
from typing import Any
import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import io


class The(commands.Cog):
    """
    This cog lets you make a "the" barnacle boy laser eyes meme 
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.background_url = 'https://i.kym-cdn.com/photos/images/newsfeed/001/777/063/d42.png'  # Set your background image URL here
        self.x = 30  # Set your desired X coordinate
        self.y = 340  # Set your desired Y coordinate

    async def fetch_image(self, url: str) -> io.BytesIO:
        """
        Add the cog to the bot on extension load

        Parameters
        ----------
        url (str): url

        Returns
        ----------
        (io.BytesIO): data buffer
        """
        if not url:
            return None
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                data = io.BytesIO(await resp.read())
                return data

    def outline_text(
        self,
        draw: ImageDraw,
        text: str,
        font: ImageFont.FreeTypeFont,
        x: int,
        y: int,
        thickness: int,
    ) -> None:
        """
        Outlines given text
        """

        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill="black")
        draw.text((x, y), text, font=font, fill="white")

    @app_commands.command()
    async def the(self, interaction: discord.Interaction, top_text: str = "", image_url: str = "", bottom_text: str = ""):
        """
        Responds with a barnacle boy laser eyes THE meme with the given captions

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        caption (str): top text
        image_url (str): image url
        bottom_text (str): bottom text
        
        Returns
        ----------
        (discord.File): an image 
        """
        await interaction.response.defer()

        try:
            bg_data = await self.fetch_image(self.background_url)
            background = Image.open(bg_data)
            
            image_data = await self.fetch_image(image_url)

            if image_data:
                image = Image.open(image_data).resize((200, 200), Image.ANTIALIAS)
                background.paste(image, (self.x, self.y))

            draw = ImageDraw.Draw(background)
            font = ImageFont.truetype("./src/assets/fonts/impact.ttf", 120)

            if top_text:
                text_x, text_y = (210, -10)
                self.outline_text(draw, top_text.upper(), font, text_x, text_y, thickness=5)

            if bottom_text:
                text_x, text_y = (150, 550)
                self.outline_text(draw, bottom_text.upper(), font, text_x, text_y, thickness=5)

            with io.BytesIO() as output:
                background.save(output, format="PNG")
                output.seek(0)
                await interaction.followup.send(file=discord.File(output, "result.png"))

        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send("An error occurred while processing the images.")


async def setup(bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """
    
    await bot.add_cog(The(bot))
