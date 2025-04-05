"""
Integration test for data collection process.
Tests the entire data collection pipeline from API to database storage.
"""
import os
import sys
import unittest
import tempfile
import asyncio
import pandas as pd
from unittest.mock import patch, MagicMock

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import project modules
from src.data.collectors.fpl_api import FPLApiClient
from src.data.collectors.understat_api import UnderstatClient
from src.data.collectors.news_collector import NewsCollector
from src.data.storage.db_handler import DatabaseHandler


class TestDataCollection(unittest.TestCase):
    """Test data collection integration."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary database
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db')
        self.db_handler = DatabaseHandler(db_path=self.temp_db.name)

        # Create tables
        self.db_handler.create_tables()

    def tearDown(self):
        """Clean up after test."""
        # Close and delete temporary database
        self.temp_db.close()

    @patch('src.data.collectors.fpl_api.FPLApiClient.get_general_info')
    def test_team_collection(self, mock_get_general_info):
        """Test collecting and saving team data."""
        # Mock data
        mock_teams = [
            {
                'id': 1,
                'name': 'Arsenal',
                'short_name': 'ARS',
                'code': 3,
                'strength': 4
            },
            {
                'id': 2,
                'name': 'Aston Villa',
                'short_name': 'AVL',
                'code': 7,
                'strength': 3
            }
        ]

        mock_get_general_info.return_value = {
            'teams': mock_teams
        }

        # Create client and collect data
        client = FPLApiClient()
        general_info = client.get_general_info()

        # Save to database
        self.db_handler.save_teams(general_info['teams'])

        # Query database to verify teams were saved
        conn = self.db_handler.engine.connect()
        result = conn.execute("SELECT COUNT(*) FROM teams").fetchone()
        conn.close()

        # Check that teams were saved
        self.assertEqual(result[0], 2)

    @patch('src.data.collectors.fpl_api.FPLApiClient.get_all_players')
    def test_player_collection(self, mock_get_all_players):
        """Test collecting and saving player data."""
        # Mock data
        mock_players = [
            {
                'id': 1,
                'first_name': 'Harry',
                'second_name': 'Kane',
                'web_name': 'Kane',
                'team': 1,
                'element_type': 4,
                'now_cost': 120,
                'minutes': 1800,
                'goals_scored': 15,
                'assists': 5
            },
            {
                'id': 2,
                'first_name': 'Kevin',
                'second_name': 'De Bruyne',
                'web_name': 'De Bruyne',
                'team': 2,
                'element_type': 3,
                'now_cost': 130,
                'minutes': 1600,
                'goals_scored': 8,
                'assists': 12
            }
        ]

        mock_get_all_players.return_value = pd.DataFrame(mock_players)

        # Create client and collect data
        client = FPLApiClient()
        players_df = client.get_all_players()

        # Save to database
        self.db_handler.save_players(players_df.to_dict('records'))

        # Query database to verify players were saved
        conn = self.db_handler.engine.connect()
        result = conn.execute("SELECT COUNT(*) FROM players").fetchone()
        conn.close()

        # Check that players were saved
        self.assertEqual(result[0], 2)

    @patch('src.data.collectors.understat_api.UnderstatClient.get_league_players')
    def test_understat_collection(self, mock_get_league_players):
        """Test collecting and integrating Understat data."""
        # Mock data
        mock_understat_players = [
            {
                'id': 'u1',
                'player_name': 'Harry Kane',
                'team_title': 'Tottenham',
                'xG': '15.5',
                'xA': '5.2'
            },
            {
                'id': 'u2',
                'player_name': 'Kevin De Bruyne',
                'team_title': 'Manchester City',
                'xG': '8.3',
                'xA': '12.1'
            }
        ]

        mock_get_league_players.return_value = pd.DataFrame(mock_understat_players)

        # Create client and collect data
        client = UnderstatClient()
        understat_df = client.get_league_players()

        # Verify data
        self.assertEqual(len(understat_df), 2)
        self.assertIn('xG', understat_df.columns)
        self.assertIn('xA', understat_df.columns)


def run_async_test(coro):
    """Helper to run async tests."""
    return asyncio.run(coro)


if __name__ == '__main__':
    unittest.main()