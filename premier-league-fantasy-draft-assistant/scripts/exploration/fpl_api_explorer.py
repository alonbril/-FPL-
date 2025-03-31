"""
FPL API Explorer Script

This script helps explore the Fantasy Premier League API endpoints
and evaluate the available data for the Fantasy Draft Assistant project.

Usage:
    python fpl_api_explorer.py

Functions:
    - Fetch general game information
    - Explore player data structure
    - Sample player detailed information
    - Check fixture data
    - Export sample data to CSV for analysis
"""
import requests
import json
import pandas as pd
import os
from pprint import pprint
from typing import Dict, List, Any, Optional
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure output directory exists
os.makedirs('data/raw', exist_ok=True)


class FPLExplorer:
    """Class to explore the FPL API endpoints and data structure."""

    BASE_URL = "https://fantasy.premierleague.com/api"

    def __init__(self):
        """Initialize the explorer and get basic game data."""
        self.general_data = None

    def get_general_info(self) -> Dict[str, Any]:
        """
        Fetch general game information including teams, players, and game settings.

        Returns:
            Dictionary containing the raw API response
        """
        endpoint = f"{self.BASE_URL}/bootstrap-static/"

        try:
            logger.info(f"Fetching data from {endpoint}")
            response = requests.get(endpoint)
            response.raise_for_status()
            data = response.json()

            # Save data to file
            with open('data/raw/fpl_general_info.json', 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Successfully fetched general information. Data saved to data/raw/fpl_general_info.json")
            self.general_data = data
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data: {str(e)}")
            return {}

    def list_data_categories(self) -> None:
        """List the main data categories available in the general API response."""
        if not self.general_data:
            self.get_general_info()

        if self.general_data:
            print("\nAvailable Data Categories:")
            print("==========================")
            for key, value in self.general_data.items():
                if isinstance(value, list):
                    print(f"{key}: {len(value)} items")
                else:
                    print(f"{key}: {type(value)}")

    def explore_player_data(self, sample_size: int = 1) -> None:
        """
        Explore the structure of player data.

        Args:
            sample_size: Number of players to sample
        """
        if not self.general_data:
            self.get_general_info()

        if self.general_data and 'elements' in self.general_data:
            players = self.general_data['elements']

            print(f"\nPlayer Data Structure (Sample of {sample_size}):")
            print("=====================================")
            for i in range(min(sample_size, len(players))):
                pprint(players[i])
                print("\n")

            # Show all available fields
            if players:
                print("Available Player Fields:")
                print("=======================")
                for field in players[0].keys():
                    print(f"- {field}")

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
            logger.info(f"Fetching player details for player ID {player_id}")
            response = requests.get(endpoint)
            response.raise_for_status()
            data = response.json()

            # Save data to file
            with open(f'data/raw/player_{player_id}_details.json', 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Successfully fetched details for player {player_id}")
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching player details: {str(e)}")
            return {}

    def get_fixtures(self) -> List[Dict[str, Any]]:
        """
        Fetch fixture information.

        Returns:
            List of fixture dictionaries
        """
        endpoint = f"{self.BASE_URL}/fixtures/"

        try:
            logger.info(f"Fetching fixtures from {endpoint}")
            response = requests.get(endpoint)
            response.raise_for_status()
            data = response.json()

            # Save data to file
            with open('data/raw/fixtures.json', 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Successfully fetched fixtures. Data saved to data/raw/fixtures.json")
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching fixtures: {str(e)}")
            return []

    def create_player_dataframe(self) -> pd.DataFrame:
        """
        Create a pandas DataFrame with player information.

        Returns:
            DataFrame with player data
        """
        if not self.general_data:
            self.get_general_info()

        if self.general_data and 'elements' in self.general_data:
            players = self.general_data['elements']

            # Convert to DataFrame
            df = pd.DataFrame(players)

            # Add team names instead of just IDs
            if 'teams' in self.general_data:
                teams_dict = {team['id']: team['name'] for team in self.general_data['teams']}
                df['team_name'] = df['team'].map(teams_dict)

            # Add position names instead of just IDs
            if 'element_types' in self.general_data:
                positions_dict = {pos['id']: pos['singular_name'] for pos in self.general_data['element_types']}
                df['position'] = df['element_type'].map(positions_dict)

            # Save to CSV
            df.to_csv('data/raw/fpl_players.csv', index=False)
            logger.info(f"Created player DataFrame with {len(df)} rows. Saved to data/raw/fpl_players.csv")

            return df

        return pd.DataFrame()

    def create_team_dataframe(self) -> pd.DataFrame:
        """
        Create a pandas DataFrame with team information.

        Returns:
            DataFrame with team data
        """
        if not self.general_data:
            self.get_general_info()

        if self.general_data and 'teams' in self.general_data:
            teams = self.general_data['teams']

            # Convert to DataFrame
            df = pd.DataFrame(teams)

            # Save to CSV
            df.to_csv('data/raw/fpl_teams.csv', index=False)
            logger.info(f"Created team DataFrame with {len(df)} rows. Saved to data/raw/fpl_teams.csv")

            return df

        return pd.DataFrame()

    def explore_api(self) -> None:
        """Run a comprehensive exploration of the API."""
        # Get general info
        self.get_general_info()

        # List available data categories
        self.list_data_categories()

        # Explore player data structure
        self.explore_player_data(sample_size=1)

        # Create and save player DataFrame
        players_df = self.create_player_dataframe()

        # Get sample player details
        if not players_df.empty:
            sample_player_id = players_df.iloc[0]['id']
            player_details = self.get_player_details(sample_player_id)
            print("\nSample Player Details Structure:")
            print("===============================")
            pprint(player_details)

        # Get fixtures
        fixtures = self.get_fixtures()
        if fixtures:
            print(f"\nRetrieved {len(fixtures)} fixtures")
            print("Sample fixture data:")
            pprint(fixtures[0])

        # Create team DataFrame
        self.create_team_dataframe()

        print("\nAPI exploration complete. Check the data/raw directory for exported files.")


if __name__ == "__main__":
    explorer = FPLExplorer()
    explorer.explore_api()