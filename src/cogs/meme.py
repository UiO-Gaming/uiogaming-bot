from io import BytesIO

import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image
from PIL import ImageEnhance
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


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): The bot instance
    """

    await bot.add_cog(Meme(bot))
