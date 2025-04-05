"""
News collector module for Premier League Fantasy Draft Assistant.
Collects player news, injury updates, and team news from reliable sources.
"""
import requests
import logging
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import time
import re

logger = logging.getLogger(__name__)


class NewsCollector:
    """Collects news and updates about Premier League players."""

    def __init__(self):
        """Initialize the news collector."""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        logger.info("Initialized news collector")

    def get_fpl_status_updates(self) -> List[Dict[str, Any]]:
        """
        Get player status updates from the FPL API.

        Returns:
            List of player status updates
        """
        url = "https://fantasy.premierleague.com/api/bootstrap-static/"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            # Extract status changes
            status_updates = []
            if 'elements' in data:
                for player in data['elements']:
                    # Check if player has a status change (not available)
                    if player.get('status') != 'a':
                        status_updates.append({
                            'player_id': player.get('id'),
                            'name': f"{player.get('first_name')} {player.get('second_name')}",
                            'status': player.get('status'),
                            'news': player.get('news', ''),
                            'chance_of_playing_next_round': player.get('chance_of_playing_next_round'),
                            'chance_of_playing_this_round': player.get('chance_of_playing_this_round')
                        })

            logger.info(f"Retrieved {len(status_updates)} player status updates")
            return status_updates

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching FPL status updates: {e}")
            return []

    def get_premierinjuries_data(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Scrape injury data from premierinjuries.com.

        Returns:
            Dictionary mapping team names to lists of injured players
        """
        url = "https://www.premierinjuries.com/injury-table.php"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Dictionary to store injury data by team
            injury_data = {}

            # Find all team tables
            team_tables = soup.find_all('table', class_='injury-table')

            for table in team_tables:
                # Get team name
                team_header = table.find_previous('h2')
                if not team_header:
                    continue

                team_name = team_header.text.strip()
                injury_data[team_name] = []

                # Get player injuries
                rows = table.find_all('tr')[1:]  # Skip header row
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        player_data = {
                            'name': cells[0].text.strip(),
                            'injury': cells[1].text.strip(),
                            'return_date': cells[2].text.strip(),
                            'status': cells[3].text.strip()
                        }
                        injury_data[team_name].append(player_data)

            # Count total players with injuries
            total_injuries = sum(len(players) for players in injury_data.values())
            logger.info(f"Retrieved injury data for {len(injury_data)} teams, {total_injuries} players total")

            return injury_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching injury data: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error parsing injury data: {e}")
            return {}