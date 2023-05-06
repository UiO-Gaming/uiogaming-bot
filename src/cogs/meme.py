import textwrap
from io import BytesIO

import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image
from PIL import ImageDraw
from PIL import ImageEnhance
from PIL import ImageFont
from PIL import UnidentifiedImageError

from cogs.utils import embed_templates


class Meme(commands.Cog):
    """Generate memes"""

    def __init__(self, bot: commands.Bot):
        """
        Parameters
        ----------
        bot (commands.Bot): The bot instance
        """

        self.bot = bot

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 5)
    @app_commands.command(name="deepfry", description="Friter et bilde til hundre og helvete")
    async def deepfry(self, interaction: discord.Interaction, bilde: discord.Attachment):
        """
        Deepfries an image

        Parameters
        ----------
        interaction (discord.Interaction): The interaction
        bilde (discord.Attachment): The image to deepfry
        """

        await interaction.response.defer()

        # Fetch image
        input = BytesIO()
        input.write(await bilde.read())
        input.seek(0)

        # Open image
        # Check if image is valid
        try:
            image = Image.open(input)
        except UnidentifiedImageError:
            await interaction.followup.send(embed=embed_templates.error_warning(interaction, text="Bildet er ugyldig"))
            return

        # Apply various deepfrying filters
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(2.0)

        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)

        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)

        output = BytesIO()
        image.save(output, format="jpeg", quality=5)
        output.seek(0)

        await interaction.followup.send(file=discord.File(output, "deepfry.jpg"))

    @staticmethod
    def __format_text(text: str, textbox_width: int):
        """
        Formats text to fit in a textbox of a given width.

        Parameters
        ----------
        text (str): Text to be formatted.
        textbox_width (int): Width of the textbox.
        """
        font_size = int(textbox_width / (3 * len(text) ** (1 / 2)))
        font = ImageFont.truetype("./src/assets/fonts/RobotoMono-Medium.ttf", font_size)

        line_length = textbox_width // font_size
        text = textwrap.fill(text, width=line_length)

        return text, font

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 5)
    @app_commands.command(name="preferansemem", description="Generer en drake-aktig mem basert på tekst")
    async def prefer_meme(self, interaction: discord.Interaction, dårlig_tekst: str, bra_tekst: str):
        """
        Generates a drake-like meme based on text

        Parameters
        ----------
        interaction (discord.Interaction): The interaction
        dårlig_tekst (str): The upper text, what's disliked
        bra_tekst (str): The lower text, what's liked
        """

        await interaction.response.defer()

        # Fetch meme template
        template = Image.open("./src/assets/misc/sivert_goodbad.jpg")

        # Calculate font sizes
        top_text, top_font = Meme.__format_text(dårlig_tekst, 536)
        bottom_text, bottom_font = Meme.__format_text(bra_tekst, 536)

        # Draw top text
        box_size = (536, 538)
        box = Image.new("RGB", box_size, (255, 255, 255))
        draw = ImageDraw.Draw(box)
        text_box = draw.multiline_textbbox(
            (box_size[0] // 2, box_size[1] // 2), text=top_text, font=top_font, align="center"
        )
        text_box = ((box.size[0] - text_box[0]) // 2, (box.size[1] - text_box[1]) // 2)
        draw.multiline_text(text_box, top_text, font=top_font, fill=(0, 0, 0, 255), align="center")
        template.paste(box, (536, 0))

        # Draw bottom text
        box_size = (536, 554)
        box = Image.new("RGB", box_size, (255, 255, 255))
        draw = ImageDraw.Draw(box)
        text_box = draw.multiline_textbbox(
            (box_size[0] // 2, box_size[1] // 2), text=bottom_text, font=bottom_font, align="center"
        )
        text_box = ((box.size[0] - text_box[0]) // 2, (box.size[1] - text_box[1]) // 2)
        draw.multiline_text(text_box, bottom_text, font=bottom_font, fill=(0, 0, 0, 255), align="center")
        template.paste(box, (536, 538))

        # Save image to buffer
        output = BytesIO()
        template.save(output, format="jpeg")
        output.seek(0)

        # Send image
        await interaction.followup.send(file=discord.File(output, "sivert_goodbad.jpg"))


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): The bot instance
    """

    await bot.add_cog(Meme(bot))
