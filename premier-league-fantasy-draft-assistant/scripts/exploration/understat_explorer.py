"""
Understat Explorer Script

This script helps explore the Understat website to extract advanced football statistics
such as Expected Goals (xG) and Expected Assists (xA) for Premier League players.

Since Understat doesn't have an official API, this script demonstrates web scraping
techniques to extract the embedded JSON data from the HTML.

Usage:
    python understat_explorer.py

Functions:
    - Fetch league player data
    - Extract player statistics
    - Sample individual player data
    - Export to CSV for analysis
"""
import requests
import json
import pandas as pd
import os
import re
import time
from bs4 import BeautifulSoup
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


class UnderstatExplorer:
    """Class to explore Understat data through web scraping."""

    BASE_URL = "https://understat.com"

    def __init__(self, league: str = "epl", season: str = "2023"):
        """
        Initialize the explorer with league and season.

        Args:
            league: League code (epl, la_liga, bundesliga, serie_a, ligue_1, rfpl)
            season: Season (e.g., 2023 for 2023/2024 season)
        """
        self.league = league
        self.season = season
        logger.info(f"Initialized Understat explorer for {league} season {season}")

    def _extract_json_data(self, html_text: str, variable_name: str) -> Dict:
        """
        Extract JSON data embedded in HTML using regex.

        Args:
            html_text: HTML content as string
            variable_name: JavaScript variable name containing the data

        Returns:
            Parsed JSON data
        """
        pattern = re.compile(f"var {variable_name} = JSON.parse\\('(.*?)'\\);")
        match = pattern.search(html_text)
        if match:
            json_str = match.group(1).encode('utf-8').decode('unicode_escape')
            return json.loads(json_str)
        return {}

    def get_league_players(self) -> pd.DataFrame:
        """
        Fetch player statistics for the specified league and season.

        Returns:
            DataFrame with player statistics
        """
        url = f"{self.BASE_URL}/league/{self.league}/{self.season}"

        try:
            logger.info(f"Fetching player data from {url}")
            response = requests.get(url)
            response.raise_for_status()

            # Extract the embedded JSON data
            players_data = self._extract_json_data(response.text, "playersData")

            if not players_data:
                logger.error("Failed to extract player data from Understat")
                return pd.DataFrame()

            # Save raw data
            with open(f'data/raw/understat_{self.league}_{self.season}_players.json', 'w') as f:
                json.dump(players_data, f, indent=2)

            # Convert to DataFrame
            df = pd.DataFrame(players_data)

            # Convert numeric columns
            numeric_cols = ['games', 'time', 'goals', 'assists', 'shots', 'key_passes',
                            'yellow_cards', 'red_cards', 'xG', 'xA', 'npg', 'npxG']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # Save to CSV
            df.to_csv(f'data/raw/understat_{self.league}_{self.season}_players.csv', index=False)

            logger.info(f"Retrieved {len(df)} players from Understat. Data saved to CSV and JSON.")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching players from Understat: {e}")
            return pd.DataFrame()

    def get_player_stats(self, player_id: str) -> Dict[str, Any]:
        """
        Fetch detailed statistics for a specific player.

        Args:
            player_id: Understat player ID

        Returns:
            Dictionary with player match data
        """
        url = f"{self.BASE_URL}/player/{player_id}"

        try:
            logger.info(f"Fetching player stats for player ID {player_id}")
            response = requests.get(url)
            response.raise_for_status()

            # Extract the embedded JSON data
            player_data = self._extract_json_data(response.text, "playersData")
            match_data = self._extract_json_data(response.text, "matchesData")

            result = {
                'player_info': player_data,
                'matches': match_data
            }

            # Save to file
            with open(f'data/raw/understat_player_{player_id}.json', 'w') as f:
                json.dump(result, f, indent=2)

            logger.info(f"Retrieved detailed stats for player {player_id}")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching stats for player {player_id}: {e}")
            return {}

    def get_team_players(self, team_name: str) -> pd.DataFrame:
        """
        Fetch statistics for all players in a specific team.

        Args:
            team_name: Team name exactly as it appears on Understat

        Returns:
            DataFrame with team player statistics
        """
        url = f"{self.BASE_URL}/team/{team_name}/{self.season}"

        try:
            logger.info(f"Fetching team data for {team_name}")
            response = requests.get(url)
            response.raise_for_status()

            # Extract the embedded JSON data
            players_data = self._extract_json_data(response.text, "playersData")

            if not players_data:
                logger.error(f"Failed to extract player data for team {team_name}")
                return pd.DataFrame()

            # Save raw data
            with open(f'data/raw/understat_team_{team_name}_{self.season}.json', 'w') as f:
                json.dump(players_data, f, indent=2)

            # Convert to DataFrame
            df = pd.DataFrame(players_data)

            # Save to CSV
            df.to_csv(f'data/raw/understat_team_{team_name}_{self.season}.csv', index=False)

            logger.info(f"Retrieved {len(df)} players for {team_name} from Understat")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching players for team {team_name}: {e}")
            return pd.DataFrame()

    def explore_website_structure(self) -> Dict[str, Any]:
        """
        Explore the structure of the Understat website and document available data.

        Returns:
            Dictionary with website structure information
        """
        structure = {
            'leagues': ['epl', 'la_liga', 'bundesliga', 'serie_a', 'ligue_1', 'rfpl'],
            'seasons': ['2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023'],
            'url_patterns': {
                'league': f"{self.BASE_URL}/league/{{league}}/{{season}}",
                'team': f"{self.BASE_URL}/team/{{team}}/{{season}}",
                'player': f"{self.BASE_URL}/player/{{player_id}}",
                'match': f"{self.BASE_URL}/match/{{match_id}}"
            },
            'data_variables': {
                'league_page': ['playersData', 'teamsData', 'datesData'],
                'team_page': ['playersData', 'datesData', 'matchesData'],
                'player_page': ['playersData', 'matchesData', 'shotsData', 'groupsData'],
                'match_page': ['rostersData', 'matchesData', 'shotsData']
            }
        }

        # Save structure information
        with open('data/raw/understat_structure.json', 'w') as f:
            json.dump(structure, f, indent=2)

        return structure

    def list_premier_league_teams(self) -> List[str]:
        """
        Get a list of Premier League teams available on Understat.

        Returns:
            List of team names
        """
        url = f"{self.BASE_URL}/league/{self.league}/{self.season}"

        try:
            logger.info(f"Fetching Premier League teams from {url}")
            response = requests.get(url)
            response.raise_for_status()

            # Extract the embedded JSON data
            teams_data = self._extract_json_data(response.text, "teamsData")

            if not teams_data:
                logger.error("Failed to extract team data from Understat")
                return []

            # Get team names
            team_names = [team['title'] for team in teams_data.values()]

            logger.info(f"Retrieved {len(team_names)} teams: {', '.join(team_names)}")
            return team_names

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching teams from Understat: {e}")
            return []

    def explore_available_metrics(self) -> Dict[str, List[str]]:
        """
        Explore and document the metrics available on Understat.

        Returns:
            Dictionary with available metrics by data type
        """
        metrics = {
            'player_level': [
                'games', 'time', 'goals', 'assists', 'shots', 'key_passes',
                'yellow_cards', 'red_cards', 'xG', 'xA', 'npg', 'npxG',
                'xGChain', 'xGBuildup'
            ],
            'match_level': [
                'minute', 'result', 'xG', 'xA', 'h_a', 'player', 'player_id',
                'situation', 'season', 'shotType', 'match_id', 'h_goals', 'a_goals',
                'date', 'player_assisted', 'player_assisted_id'
            ],
            'shot_level': [
                'id', 'minute', 'result', 'X', 'Y', 'xG', 'player', 'player_id',
                'situation', 'season', 'shotType', 'match_id', 'h_goals', 'a_goals',
                'h_team', 'a_team', 'date', 'player_assisted', 'player_assisted_id'
            ]
        }

        # Save metrics information
        with open('data/raw/understat_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2)

        return metrics

    def explore_understat(self) -> None:
        """Run a comprehensive exploration of Understat data."""
        # Explore website structure
        structure = self.explore_website_structure()
        print("\nUnderstat Website Structure:")
        print("===========================")
        for key, value in structure.items():
            print(f"{key}: {value}")

        # List available teams
        teams = self.list_premier_league_teams()

        # Get league players
        players_df = self.get_league_players()
        if not players_df.empty:
            print(f"\nRetrieved {len(players_df)} players from {self.league} {self.season}")
            print("\nSample Player Data (First 5 rows):")
            print(players_df.head())

            print("\nAvailable Columns:")
            for col in players_df.columns:
                print(f"- {col}")

            # Get sample player details
            sample_player_id = players_df.iloc[0]['id']
            player_stats = self.get_player_stats(sample_player_id)
            print(f"\nRetrieved detailed stats for player {sample_player_id}")
            print(f"Player name: {players_df.iloc[0]['player_name']}")

            # Get sample team
            if teams:
                sample_team = teams[0]
                team_df = self.get_team_players(sample_team)
                print(f"\nRetrieved {len(team_df)} players for team {sample_team}")

        # Document available metrics
        metrics = self.explore_available_metrics()
        print("\nAvailable Metrics on Understat:")
        print("==============================")
        for level, metric_list in metrics.items():
            print(f"\n{level.replace('_', ' ').title()} Metrics:")
            for metric in metric_list:
                print(f"- {metric}")

        print("\nUnderstat exploration complete. Check the data/raw directory for exported files.")


if __name__ == "__main__":
    explorer = UnderstatExplorer(league="epl", season="2023")
    explorer.explore_understat()