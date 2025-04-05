#!/usr/bin/env python3
"""
Premier League Fantasy Draft Assistant Data Collection Script

This script coordinates the data collection process from multiple sources
and stores it in the database.

Usage:
    python collect_data.py [options]

Options:
    --full               Perform a full data collection (all sources)
    --fpl                Collect data from FPL API only
    --understat          Collect data from Understat only
    --players            Update player data only
    --fixtures           Update fixtures only
    --news               Update news and injury data only
    --db-path=<path>     Specify database path (default: data/db/fantasy.db)
"""

import logging
import argparse
import time
from typing import Dict, List, Any, Optional
import pandas as pd
import aiohttp
import asyncio

import os
import sys

# Get the absolute path of the script
script_path = os.path.abspath(__file__)
# Get the directory containing the script
script_dir = os.path.dirname(script_path)
# Get the project root directory (parent directory of scripts folder)
project_root = os.path.dirname(script_dir)
# Add the project root to Python path
sys.path.append(project_root)

# Now import the modules
from src.data.collectors.fpl_api import FPLApiClient
# rest of your imports...
from src.data.collectors.fpl_api import FPLApiClient
from src.data.collectors.understat_api import UnderstatClient
from src.data.collectors.news_collector import NewsCollector
from src.data.processors.data_cleaner import DataCleaner
from src.data.processors.player_mapper import PlayerMapper
from src.data.storage.db_handler import DatabaseHandler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("data_collection")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Collect fantasy football data')
    parser.add_argument('--full', action='store_true', help='Perform a full data collection')
    parser.add_argument('--fpl', action='store_true', help='Collect data from FPL API only')
    parser.add_argument('--understat', action='store_true', help='Collect data from Understat only')
    parser.add_argument('--players', action='store_true', help='Update player data only')
    parser.add_argument('--fixtures', action='store_true', help='Update fixtures only')
    parser.add_argument('--news', action='store_true', help='Update news and injury data only')
    parser.add_argument('--db-path', type=str, default='data/db/fantasy.db', help='Database path')

    return parser.parse_args()


async def collect_fpl_data(db_handler: DatabaseHandler, players_only: bool = False, fixtures_only: bool = False):
    """
    Collect data from the FPL API.

    Args:
        db_handler: Database handler instance
        players_only: Only collect player data
        fixtures_only: Only collect fixture data
    """
    logger.info("Starting FPL data collection")

    async with aiohttp.ClientSession() as session:
        fpl_client = FPLApiClient(session)

        # Get general information
        general_info = fpl_client.get_general_info()

        if not general_info:
            logger.error("Failed to retrieve general information from FPL API")
            return

        # Save teams and positions data
        if not players_only and not fixtures_only:
            if 'teams' in general_info:
                db_handler.save_teams(general_info['teams'])

            if 'element_types' in general_info:
                db_handler.save_positions(general_info['element_types'])

        # Save player data
        if not fixtures_only:
            if 'elements' in general_info:
                # Get and enrich player data
                players_df = fpl_client.get_all_players()
                enriched_players_df = fpl_client.enrich_player_data(players_df)

                # Clean player data
                cleaner = DataCleaner()
                cleaned_players_df = cleaner.handle_missing_values(enriched_players_df)
                validated_players_df = cleaner.validate_player_data(cleaned_players_df)

                # Convert DataFrame to list of dicts for database
                players_data = validated_players_df.to_dict('records')
                db_handler.save_players(players_data)

                # Sample player histories for demonstration
                # In a real implementation, you'd process all players
                sample_ids = validated_players_df['id'].head(10).tolist()
                histories = await fpl_client.get_player_history_async(sample_ids)

                for player_id, history_data in histories.items():
                    if 'history' in history_data:
                        db_handler.save_player_histories(player_id, history_data['history'])

        # Save fixture data
        if not players_only:
            fixtures = fpl_client.get_fixtures()
            if fixtures:
                db_handler.save_fixtures(fixtures)

    logger.info("Completed FPL data collection")


def collect_understat_data(db_handler: DatabaseHandler):
    """
    Collect data from Understat.

    Args:
        db_handler: Database handler instance
    """
    logger.info("Starting Understat data collection")

    # Initialize clients
    understat_client = UnderstatClient(league="epl", season="2023")

    # Get player data from Understat
    understat_players_df = understat_client.get_league_players()

    if understat_players_df.empty:
        logger.error("Failed to retrieve player data from Understat")
        return

    # Get FPL player data from database
    fpl_players_df = db_handler.get_players_dataframe()

    if fpl_players_df.empty:
        logger.error("Failed to retrieve FPL player data from database")
        return

    # Map players between FPL and Understat
    player_mapper = PlayerMapper()
    mappings_df = player_mapper.map_players(fpl_players_df, understat_players_df)

    # Export unmapped players for manual review
    player_mapper.export_missing_mappings(fpl_players_df, mappings_df)

    # Update database with Understat data
    for _, mapping in mappings_df.iterrows():
        fpl_id = mapping['fpl_id']
        understat_id = mapping['understat_id']

        # Find player in Understat DataFrame
        understat_player = understat_players_df[understat_players_df['id'] == understat_id]

        if not understat_player.empty:
            # Get the Understat data as a dictionary
            understat_data = understat_player.iloc[0].to_dict()

            # Update player in database
            db_handler.update_player_understat_data(fpl_id, understat_data)

    logger.info("Completed Understat data collection")


def collect_news_data(db_handler: DatabaseHandler):
    """
    Collect news and injury data.

    Args:
        db_handler: Database handler instance
    """
    logger.info("Starting news data collection")

    # Initialize news collector
    news_collector = NewsCollector()

    # Get player status updates from FPL
    status_updates = news_collector.get_fpl_status_updates()

    # Get injury data
    injury_data = news_collector.get_premierinjuries_data()

    # In a real implementation, you would:
    # 1. Store this data in appropriate database tables
    # 2. Link it to player records
    # 3. Use it for risk assessments

    logger.info(f"Collected {len(status_updates)} status updates and injury data for {len(injury_data)} teams")


async def main():
    """Main function to coordinate data collection."""
    # Parse command line arguments
    args = parse_arguments()

    # Ensure logs directory exists
    os.makedirs('data/logs', exist_ok=True)

    logger.info("Starting data collection process")

    # Initialize database handler
    db_handler = DatabaseHandler(db_path=args.db_path)

    # Create database tables if they don't exist
    db_handler.create_tables()

    # Determine what to collect based on arguments
    collect_fpl = args.full or args.fpl or args.players or args.fixtures or not (args.understat or args.news)
    collect_understat = args.full or args.understat
    collect_news = args.full or args.news

    # Collect data from FPL API
    if collect_fpl:
        await collect_fpl_data(
            db_handler,
            players_only=args.players,
            fixtures_only=args.fixtures
        )

    # Collect data from Understat
    if collect_understat:
        collect_understat_data(db_handler)

    # Collect news and injury data
    if collect_news:
        collect_news_data(db_handler)

    logger.info("Data collection process completed")


if __name__ == "__main__":
    asyncio.run(main())
