import functools
import os
from io import BytesIO

import cv2
import discord
import numpy as np
from discord import app_commands
from discord.ext import commands
from moviepy.editor import CompositeVideoClip
from moviepy.editor import TextClip
from moviepy.editor import VideoFileClip
from PIL import Image
from PIL import ImageEnhance
from PIL import UnidentifiedImageError

from cogs.utils import discord_utils
from cogs.utils import embed_templates
from cogs.utils import misc_utils


class Meme(commands.Cog):
    """Generate memes"""

    def __init__(self, bot: commands.Bot):
        """
        Parameters
        ----------
        bot (commands.Bot): The bot instance
        """

        self.bot = bot

    @app_commands.checks.bot_has_permissions(attach_files=True)
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
        input_image = await discord_utils.get_file_bytesio(bilde)

        try:
            image = Image.open(input_image)
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
        template = cv2.imread("./src/assets/sivert_goodbad.jpg")

        # Draw text
        font = "./src/assets/fonts/comic.ttf"
        await misc_utils.put_text_in_box(template, dårlig_tekst, (540, 0), (1080, 540), font)
        await misc_utils.put_text_in_box(template, bra_tekst, (540, 540), (1080, 1080), font)

        # Save image to buffer
        _, buffer = cv2.imencode(".jpg", template)
        output = BytesIO(buffer)
        cv2.imdecode(np.frombuffer(output.getbuffer(), np.uint8), -1)
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
