"""
Fantasy Premier League API data collector module.
Handles fetching player data from the official FPL API.
"""
import requests
import logging
import pandas as pd
from typing import Dict, List, Any, Optional
import asyncio
import aiohttp
from fpl import FPL

logger = logging.getLogger(__name__)


class FPLApiClient:
    """Client for interacting with the official Fantasy Premier League API."""

    BASE_URL = "https://fantasy.premierleague.com/api"

    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        """
        Initialize the FPL API client.

        Args:
            session: Optional aiohttp session for authenticated requests
        """
        self.session = session
        logger.info(f"Initialized FPL API client")

    def get_general_info(self) -> Dict[str, Any]:
        """
        Fetch general game information.

        Returns:
            Dictionary containing game settings, teams, and basic player info
        """
        endpoint = f"{self.BASE_URL}/bootstrap-static/"

        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            data = response.json()

            logger.info("Successfully fetched general information from FPL API")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching general information from FPL API: {e}")
            return {}

    def get_player_details(self, player_id: int) -> Dict[str, Any]:
        """
        Fetch detailed information for a specific player.

        Args:
            player_id: FPL player ID

        Returns:
            Dictionary with detailed player data
        """
        endpoint = f"{self.BASE_URL}/element-summary/{player_id}/"

        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            data = response.json()

            logger.info(f"Successfully fetched details for player {player_id}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching details for player {player_id}: {e}")
            return {}

    def get_all_players(self) -> pd.DataFrame:
        """
        Fetch all available players and return as a DataFrame.

        Returns:
            DataFrame with player data
        """
        data = self.get_general_info()

        if not data or 'elements' not in data:
            logger.error("Failed to retrieve player data from FPL API")
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(data['elements'])

        # Add team names instead of just IDs
        if 'teams' in data:
            teams_dict = {team['id']: team['name'] for team in data['teams']}
            df['team_name'] = df['team'].map(teams_dict)

        # Add position names instead of just IDs
        if 'element_types' in data:
            positions_dict = {pos['id']: pos['singular_name'] for pos in data['element_types']}
            df['position'] = df['element_type'].map(positions_dict)

        logger.info(f"Retrieved {len(df)} players from FPL API")
        return df

    async def get_player_history_async(self, player_ids: List[int]) -> Dict[int, Dict]:
        """
        Asynchronously fetch detailed history for multiple players.

        Args:
            player_ids: List of FPL player IDs

        Returns:
            Dictionary mapping player IDs to their history data
        """
        if self.session is None:
            self.session = aiohttp.ClientSession()
            should_close_session = True
        else:
            should_close_session = False

        async def fetch_player(player_id):
            url = f"{self.BASE_URL}/element-summary/{player_id}/"
            async with self.session.get(url) as response:
                if response.status == 200:
                    return player_id, await response.json()
                else:
                    logger.error(f"Error fetching player {player_id}: {response.status}")
                    return player_id, {}

        tasks = [fetch_player(player_id) for player_id in player_ids]
        results = await asyncio.gather(*tasks)

        if should_close_session:
            await self.session.close()

        return dict(results)

    def enrich_player_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich player DataFrame with additional metrics and calculations.

        Args:
            df: DataFrame with base player data

        Returns:
            Enriched DataFrame with additional metrics
        """
        if df.empty:
            return df

        # Calculate points per game if not already present
        if 'total_points' in df.columns and 'minutes' in df.columns:
            df['points_per_90'] = df.apply(
                lambda row: (row['total_points'] / row['minutes']) * 90 if row['minutes'] > 0 else 0,
                axis=1
            )

        # Calculate value (points per cost)
        if 'total_points' in df.columns and 'now_cost' in df.columns:
            df['value'] = df.apply(
                lambda row: row['total_points'] / (row['now_cost'] / 10) if row['now_cost'] > 0 else 0,
                axis=1
            )

        return df

    def get_fixtures(self) -> List[Dict[str, Any]]:
        """
        Fetch all fixture data for the current season.

        Returns:
            List of fixture dictionaries
        """
        endpoint = f"{self.BASE_URL}/fixtures/"

        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            data = response.json()

            logger.info(f"Successfully fetched {len(data)} fixtures")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching fixtures: {e}")
            return []

    def get_gameweek_data(self, gameweek: int) -> Dict[str, Any]:
        """
        Fetch data for a specific gameweek.

        Args:
            gameweek: Gameweek number

        Returns:
            Dictionary with gameweek data
        """
        endpoint = f"{self.BASE_URL}/event/{gameweek}/live/"

        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            data = response.json()

            logger.info(f"Successfully fetched data for gameweek {gameweek}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching gameweek data: {e}")
            return {}


# Example usage
async def example_usage():
    """Example of how to use the FPL API client."""
    async with aiohttp.ClientSession() as session:
        # For authenticated requests (optional)
        fpl = FPL(session)
        # await fpl.login(email="your@email.com", password="your_password")

        # Create client
        client = FPLApiClient(session)

        # Get all players
        players_df = client.get_all_players()
        print(f"Retrieved {len(players_df)} players")

        # Get history for a few players
        if not players_df.empty:
            sample_ids = players_df['id'].head(5).tolist()
            histories = await client.get_player_history_async(sample_ids)
            print(f"Retrieved history for {len(histories)} players")


if __name__ == "__main__":
    # Run the async example
    asyncio.run(example_usage())