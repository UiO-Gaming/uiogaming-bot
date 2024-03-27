import functools
import os
import textwrap
from io import BytesIO

import discord
from discord import app_commands
from discord.ext import commands
from moviepy.editor import CompositeVideoClip
from moviepy.editor import TextClip
from moviepy.editor import VideoFileClip
from PIL import Image
from PIL import ImageDraw
from PIL import ImageEnhance
from PIL import ImageFont
from PIL import UnidentifiedImageError

from cogs.utils import discord_utils
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
        input = await discord_utils.get_file_bytesio(bilde)

        # Open image
        # Check if image is valid
        try:
            image = Image.open(input)
        except UnidentifiedImageError:
            await interaction.followup.send(embed=embed_templates.error_warning("Bildet er ugyldig"))
            return

        if image.mode != "RGB":
            image = image.convert("RGB")

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
    def __draw_text(image: Image.Image, text: str, offset: tuple = (0, 0)):
        """
        Draws meme text on preferred meme template.

        Parameters
        ----------
        image (Image.Image): The meme template.
        text (str): The text to be drawn.
        font (ImageFont.FreeTypeFont): The font, with its size set, to be used.
        offset (tuple): The offset of the text from the top left corner of the image. Defaults to (0, 0).
        """

        box_size = (540, 540)
        box = Image.new("RGB", box_size, (255, 255, 255))
        draw = ImageDraw.Draw(box)

        # Using a non-mono font may cause issues but eh
        # I don't want to ship a whole ass new font just to cover edge cases for this command
        # It's rather a skill issue on my end that I can't get things to stay within bounds
        font_path = "./src/assets/fonts/comic.ttf"

        # Calculate initial font size
        # This is done by increasing the font size until the text is too wide
        max_width, max_height = box_size[0] * 0.9, box_size[1] * 0.9  # 90% of the box size

        font_size = 20  # Initiale size. I consider this the smallest readable size
        font_width = 0  # Initiale width. This is just to make sure the while loop runs at least once
        while font_width < max_width:
            font = ImageFont.truetype(font_path, font_size)

            font_box = font.getbbox(text)
            font_width = font_box[2] - font_box[0]

            font_size += 2

        # Wrap the text based on our current font size
        text = textwrap.fill(text, width=font_size)

        # We then have to calculate the font size again
        #
        # The problem is, font.getbbox() doesn't work with multiline text so it returns the size without the linebreaks
        # We can get around this by calculating the size of the longest line in the text
        # and then increasing the font size until that line is too wide
        #
        # We also have to make sure it doesn't get too tall
        longest_line = max(text.split("\n"), key=len)
        longest_line_font_box = font.getbbox(longest_line)
        font_width = longest_line_font_box[2] - longest_line_font_box[0]

        # Estimate font height
        # This is done by multiplying the height of the original non-wrapped text with the number of lines
        # and then adding 20 to account for the line spacing.
        # This of course is dependant on font size itself, but it's good enough for now
        font_height = (font_box[3] - font_box[1] + 20) * text.count("\n")
        max_height = box_size[1] * 0.9

        while font_width < max_width and font_height < max_height:
            font = ImageFont.truetype(font_path, font_size)

            longest_line_font_box = font.getbbox(longest_line)
            font_width = longest_line_font_box[2] - longest_line_font_box[0]

            font_box = font.getbbox(text)
            font_height = (font_box[3] - font_box[1] + 20) * text.count("\n")

            font_size += 2

        # Draw textbox and text
        text_box = draw.multiline_textbbox(box_size, text=text, font=font, align="center", anchor="mm")
        text_box = box.size[0] // 2, box.size[1] // 2
        draw.multiline_text(text_box, text, font=font, fill=(0, 0, 0, 255), align="center", anchor="mm")

        image.paste(box, offset)

    @app_commands.checks.bot_has_permissions(attach_files=True)
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
        template = Image.open("./src/assets/sivert_goodbad.jpg")

        # Draw text
        Meme.__draw_text(template, dårlig_tekst, offset=(540, 0))
        Meme.__draw_text(template, bra_tekst, offset=(540, 540))

        # Save image to buffer
        output = BytesIO()
        template.save(output, format="jpeg")
        output.seek(0)

        # Send image
        await interaction.followup.send(file=discord.File(output, "sivert_goodbad.jpg"))

    @app_commands.checks.bot_has_permissions(attach_files=True)
    @app_commands.checks.cooldown(1, 60)
    @app_commands.command(name="crabrave", description="Generer en crab rave video basert på tekst")
    async def crab_rave(self, interaction: discord.Interaction, topptekst: str, bunntekst: str):
        """
        Generates a crab rave video based on text

        Parameters
        ----------
        interaction (discord.Interaction): The interaction
        topptekst (str): The upper text
        bunntekst (str): The lower text
        """

        await interaction.response.defer()

        generation_task = functools.partial(Meme.make_crab, topptekst, bunntekst, interaction.user.id)
        await self.bot.loop.run_in_executor(None, generation_task)

        temp_file = f"./src/assets/temp/{interaction.user.id}_crab.mp4"
        await interaction.followup.send(file=discord.File(temp_file))
        try:
            os.remove(temp_file)
        except (FileNotFoundError, PermissionError):
            self.bot.logger.warn(f"Failed to remove temporary file {temp_file}")
            pass

    @staticmethod
    def make_crab(top_text: str, bottom_text: str, user_id: int):
        """
        Generates a crab rave video based on text
        Is it really stolen code if the copilot stole it for me?

        Parameters
        ----------
        top_text (str): The upper text
        bottom_text (str): The lower text
        user_id (int): The user ID
        """

        font_path = "DejaVu-Sans-Bold"
        clip = VideoFileClip("./src/assets/crab.mp4")

        top_part = (
            TextClip(top_text, fontsize=60, color="white", stroke_width=2, stroke_color="black", font=font_path)
            .set_start(11.0)
            .set_position(("center", 300))
            .set_duration(26.0)
        )
        middle_part = (
            TextClip(
                "____________________",
                fontsize=48,
                color="white",
                font=font_path,
            )
            .set_start(11.0)
            .set_position(("center", "center"))
            .set_duration(26.0)
        )
        bottom_part = (
            TextClip(bottom_text, fontsize=60, color="white", stroke_width=2, stroke_color="black", font=font_path)
            .set_start(11.0)
            .set_position(("center", 400))
            .set_duration(26.0)
        )

        video = CompositeVideoClip(
            [clip, top_part.crossfadein(1), middle_part.crossfadein(1), bottom_part.crossfadein(1)]
        ).set_duration(26.0)

        video.write_videofile(
            f"./src/assets/temp/{user_id}_crab.mp4", threads=1, preset="superfast", verbose=False, logger=None
        )
        clip.close()
        video.close()


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): The bot instance
    """

    await bot.add_cog(Meme(bot))
