from discord.ext import commands
import discord

from yr.libyr import Yr
import aiocron
import json


class Vær(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        @aiocron.crontab("0 6 * * *")
        async def forecast():

            dev = await self.bot.fetch_user(162337748781367296)
            guild = self.bot.get_guild(747542543750660178)
            channel = guild.get_channel(750052141346979850)

            weather = Yr(location_name='Norway/Oslo/Oslo/Oslo', forecast_link='forecast_hour_by_hour')

            embed = discord.Embed(title=":white_sun_small_cloud: Værmelding for Oslo :white_sun_small_cloud:")
            embed.description = "*Værmeldingen levert til deg av Petter*"
            embed.set_author(name=dev.name, icon_url=dev.avatar_url)

            half_hour = False
            klokkeslett = 0
            for forecast in weather.forecast(str):
                if half_hour:
                    half_hour = False
                    continue

                data = json.loads(forecast)
                temp = data['temperature']
                rain = data['precipitation']
                regn = rain['@value']
                temperatur = temp['@value']
                embed.add_field(name=f"kl {klokkeslett}", value=f"{temperatur}°C - {regn}mm")
                klokkeslett += 1
                half_hour = True

            await channel.send("RISE AND SHINE GAMERS!", embed=embed)


def setup(bot):
    bot.add_cog(Vær(bot))
