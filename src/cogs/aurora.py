from datetime import datetime
from datetime import timedelta

import discord
import requests
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks

from cogs.utils import embed_templates


class Aurora(commands.Cog):
    """Aurora Borealis forecasts and alerts"""

    def __init__(self, bot: commands.Bot):
        """
        Parameters
        ----------
        bot (commands.Bot): The bot instance
        """

        self.bot = bot

        self.NEUF_LAT = 59.9323960544179
        self.NEUF_LON = 10.712627459170472

        self.notified = datetime(2000, 9, 11)  # Used to prevent spamming aurora alerts
        self.aurora_alarm.start()

    async def get_forecast(self) -> dict | None:
        """
        Get the current aurora and cloud cover forecast for Chateau Neuf

        Returns
        -------
        (dict) The forecast data | None
            {
                "aurora_forecast_time": (str) Time the aurora forecast was made formatted as a discord timestamp
                "aurora_percentage": (int) Percentage chance of aurora
                "cloud_forecast_time": (str) Time the cloud cover forecast was made formatted as a discord timestamp
                "cloud_cover_percentage": (int) Percentage cloud cover
            }
        """

        # Get the aurora forecast data from NOAA
        forecast_data = requests.get("https://services.swpc.noaa.gov/json/ovation_aurora_latest.json").json()
        if not forecast_data:
            self.bot.logger.warning("Failed to get aurora forecast data from NOAA")
            return None
        aurora_forecast_time = forecast_data.get("Observation Time")

        # Make sure longitude is in range 0-360. For some reason we need to do this.
        # I don't know why. Maybe because I ~~stole~~ borrowed the code :P
        longitude = self.NEUF_LON % 360

        forecast_dict = {}
        for forecast_item in forecast_data["coordinates"]:
            forecast_dict[forecast_item[0], forecast_item[1]] = forecast_item[2]
        aurora_percentage = forecast_dict.get((int(longitude), int(self.NEUF_LAT)), 0)

        # Get the cloud cover data from MET Norway
        cloud_data = requests.get(
            "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=59.9323960544179&lon=10.712627459170472",
            headers={"User-Agent": "UiO Gaming Bot"},
        ).json()
        if not cloud_data:
            self.bot.logger.warning("Failed to get cloud cover data from MET Norway")
            return None

        cloud_cover = cloud_data["properties"]["timeseries"][0]["data"]["instant"]["details"]["cloud_area_fraction"]
        cloud_forecast_time = cloud_data["properties"]["timeseries"][0]["time"]

        # Convert time to discord timestamps
        try:
            aurora_forecast_time = discord.utils.format_dt(datetime.fromisoformat(aurora_forecast_time), style="R")
        except ValueError as e:
            self.bot.logger.warning(e)
            aurora_forecast_time = f"`{aurora_forecast_time}`"

        try:
            cloud_forecast_time = discord.utils.format_dt(datetime.fromisoformat(cloud_forecast_time), style="R")
        except ValueError as e:
            self.bot.logger.warning(e)
            cloud_forecast_time = f"`{cloud_forecast_time}`"

        return {
            "aurora_forecast_time": aurora_forecast_time,
            "aurora_percentage": aurora_percentage,
            "cloud_forecast_time": cloud_forecast_time,
            "cloud_cover_percentage": cloud_cover,
        }

    def get_forecast_embed(self, forecast: dict) -> discord.Embed:
        """
        Format the forecast data into a standaridized embed. DRY

        Parameters
        ----------
        forecast (dict): The forecast data
            {
                "aurora_forecast_time": (str) Time the aurora forecast was made formatted as a discord timestamp
                "aurora_percentage": (int) Percentage chance of aurora
                "cloud_forecast_time": (str) Time the cloud cover forecast was made formatted as a discord timestamp
                "cloud_cover_percentage": (int) Percentage cloud cover
            }
        """

        aurora_time = forecast.get("aurora_forecast_time")
        cloud_time = forecast.get("cloud_forecast_time")
        aurora_percentage = forecast.get("aurora_percentage")
        cloud_percentage = forecast.get("cloud_cover_percentage")

        embed = discord.Embed(title="Nordlysvarsel for Chateu Neuf", color=0x00EA8D)
        embed.description = f"Nordlysvarsel hentet: {aurora_time}\nSkydekkevarsel hentet: {cloud_time}"
        embed.add_field(name="Sjanse for å se nordlys", value=f"{aurora_percentage}%")
        embed.add_field(name="Skydekke", value=f"{cloud_percentage}%")
        embed.set_footer(text="Nordlysdata fra NOAA | Skydekkedata fra MET Norge")
        return embed

    @tasks.loop(minutes=10)
    async def aurora_alarm(self):
        """
        Checks if the aurora forecast is above 50% and sends a message to the aurora channel if it is
        """

        await self.bot.wait_until_ready()  # Make sure we can fetch the #general channel

        if datetime.now() - self.notified < timedelta(hours=12):
            self.bot.logger.info(
                "aurora_alarm: Not sending aurora alert because it has been less than 12 hours since last alert"
            )
            return

        forecast = await self.get_forecast()
        if not forecast:
            self.bot.logger.warning("aurora_alarm: Failed to get forecast data")
            return

        if forecast.get("aurora_percentage") >= 50 and forecast.get("cloud_cover_percentage") <= 50:
            channel = self.bot.get_channel(747542544291987597)
            if not channel:
                self.bot.logger.warning("aurora_alarm: Failed to get aurora channel")
                return

            embed = self.get_forecast_embed(forecast)
            await channel.send(
                content="SJANSE FOR NORDLYS AKKURAT NÅ PÅ NEUF! Se ut vinduet istedenfor på den dumme skjermen din",
                embed=embed,
            )
            self.notified = datetime.now()  # Update the last notification time

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 2)
    @app_commands.command(name="nordlys", description="Se nordlysvarselet for Neuf akkurat nå")
    async def aurora_forecast(self, interaction: discord.Interaction):
        """
        See the aurora forecast at Chateau Neuf right now

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        """

        forecast = await self.get_forecast()
        if not forecast:
            return await interaction.response.send_message(
                embed=embed_templates.error_fatal(
                    interaction,
                    text="Kunne ikke hente nordlysvarsel akkurat nå. Et av APIene feilet (ikke min feil :P)",
                )
            )

        embed = self.get_forecast_embed(forecast)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    await bot.add_cog(Aurora(bot))
