from discord.ext import commands
from discord import app_commands

import requests
class AutoBalance(commands.Cog):
    """
    This cog implements a custom elo/rating system to easily suggest
    cs lobbies that are balanced, with some custom rules such as
    * Two highest rated players must be on different teams
    * If some players need to be on same or different teams it can be arranged
    """
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cursor = self.bot.db_connection.cursor()
        self.init_db()
        faceit_api_key = self.bot.cs2_settings.get("faceit_api_key")
        self.faceit_api_headers = faceit_api_key and {"Authorization": f"Bearer {faceit_api_key}", "content-type": "application/json"}

    async def init_db():
        pass
        # self.cursor.execute(
        #     """
        #     CREATE TABLE IF NOT EXISTS cs_elo (
        #         discord_id BIGINT PRIMARY KEY,
        #         steam_id BIGINT,
        #         faceit_id BIGINT,
        #     );
        #     """
        # )

    async def register(steam_id: str | None, faceit_username: str | None) -> None:
        pass


    def calculate_skill():
        pass
        # 1. if faceit profile and more than 5 matches played this year: faceit elo / average kd
        # 2. premier elo * average kd


    def get_faceit_elo(self, username: str):
        
        # player_data = requests.get(
        #     f"https://open.faceit.com/data/v4/players/{player_id}", 
        #     headers={"Authorization": )
        # player_data_json = player_data.json()
        pass
    

    def get_faceit_player_id(self, username: str):
        try:
            response = requests.get(
                f"https://open.faceit.com/data/v4/players?nickname={username}",
                headers=self.faceit_api_headers,
            )
            data = response.json()
            player_id = data["player_id"]
            return player_id
        except Exception as e:
            pass
            # TODO

    def get_faceit_player_info(player_id):
        pass