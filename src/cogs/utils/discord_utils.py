from dataclasses import dataclass
from datetime import datetime
from io import BytesIO

import discord
from discord.ext import commands

from . import embed_templates
from .misc_utils import Paginator


def get_color(discord_object: discord.User | discord.Member | discord.Role) -> discord.Color:
    """
    Returns the user's top role color

    Parameters
    -----------
    discord_object (discord.User|discord.Member|discord.Role): A discord object that has a color attribute

    Returns
    -----------
    (discord.Color): The user's displayed color
    """

    if hasattr(discord_object, "color") and str(discord_object.color) != "#000000":
        return discord_object.color

    return discord.Colour(0x99AAB5)


async def sleep_until_midnight(bot):
    """Syncs loop with the time of day"""

    await bot.wait_until_ready()

    now = datetime.datetime.now()
    if now.hour > 0:
        sleep_until = now + datetime.timedelta(days=1)
        sleep_until = sleep_until.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        sleep_until = now.replace(hour=0, minute=0, second=0, microsecond=0)

    bot.logger.info(f"Loop sleeping until {sleep_until}")

    await discord.utils.sleep_until(sleep_until)


async def get_file_bytesio(file: discord.Attachment | discord.Asset) -> BytesIO:
    """
    Returns a BytesIO object of the file

    Parameters
    -----------
    file (discord.Attatchment | discord.Asset): The file to get the BytesIO object of

    Returns
    -----------
    (BytesIO): The file as a BytesIO object
    """

    input = BytesIO()
    input.write(await file.read())
    input.seek(0)
    return input


class ScrollerButton(discord.ui.Button):
    """Button that scrolls through pages in a scroller view"""

    def __init__(
        self,
        paginator: Paginator,
        button_action: callable,
        content_constructor: callable,
        owner: discord.User | discord.Member,
        label: str,
        disabled: bool = False,
    ):
        """
        Parameters
        -----------
        paginator (Paginator): The paginator object that contains the data to be paginated
        button_action (callable): The function that returns the requested page
        content_constructor (callable): A function that takes a paginator object and a page number and returns an embed
        owner (discord.User|discord.Member): The user that invoked the paginator. Only this user can use the button
        """

        super().__init__(label=label, disabled=disabled)
        self.paginator = paginator
        self.button_action = button_action
        self.content_constructor = content_constructor
        self.owner = owner

    async def callback(self, interaction: discord.Interaction):
        """
        What to do when the button is pressed

        Parameters
        -----------
        interaction (discord.Interaction): Slash command context object
        """

        if interaction.user.id != self.owner.id:
            return await interaction.response.send_message(
                "Bare den som skrev kommandoen kan bruke denne knappen", ephemeral=True
            )

        await interaction.response.defer()

        content = self.content_constructor(self.button_action(), interaction.message.embeds[0])
        await interaction.message.edit(
            embed=content, view=Scroller(self.paginator, self.owner, self.content_constructor)
        )


class Scroller(discord.ui.View):
    """View that allows scrolling through pages of data using the pagination module"""

    def __init__(
        self, paginatior: Paginator, owner: discord.User | discord.Member, content_constructor: callable = None
    ):
        """
        Parameters
        -----------
        paginator (Paginator): The paginator object that contains the data to be paginated
        owner (discord.User|discord.Member): The user that invoked the paginator. Only this user can use the buttons
        content_constructor (callable): A function that takes a paginator object and a page number and returns an embed
        """

        super().__init__()
        self.paginator = paginatior
        self.content_constructor = content_constructor if content_constructor else self.__default_content_constructor

        self.add_item(
            ScrollerButton(
                self.paginator,
                self.paginator.first_page,
                self.content_constructor,
                owner,
                label="<<",
                disabled=self.paginator.current_page == 1,
            )
        )
        self.add_item(
            ScrollerButton(
                self.paginator,
                self.paginator.previous_page,
                self.content_constructor,
                owner,
                label="<",
                disabled=self.paginator.current_page == 1,
            )
        )
        self.add_item(
            ScrollerButton(
                self.paginator,
                self.paginator.next_page,
                self.content_constructor,
                owner,
                label=">",
                disabled=self.paginator.current_page == self.paginator.total_page_count,
            )
        )
        self.add_item(
            ScrollerButton(
                self.paginator,
                self.paginator.last_page,
                self.content_constructor,
                owner,
                label=">>",
                disabled=self.paginator.current_page == self.paginator.total_page_count,
            )
        )


@dataclass
class Lobby:
    host: discord.User
    players: list[discord.User]
    ends: datetime
    kicked_players: list[discord.User]


class LobbyView(discord.ui.View):
    def __init__(self, lobby: Lobby, bot: commands.Bot):
        lobby_end = (lobby.ends - datetime.now()).total_seconds()
        super().__init__(timeout=lobby_end)

        self.lobby = lobby
        self.bot = bot

        self.add_item(_KickSelectMenu(self))

    async def on_timeout(self):
        await self.end_lobby()

    async def end_lobby(self):
        self.lobby.ends = datetime.now()
        for item in self.children:
            item.disabled = True

    async def rerender_players(self, interaction: discord.Interaction):
        self.children[-1].options = [
            discord.SelectOption(label=p.display_name, value=str(p.id), emoji="🔨") for p in self.lobby.players
        ]
        embed = interaction.message.embeds[0].set_field_at(
            0, name="Spillere", value="\n".join([f"* {p.mention}" for p in self.lobby.players])
        )
        await interaction.message.edit(embed=embed, view=self)

    @discord.ui.button(label="Bli med", style=discord.ButtonStyle.blurple)
    async def join_lobby(self, interaction: discord.Interaction, button: discord.ui.Button):
        if datetime.now() > self.lobby.ends:
            embed = embed_templates.error_warning(interaction, text="Lobbyen har allerede startet")
            return await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

        if (
            interaction.user.id in self.lobby.kicked_players
        ):  # We have to use the ID here to avoid fetching the member object in the selection menu
            embed = embed_templates.error_warning(interaction, text="Du er blitt kastet ut av lobbyen")
            return await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

        if interaction.user in self.lobby.players:
            embed = embed_templates.error_warning(interaction, text="Du er allerede i lobbyen")
            return await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

        if len(self.lobby.players) >= 10:
            embed = embed_templates.error_warning(interaction, text="Lobbyen er full")
            return await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

        self.lobby.players.append(interaction.user)
        await self.rerender_players(interaction)

        embed = embed_templates.success(interaction, text="Du har blitt med i lobbyen")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)

    @discord.ui.button(label="Start", style=discord.ButtonStyle.green)
    async def start_lobby(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.lobby.host:
            embed = embed_templates.error_warning(interaction, text="Bare hosten kan starte")
            return await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

        await self.end_lobby()

        embed = interaction.message.embeds[0]
        embed.description = "Lobbyen har startet!"
        await interaction.message.edit(embed=embed, view=self)

    @discord.ui.button(label="Forlat", style=discord.ButtonStyle.gray)
    async def leave_lobby(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.lobby.host:
            embed = embed_templates.error_warning(
                interaction, text="Du kan ikke forlate lobbyen som host. Slett lobbyen i stedet om ønskelig!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

        if interaction.user not in self.lobby.players:
            embed = embed_templates.error_warning(interaction, text="Du er ikke i lobbyen")
            return await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

        self.lobby.players.remove(interaction.user)
        await self.rerender_players(interaction)

        embed = embed_templates.success(interaction, text="Du har forlatt lobbyen")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)

    @discord.ui.button(label="Slett", style=discord.ButtonStyle.red)
    async def delete_lobby(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.lobby.host:
            embed = embed_templates.error_warning(interaction, text="Bare hosten kan slette lobbyen")
            return await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

        self.lobby.ends = datetime.now()
        await interaction.message.delete()

        embed = embed_templates.success(interaction, text="Lobbyen har blitt slettet")
        await interaction.response.send_message(embed=embed, delete_after=5)


class _KickSelectMenu(discord.ui.Select):
    def __init__(self, parent_view: LobbyView):
        self.parent_view = parent_view
        options = [
            discord.SelectOption(label=p.display_name, value=str(p.id), emoji="🔨", description=f"Kick {p.display_name}")
            for p in self.parent_view.lobby.players
        ]
        super().__init__(placeholder="Kick en spiller", max_values=1, min_values=1, options=options)

    # TODO: DRY
    async def rerender_players(self, interaction: discord.Interaction):
        self.options = [
            discord.SelectOption(label=p.display_name, value=str(p.id), emoji="🔨")
            for p in self.parent_view.lobby.players
        ]
        embed = interaction.message.embeds[0].set_field_at(
            0, name="Spillere", value="\n".join([f"* {p.mention}" for p in self.parent_view.lobby.players])
        )
        await interaction.message.edit(embed=embed, view=self.parent_view)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.parent_view.lobby.host:
            embed = embed_templates.error_warning(interaction, text="Bare hosten kan kicke spillere")
            return await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

        if str(interaction.user.id) in interaction.data["values"][0]:
            embed = embed_templates.error_warning(interaction, text="Du kan ikke kicke deg selv")
            return await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

        self.parent_view.lobby.kicked_players.append(int(interaction.data["values"][0]))

        # Remove the player from the lobby
        # Since we only have the ID, we have to iterate through the list
        # unless we want to fetch the member object from the API
        # which we don't :)
        for i, member in enumerate(self.parent_view.lobby.players):
            if member.id == int(interaction.data["values"][0]):
                self.parent_view.lobby.players.pop(i)
                break

        await self.rerender_players(interaction)

        embed = embed_templates.success(interaction, text="Brukeren har blitt sparket fra lobbyen")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)


def construct_embed(self, base_embed: discord.Embed):
    """
    Constructs the embed to be displayed

    Parameters
    -----------
    base_embed (discord.Embed): The base embed to add fields to
    """

    return self.content_constructor(self.paginator.get_current_page(), embed=base_embed)


def __default_content_constructor(self, page: list, embed: discord.Embed) -> discord.Embed:
    """
    Default embed template for the paginator

    Parameters
    ----------
    paginator (Paginator): Paginator dataclass
    page (list): List of streaks to display on a page
    embed (discord.Embed): Embed to add fields to
    """

    embed.description = "\n".join(page)
    embed.set_footer(text=f"Side {self.paginator.current_page}/{self.paginator.total_page_count}")
    return embed
