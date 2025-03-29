"""
Understat API data collector module.
Handles fetching advanced football statistics (xG, xA) from Understat.
"""
import requests
import logging
import pandas as pd
import json
import re
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class UnderstatClient:
    """Client for scraping data from Understat (no official API)."""

    BASE_URL = "https://understat.com"

    def __init__(self, league: str = "epl", season: str = "2024"):
        """
        Initialize the Understat client.

        Args:
            league: League code (epl, la_liga, bundesliga, serie_a, ligue_1, rfpl)
            season: Season (e.g., 2024 for 2024/2025 season)
        """
        self.league = league
        self.season = season
        logger.info(f"Initialized Understat client for {league} season {season}")

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
            response = requests.get(url)
            response.raise_for_status()

            # Extract the embedded JSON data
            players_data = self._extract_json_data(response.text, "playersData")

            if not players_data:
                logger.error("Failed to extract player data from Understat")
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(players_data)

            # Convert numeric columns
            numeric_cols = ['games', 'time', 'goals', 'assists', 'shots', 'key_passes',
                            'yellow_cards', 'red_cards', 'xG', 'xA', 'npg', 'npxG']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            logger.info(f"Retrieved {len(df)} players from Understat")
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
            response = requests.get(url)
            response.raise_for_status()

            # Extract the embedded JSON data
            player_data = self._extract_json_data(response.text, "playersData")
            match_data = self._extract_json_data(response.text, "matchesData")

            result = {
                'player_info': player_data,
                'matches': match_data
            }

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
            response = requests.get(url)
            response.raise_for_status()

            # Extract the embedded JSON data
            players_data = self._extract_json_data(response.text, "playersData")

            if not players_data:
                logger.error(f"Failed to extract player data for team {team_name}")
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(players_data)

            logger.info(f"Retrieved {len(df)} players for {team_name} from Understat")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching players for team {team_name}: {e}")
            return pd.DataFrame()

    def map_players_to_fpl(self, understat_df: pd.DataFrame, fpl_df: pd.DataFrame) -> pd.DataFrame:
        """
        Map Understat players to FPL players based on name and team.

        Args:
            understat_df: DataFrame with Understat player data
            fpl_df: DataFrame with FPL player data

        Returns:
            DataFrame with mapped player IDs
        """
        # This is a simplified version - in practice, would need more robust matching
        mapping = []

        # Normalize team names (this would need to be expanded)
        team_mapping = {
            'Manchester United': 'Man Utd',
            'Manchester City': 'Man City',
            'Tottenham': 'Spurs',
            'Newcastle United': 'Newcastle',
            # Add more mappings as needed
        }

        if 'team_name' in fpl_df.columns and 'team_title' in understat_df.columns:
            understat_df['team_normalized'] = understat_df['team_title'].map(
                lambda x: team_mapping.get(x, x)
            )
            fpl_df['team_normalized'] = fpl_df['team_name'].map(
                lambda x: team_mapping.get(x, x)
            )

            # Simple matching by player name and team
            for _, us_player in understat_df.iterrows():
                us_name = us_player['player_name'].lower()
                us_team = us_player['team_normalized'].lower() if 'team_normalized' in us_player else ''

                for _, fpl_player in fpl_df.iterrows():
                    # Try to match on first and last name (simplified)
                    fpl_name = fpl_player['web_name'].lower() if 'web_name' in fpl_player else ''
                    fpl_team = fpl_player['team_normalized'].lower() if 'team_normalized' in fpl_player else ''

                    # If name contains and team matches
                    if (us_name in fpl_name or fpl_name in us_name) and (us_team == fpl_team):
                        mapping.append({
                            'understat_id': us_player['id'],
                            'fpl_id': fpl_player['id'],
                            'understat_name': us_player['player_name'],
                            'fpl_name': fpl_player['web_name'] if 'web_name' in fpl_player else '',
                            'team': us_player['team_title']
                        })
                        break

        return pd.DataFrame(mapping)


# Example usage
if __name__ == "__main__":
    client = UnderstatClient(league="epl", season="2024")
    players_df = client.get_league_players()
    print(f"Retrieved {len(players_df)} players from Understat")

    # Sample of getting individual player stats
    if not players_df.empty:
        sample_player_id = players_df.iloc[0]['id']
        player_stats = client.get_player_stats(sample_player_id)
        print(f"Retrieved stats for player {sample_player_id}")