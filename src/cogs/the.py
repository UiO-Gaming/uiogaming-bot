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

    def __init__(self, bot):
        self.bot = bot
        self.background_url = 'https://i.kym-cdn.com/photos/images/newsfeed/001/777/063/d42.png'  # Set your background image URL here
        self.x = 30  # Set your desired X coordinate
        self.y = 340  # Set your desired Y coordinate

    async def fetch_image(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                data = io.BytesIO(await resp.read())
                return data

    def outline_text(self, draw, text, font, x, y, thickness):
        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill="black")
        draw.text((x, y), text, font=font, fill="white")


    @app_commands.command()
    async def the(self, interaction: discord.Interaction, caption: str, image_url: str, bottom_text: str = ""):
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
        try:
            image_data = await self.fetch_image(image_url)
            bg_data = await self.fetch_image(self.background_url)

            if not image_data or not bg_data:
                await interaction.response.send_message("Invalid image URLs provided.")
                return

            image = Image.open(image_data)
            background = Image.open(bg_data)

            fixed_size = (200, 200)  # Set your desired maximum width and height
            image.thumbnail(fixed_size, Image.ANTIALIAS)

            background.paste(image, (self.x, self.y))

            if caption:
                draw = ImageDraw.Draw(background)
                font = ImageFont.truetype("./src/assets/fonts/impact.ttf", 120)
                text = caption.upper()
                text_width, text_height = draw.textsize(text, font=font)
                text_x, text_y = (210, -10)
                # text_x, text_y = self.x + (image.width - text_width) // 2, self.y + image.height
                self.outline_text(draw, text, font, text_x, text_y, thickness=5)
                draw.text((text_x, text_y), text, font=font, fill="white")

            if bottom_text:
                draw = ImageDraw.Draw(background)
                font = ImageFont.truetype("./src/assets/fonts/impact.ttf", 120)
                text = bottom_text.upper()
                text_width, text_height = draw.textsize(text, font=font)
                text_x, text_y = (150, 550)
                # text_x, text_y = self.x + (image.width - text_width) // 2, self.y + image.height
                self.outline_text(draw, text, font, text_x, text_y, thickness=5)
                draw.text((text_x, text_y), text, font=font, fill="white")

            with io.BytesIO() as output:
                background.save(output, format="PNG")
                output.seek(0)
                await interaction.response.send_message(file=discord.File(output, "result.png"))

        except Exception as e:
            print(e)
            await interaction.response.send_message("An error occurred while processing the images.")

async def setup(bot):
    await bot.add_cog(The(bot))
