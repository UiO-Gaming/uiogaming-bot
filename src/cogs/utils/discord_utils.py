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
        label: str,
        disabled: bool = False,
    ):
        """
        Parameters
        -----------
        paginator (Paginator): The paginator object that contains the data to be paginated
        button_action (callable): The function that returns the requested page
        content_constructor (callable): A function that takes a paginator object and a page number and returns an embed
        """

        super().__init__(label=label, disabled=disabled)
        self.paginator = paginator
        self.button_action = button_action
        self.content_constructor = content_constructor

    async def callback(self, interaction: discord.Interaction):
        """
        What to do when the button is pressed

        Parameters
        -----------
        interaction (discord.Interaction): Slash command context object
        """

        await interaction.response.defer()
        content = self.content_constructor(self.paginator, self.button_action(), interaction.message.embeds[0])
        await interaction.message.edit(embed=content, view=Scroller(self.paginator, self.content_constructor))


class Scroller(discord.ui.View):
    """View that allows scrolling through pages of data using the pagination module"""

    def __init__(self, paginatior: Paginator, content_constructor: callable):
        """
        Parameters
        -----------
        paginator (Paginator): The paginator object that contains the data to be paginated
        content_constructor (callable): A function that takes a paginator object and a page number and returns an embed
        """

        super().__init__()
        self.paginator = paginatior

        self.add_item(
            ScrollerButton(
                self.paginator,
                self.paginator.first_page,
                content_constructor,
                label="<<",
                disabled=self.paginator.current_page == 1,
            )
        )
        self.add_item(
            ScrollerButton(
                self.paginator,
                self.paginator.previous_page,
                content_constructor,
                label="<",
                disabled=self.paginator.current_page == 1,
            )
        )
        self.add_item(
            ScrollerButton(
                self.paginator,
                self.paginator.next_page,
                content_constructor,
                label=">",
                disabled=self.paginator.current_page == self.paginator.total_page_count,
            )
        )
        self.add_item(
            ScrollerButton(
                self.paginator,
                self.paginator.last_page,
                content_constructor,
                label=">>",
                disabled=self.paginator.current_page == self.paginator.total_page_count,
            )
        )
