#!/usr/bin/env python3
"""
Premier League Fantasy Draft Assistant Data Export Script

This script exports data from the database to various formats for analysis.

Usage:
    python export_data.py [options]

Options:
    --format=<format>    Export format (csv, json, excel) (default: csv)
    --output=<dir>       Output directory (default: data/exports)
    --db-path=<path>     Specify database path (default: data/db/fantasy.db)
"""
import os
import sys
import logging
import argparse
import pandas as pd
from typing import Dict, List, Any, Optional

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from src.data.storage.db_handler import DatabaseHandler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/export.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("data_export")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Export fantasy football data')
    parser.add_argument('--format', type=str, default='csv',
                        choices=['csv', 'json', 'excel'], help='Export format')
    parser.add_argument('--output', type=str, default='data/exports', help='Output directory')
    parser.add_argument('--db-path', type=str, default='data/db/fantasy.db', help='Database path')

    return parser.parse_args()


def export_players(db_handler: DatabaseHandler, output_dir: str, format: str):
    """
    Export player data to the specified format.

    Args:
        db_handler: Database handler instance
        output_dir: Output directory
        format: Export format (csv, json, excel)
    """
    # Get player data from database
    players_df = db_handler.get_players_dataframe()

    if players_df.empty:
        logger.warning("No player data to export")
        return

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Export based on format
    if format == 'csv':
        output_file = os.path.join(output_dir, 'players.csv')
        players_df.to_csv(output_file, index=False)
        logger.info(f"Exported {len(players_df)} players to {output_file}")

    elif format == 'json':
        output_file = os.path.join(output_dir, 'players.json')
        players_df.to_json(output_file, orient='records', indent=2)
        logger.info(f"Exported {len(players_df)} players to {output_file}")

    elif format == 'excel':
        output_file = os.path.join(output_dir, 'players.xlsx')
        players_df.to_excel(output_file, index=False)
        logger.info(f"Exported {len(players_df)} players to {output_file}")


def export_fixtures(db_handler: DatabaseHandler, output_dir: str, format: str):
    """
    Export fixture data to the specified format.

    Args:
        db_handler: Database handler instance
        output_dir: Output directory
        format: Export format (csv, json, excel)
    """
    # Create a query to get fixtures with team names
    query = """
    SELECT f.id, f.gameweek, 
           h.name as home_team, a.name as away_team,
           f.home_team_difficulty, f.away_team_difficulty,
           f.date
    FROM fixtures f
    JOIN teams h ON f.home_team_id = h.id
    JOIN teams a ON f.away_team_id = a.id
    ORDER BY f.date, f.id
    """

    # Execute query
    conn = db_handler.engine.connect()
    fixtures_df = pd.read_sql(query, conn)
    conn.close()

    if fixtures_df.empty:
        logger.warning("No fixture data to export")
        return

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Export based on format
    if format == 'csv':
        output_file = os.path.join(output_dir, 'fixtures.csv')
        fixtures_df.to_csv(output_file, index=False)
        logger.info(f"Exported {len(fixtures_df)} fixtures to {output_file}")

    elif format == 'json':
        output_file = os.path.join(output_dir, 'fixtures.json')
        fixtures_df.to_json(output_file, orient='records', indent=2)
        logger.info(f"Exported {len(fixtures_df)} fixtures to {output_file}")

    elif format == 'excel':
        output_file = os.path.join(output_dir, 'fixtures.xlsx')
        fixtures_df.to_excel(output_file, index=False)
        logger.info(f"Exported {len(fixtures_df)} fixtures to {output_file}")


def export_player_statistics(db_handler: DatabaseHandler, output_dir: str, format: str):
    """
    Export detailed player statistics to the specified format.

    Args:
        db_handler: Database handler instance
        output_dir: Output directory
        format: Export format (csv, json, excel)
    """
    # Create a query to get player statistics with team and position names
    query = """
    SELECT p.id, p.fpl_id, p.understat_id, 
           p.first_name, p.second_name, p.web_name,
           t.name as team, pos.singular_name as position,
           p.now_cost, p.minutes, p.goals_scored, p.assists,
           p.clean_sheets, p.yellow_cards, p.red_cards,
           p.points_per_game, p.selected_by_percent, p.form,
           p.xG, p.xA, p.npxG, p.npxG_per_90, p.xA_per_90
    FROM players p
    JOIN teams t ON p.team_id = t.id
    JOIN positions pos ON p.position_id = pos.id
    ORDER BY p.points_per_game DESC NULLS LAST
    """

    # Execute query
    conn = db_handler.engine.connect()
    stats_df = pd.read_sql(query, conn)
    conn.close()

    if stats_df.empty:
        logger.warning("No player statistics to export")
        return

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Export based on format
    if format == 'csv':
        output_file = os.path.join(output_dir, 'player_statistics.csv')
        stats_df.to_csv(output_file, index=False)
        logger.info(f"Exported statistics for {len(stats_df)} players to {output_file}")

    elif format == 'json':
        output_file = os.path.join(output_dir, 'player_statistics.json')
        stats_df.to_json(output_file, orient='records', indent=2)
        logger.info(f"Exported statistics for {len(stats_df)} players to {output_file}")

    elif format == 'excel':
        output_file = os.path.join(output_dir, 'player_statistics.xlsx')
        stats_df.to_excel(output_file, index=False)
        logger.info(f"Exported statistics for {len(stats_df)} players to {output_file}")


def main():
    """Main function to coordinate data export."""
    # Parse command line arguments
    args = parse_arguments()

    # Ensure logs directory exists
    os.makedirs('data/logs', exist_ok=True)

    logger.info(f"Starting data export process (format: {args.format})")

    # Initialize database handler
    db_handler = DatabaseHandler(db_path=args.db_path)

    # Export data
    export_players(db_handler, args.output, args.format)
    export_fixtures(db_handler, args.output, args.format)
    export_player_statistics(db_handler, args.output, args.format)

    logger.info("Data export process completed")


if __name__ == "__main__":
    main()