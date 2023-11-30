import asyncio
import json
import random
import textwrap
from datetime import datetime
from datetime import timedelta

import cv2
import discord
import numpy as np
from discord import app_commands
from discord.ext import commands
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from cogs.utils import discord_utils
from cogs.utils import embed_templates


class CS2Bingo(commands.Cog):
    """Join lobbies and generate bingo sheets for CS2"""

    def __init__(self, bot: commands.Bot):
        """
        Parameters
        ----------
        bot (commands.Bot): The bot instance
        """

        self.bot = bot
        self.active_lobbies = {}

    bingo_group = app_commands.Group(name="cs2bingo", description="Bingo commands for CS2")

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 10)
    @bingo_group.command(name="lag", description="Lag en bingolobby")
    async def bingo_create(self, interaction: discord.Interaction):
        """
        Create a bingo lobby

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        """

        if lobby := self.active_lobbies.get(str(interaction.user.id), None):
            if lobby["ends"] < datetime.now():
                self.active_lobbies.pop(str(interaction.user.id))
            else:
                return await interaction.response.send_message(
                    embed=embed_templates.error_warning(
                        interaction,
                        text="Du hoster allerede en lobby",
                    )
                )

        for lobby in self.active_lobbies.values():
            if interaction.user.id in lobby["players"]:
                return await interaction.response.send_message(
                    embed=embed_templates.error_warning(
                        interaction,
                        text="Du er allerede i en lobby",
                    )
                )

        self.active_lobbies[str(interaction.user.id)] = {
            "host": interaction.user,
            "players": [interaction.user],
            "ends": datetime.now() + timedelta(minutes=10),
            "kicked_players": [],
        }

        time_left = discord.utils.format_dt(self.active_lobbies[str(interaction.user.id)]["ends"], "R")

        embed = discord.Embed(
            title="Bingolobby",
            description=f"Lobbyen stenger {time_left}. Bli med innen da!",
            color=discord_utils.get_color(interaction.user),
        )
        embed.set_author(name=interaction.user.global_name, icon_url=interaction.user.avatar)
        embed.add_field(name="Spillere", value=f"* {interaction.user.mention}", inline=False)
        await interaction.response.send_message(
            embed=embed, view=BingoView(self.active_lobbies[str(interaction.user.id)], self.bot)
        )


class BingoGenerator:
    """
    Generate bingo sheets for CS2
    """

    FONT_PATH = "./src/assets/fonts/comic.ttf"
    BINGO_PATH = "./src/assets/cs2_bingo"

    with open(f"{BINGO_PATH}/cells.json") as f:
        CELLS = json.load(f)

    with open(f"{BINGO_PATH}/names.json") as f:
        NAMES = json.load(f)

    @classmethod
    async def put_text_in_box(
        cls,
        image: np.ndarray,
        text: str,
        top_left: tuple,
        bottom_right: tuple,
        font_path: str,
        font_size: int = 10,
        color: tuple = (0, 0, 0),
    ):
        """
        Puts text inside a bounding box on the cv2 image with automatic text wrapping, using PIL for text rendering.

        :param image: Source cv2 image (numpy array).
        :param text: Text string to be put.
        :param top_left: Tuple (x, y) defining the top-left corner of the bounding box.
        :param bottom_right: Tuple (x, y) defining the bottom-right corner of the bounding box.
        :param font_path: Path to a .ttf font file.
        :param font_size: Initial font size.
        :param color: Text color in RGB.
        :return: Image with text (numpy array).
        """

        # TODO: Dry. This algorithm is also seen in the memes cog

        # Convert the cv2 image to a PIL image
        image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image_pil)

        # Get coordinates of the bounding box
        x1, y1 = top_left
        x2, y2 = bottom_right

        # Get the width and height of the bounding box
        # We multiply by 0.9 to give some padding
        w, h = (x2 - x1) * 0.9, (y2 - y1) * 0.9

        # Initialize font width/height to 0 in order to run the while loops below at least once
        font_width = 0
        font_height = 0

        # Add newlines to the text. Here we have gone with 15 characters per line
        # This is arbitrary, but seems to work well
        text = textwrap.fill(text, width=15)

        # Increase the font size until the longest line of text does not fit in the bounding box anymore
        # We also have to check the height, since the text might be too tall for the box
        while font_width < w and font_height < h:
            font = ImageFont.truetype(font_path, font_size)

            longest_line = max(text.split("\n"), key=lambda x: font.getlength(x))
            font_width = font.getlength(longest_line)

            # bbox doesn't work with multiline text, so we have to calculate the height manually
            # take the height of the bounding box, multiply by 1.5 (our assumed line dividor height)
            # after that, we multiply by the number of lines
            font_box = font.getbbox(text)
            font_height = ((font_box[3] - font_box[1]) * 1.5) * text.count("\n")

            font_size += 1

        # Actually draw the text
        draw.multiline_textbbox((w, h), text=text, font=font, align="center", anchor="mm")
        center_of_box = ((x1 + x2) // 2, (y1 + y2) // 2)
        draw.multiline_text(center_of_box, text, font=font, fill=color, align="center", anchor="mm")

        # Convert back to cv2 image format and update the original image
        cv2_image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
        np.copyto(image, cv2_image)

    @classmethod
    async def sample_cells(cls, players: list[str], bot: commands.Bot) -> dict[str, list[str]]:
        assert 0 < len(players) <= 10

        default_space = cls.CELLS["all"]

        if len(players) < 5:
            default_space += cls.CELLS["randoms"]

        player_cells = {}

        for player in players:
            other_players = players.copy()
            other_players.remove(player)
            player_space = default_space + [i for op in other_players for i in cls.CELLS.get(op, [])]
            other_players.append("du")

            other_players_names = [
                cls.NAMES.get(op, bot.get_user(int(op)).display_name) if op != "du" else op for op in other_players
            ]
            player_space += [s.format(random.choice(other_players_names)) for s in cls.CELLS["parameterized"]]

            sampled_cells = np.random.choice(player_space, replace=False, size=25)
            player_cells[player] = list(sampled_cells)

        return player_cells

    @classmethod
    async def generate_sheets(cls, players: list[discord.Member], bot: commands.Bot):
        """
        Generate bingo sheets for each player

        Parameters
        ----------
        players (list[str]): List of the player's discord IDs as strings
        """

        players = [str(p.id) for p in players]

        sample_space = await cls.sample_cells(players, bot)
        assert len(sample_space) == len(players)
        image = cv2.imread(f"{cls.BINGO_PATH}/cs2_bingo_sheet.png")

        player_sheets = {}

        for player in players:
            player_sheets[player] = await cls.generate_sheet(sample_space[player], image)

        for p, sheet in player_sheets.items():
            cv2.imwrite(f"./src/assets/temp/{p}_bingo.png", sheet)

    @classmethod
    async def generate_sheet(cls, sample_space: list, image: np.ndarray):
        image = image.copy()

        # start = 8, 294
        # end = 625, 910

        sliced = image[295:910, 10:625]
        # patches = []

        for i in range(0, 5):
            for j in range(0, 5):
                width = 123
                await cls.put_text_in_box(
                    sliced,
                    sample_space.pop(),
                    (i * width + 1, j * width + 1),
                    ((i + 1) * width, (j + 1) * width),
                    font_path=cls.FONT_PATH,
                )

        return image


class BingoView(discord.ui.View):
    def __init__(self, lobby: dict, bot: commands.Bot):
        lobby_end = (lobby.get("ends") - datetime.now()).total_seconds()
        super().__init__(timeout=lobby_end)

        self.lobby = lobby
        self.bot = bot

        self.add_item(KickSelectMenu(self))

    async def on_timeout(self):
        await self.end_lobby()

    async def end_lobby(self):
        self.lobby["ends"] = datetime.now()
        for item in self.children:
            item.disabled = True

    async def rerender_players(self, interaction: discord.Interaction):
        self.children[-1].options = [
            discord.SelectOption(label=p.display_name, value=str(p.id), emoji="🔨") for p in self.lobby["players"]
        ]
        embed = interaction.message.embeds[0].set_field_at(
            0, name="Spillere", value="\n".join([f"* {p.mention}" for p in self.lobby["players"]])
        )
        await interaction.message.edit(embed=embed, view=self)

    @discord.ui.button(label="Bli med", style=discord.ButtonStyle.blurple)
    async def join_lobby(self, interaction: discord.Interaction, button: discord.ui.Button):
        if datetime.now() > self.lobby["ends"]:
            embed = embed_templates.error_warning(interaction, text="Lobbyen har allerede startet")
            return await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

        if (
            interaction.user.id in self.lobby["kicked_players"]
        ):  # We have to use the ID here to avoid fetching the member object in the selection menu
            embed = embed_templates.error_warning(interaction, text="Du er blitt sparket fra lobbyen")
            return await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

        if interaction.user in self.lobby["players"]:
            embed = embed_templates.error_warning(interaction, text="Du er allerede i lobbyen")
            return await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

        if len(self.lobby["players"]) >= 10:
            embed = embed_templates.error_warning(interaction, text="Lobbyen er full")
            return await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

        self.lobby["players"].append(interaction.user)
        await self.rerender_players(interaction)

        embed = embed_templates.success(interaction, text="Du har blitt med i lobbyen")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)

    @discord.ui.button(label="Start", style=discord.ButtonStyle.green)
    async def start_lobby(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.lobby["host"]:
            embed = embed_templates.error_warning(interaction, text="Bare hosten kan starte bingoen")
            return await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

        await self.end_lobby()

        embed = interaction.message.embeds[0]
        embed.description = "Bingoen har startet!"
        await interaction.message.edit(embed=embed, view=self)

        mention_players = " ".join([f"{p.mention}" for p in self.lobby["players"]])
        embed = embed_templates.success(
            interaction,
            text="Bingoen har startet\n\nDere vil nå få tilsendt bingobrettene deres på DM. "
            + "Sørg for at jeg kan slide inn i dem :smirk:",
        )
        await interaction.response.send_message(content=mention_players, embed=embed)

        await BingoGenerator.generate_sheets(self.lobby["players"], self.bot)
        for player in self.lobby["players"]:
            try:
                await player.send(file=discord.File(f"./src/assets/temp/{player.id}_bingo.png"))
            except discord.Forbidden:
                await interaction.followup.send(
                    f"{player.mention} har ikke åpnet DM-ene sine :angry:\nSender den her i stedet",
                    file=discord.File(
                        f"./src/assets/temp/{player.id}_bingo.png", filename=f"SPOILER_{player.id}_bingo.png"
                    ),
                )
            finally:
                await asyncio.sleep(1)

    @discord.ui.button(label="Forlat", style=discord.ButtonStyle.gray)
    async def leave_lobby(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.lobby["host"]:
            embed = embed_templates.error_warning(
                interaction, text="Du kan ikke forlate lobbyen som host. Slett lobbyen i stedet om ønskelig!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

        if interaction.user not in self.lobby["players"]:
            embed = embed_templates.error_warning(interaction, text="Du er ikke i lobbyen")
            return await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

        self.lobby["players"].remove(interaction.user)
        await self.rerender_players(interaction)

        embed = embed_templates.success(interaction, text="Du har forlatt lobbyen")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)

    @discord.ui.button(label="Slett", style=discord.ButtonStyle.red)
    async def delete_lobby(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.lobby["host"]:
            embed = embed_templates.error_warning(interaction, text="Bare hosten kan slette lobbyen")
            return await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

        self.lobby["ends"] = datetime.now()
        await interaction.message.delete()

        embed = embed_templates.success(interaction, text="Lobbyen har blitt slettet")
        await interaction.response.send_message(embed=embed, delete_after=5)


class KickSelectMenu(discord.ui.Select):
    def __init__(self, parent_view: BingoView):
        self.parent_view = parent_view
        options = [
            discord.SelectOption(label=p.display_name, value=str(p.id), emoji="🔨", description=f"Kick {p.display_name}")
            for p in self.parent_view.lobby["players"]
        ]
        super().__init__(placeholder="Kick en spiller", max_values=1, min_values=1, options=options)

    # TODO: DRY
    async def rerender_players(self, interaction: discord.Interaction):
        self.options = [
            discord.SelectOption(label=p.display_name, value=str(p.id), emoji="🔨")
            for p in self.parent_view.lobby["players"]
        ]
        embed = interaction.message.embeds[0].set_field_at(
            0, name="Spillere", value="\n".join([f"* {p.mention}" for p in self.parent_view.lobby["players"]])
        )
        await interaction.message.edit(embed=embed, view=self.parent_view)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.parent_view.lobby["host"]:
            embed = embed_templates.error_warning(interaction, text="Bare hosten kan kicke spillere")
            return await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

        if str(interaction.user.id) in interaction.data["values"][0]:
            embed = embed_templates.error_warning(interaction, text="Du kan ikke kicke deg selv")
            return await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

        self.parent_view.lobby["kicked_players"].append(int(interaction.data["values"][0]))

        # Remove the player from the lobby
        # Since we only have the ID, we have to iterate through the list
        # unless we want to fetch the member object from the API
        # which we don't :)
        for i, member in enumerate(self.parent_view.lobby["players"]):
            if member.id == int(interaction.data["values"][0]):
                self.parent_view.lobby["players"].pop(i)
                break

        await self.rerender_players(interaction)

        embed = embed_templates.success(interaction, text="Brukeren har blitt kicket fra lobbyen")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    await bot.add_cog(CS2Bingo(bot))
