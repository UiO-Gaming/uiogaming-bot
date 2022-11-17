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
    if hasattr(discord_object, "color") and str(discord_object.color) != '#000000':
        return discord_object.color

    return discord.Colour(0x99AAB5)


class ScrollerButton(discord.ui.Button):
    def __init__(self, paginator: Paginator, button_action: callable, content_constructor: callable, label: str, disabled: bool = False):
        super().__init__(label=label, disabled=disabled)
        self.paginator = paginator
        self.button_action = button_action
        self.content_constructor = content_constructor

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        content = self.content_constructor(self.paginator, self.button_action(), interaction.message.embeds[0])
        await interaction.message.edit(embed=content, view=Scroller(self.paginator, self.content_constructor))


class Scroller(discord.ui.View):
    def __init__(self, paginatior: Paginator, content_constructor: callable):
        super().__init__()
        self.paginator = paginatior

        self.add_item(ScrollerButton(self.paginator, self.paginator.first_page, content_constructor, label='<<', disabled=True if self.paginator.current_page == 1 else False))
        self.add_item(ScrollerButton(self.paginator, self.paginator.previous_page, content_constructor, label='<', disabled=True if self.paginator.current_page == 1 else False))
        self.add_item(ScrollerButton(self.paginator, self.paginator.next_page, content_constructor, label='>', disabled=True if self.paginator.current_page == self.paginator.total_page_count else False))
        self.add_item(ScrollerButton(self.paginator, self.paginator.last_page, content_constructor, label='>>', disabled=True if self.paginator.current_page == self.paginator.total_page_count else False))
