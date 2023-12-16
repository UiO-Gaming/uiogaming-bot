from datetime import datetime
from io import BytesIO

import discord

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
