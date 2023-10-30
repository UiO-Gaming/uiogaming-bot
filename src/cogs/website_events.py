import asyncio
import json

import discord
import pytz
import requests
from discord.ext import commands


class WebsiteEvents(commands.Cog):
    """Miscellaneous commands that don"t fit anywhere else"""

    def __init__(self, bot: commands.Bot):
        """
        Parameters
        ----------
        bot (commands.Bot): The bot instance
        """

        self.bot = bot
        self.auth_header = {
            "Authorization": f"Bearer {self.bot.sanity['api_token']}",
            "Content-Type": "application/json",
        }
        self.api_url = (
            f"https://{self.bot.sanity['project_id']}.api.sanity.io"
            + f"/v2021-03-25/data/mutate/{self.bot.sanity['dataset']}"
        )

    async def cog_load(self):
        asyncio.create_task(self.after_ready())

    async def after_ready(self):
        """
        Wait for the bot's cache to be ready before syncing events
        """

        self.bot.logger.info("WebsiteEvents.py - Waiting for bot to be ready")
        await self.bot.wait_until_ready()
        self.bot.logger.info("WebsiteEvents.py - Ready")
        await self.sync_events()

    async def sync_events(self):
        """
        Sync events from Discord to Sanity CMS
        """

        self.bot.logger.info("WebsiteEvents.py - Syncing events to Sanity CMS")

        guild = self.bot.get_guild(self.bot.guild_id)

        for event in guild.scheduled_events:
            if event.status == discord.EventStatus.cancelled:
                await self.delete_event(event)
            elif event.status == discord.EventStatus.scheduled:
                await self.create_event(event)

        self.bot.logger.info("WebsiteEvents.py - Finished syncing events! Note errors may have occured")

    async def create_event(self, event: discord.ScheduledEvent):
        """
        Creates an event in Sanity CMS when an event is added on Discord

        Parameters
        ----------
        event (discord.ScheduledEvent): The created event
        """

        # Convert timezone to Europe/Oslo
        time = event.start_time.replace(tzinfo=pytz.utc)  # Make sure the datetime object contains the timezone info
        time = event.start_time.astimezone(pytz.timezone("Europe/Oslo"))

        document = {
            "_type": "event",
            "_id": str(event.id),
            "slug": {"_type": "slug", "current": str(event.id)},
            "title": event.name,
            "date": time.strftime("%Y-%m-%d %H:%M"),  # TODO
            "location": event.location,
            "description": event.description if len(event.description) <= 120 else f"{event.description[:115]}...",
        }

        mutation = {
            "mutations": [
                {
                    "createOrReplace": document,
                }
            ]
        }

        response = requests.post(self.api_url, headers=self.auth_header, data=json.dumps(mutation))
        if response.status_code == 200:
            self.bot.logger.info(f"WebsiteEvents.py - Created Event in Sanity with ID: {event.id}")
        else:
            self.bot.logger.error(
                f"WebsiteEvents.py - Failed to create event in Sanity with ID: {event.id}. Response: {response.text}"
            )

    async def delete_event(self, event: discord.ScheduledEvent):
        """
        Deletes an event in Sanity CMS when an event is deleted on Discord

        Parameters
        ----------
        event (discord.ScheduledEvent): The deleted event
        """

        mutation = {"mutations": [{"delete": {"id": str(event.id)}}]}

        response = requests.post(self.api_url, headers=self.auth_header, data=json.dumps(mutation))
        if response.status_code == 200:
            self.bot.logger.info(f"WebsiteEvents.py - Deleted Event in Sanity with ID: {event.id}")
        else:
            self.bot.logger.error(
                f"WebsiteEvents.py - Failed to delete event in Sanity with ID: {event.id}. Response: {response.text}"
            )


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    bot.add_listener(WebsiteEvents(bot).create_event, "on_scheduled_event_create")
    bot.add_listener(WebsiteEvents(bot).create_event, "on_scheduled_event_update")
    bot.add_listener(WebsiteEvents(bot).delete_event, "on_scheduled_event_delete")
    await bot.add_cog(WebsiteEvents(bot))
