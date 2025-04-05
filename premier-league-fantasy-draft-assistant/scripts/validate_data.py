#!/usr/bin/env python3
"""
Premier League Fantasy Draft Assistant Data Validation Script

This script validates the quality and completeness of collected data.

Usage:
    python validate_data.py [options]

Options:
    --db-path=<path>     Specify database path (default: data/db/fantasy.db)
    --output=<file>      Output validation report file (default: data/reports/validation_report.md)
"""
import os
import sys
import logging
import argparse
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from src.data.storage.db_handler import DatabaseHandler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("data_validation")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Validate fantasy football data')
    parser.add_argument('--db-path', type=str, default='data/db/fantasy.db', help='Database path')
    parser.add_argument('--output', type=str, default='data/reports/validation_report.md',
                        help='Output validation report file')

    return parser.parse_args()


def validate_players(db_handler: DatabaseHandler) -> Dict[str, Any]:
    """
    Validate player data completeness and quality.

    Args:
        db_handler: Database handler instance

    Returns:
        Dictionary with validation results
    """
    # Get player data
    players_df = db_handler.get_players_dataframe()

    if players_df.empty:
        return {
            'status': 'error',
            'message': 'No player data found in database',
            'player_count': 0
        }

    # Calculate completeness metrics
    total_players = len(players_df)
    players_with_understat = players_df['understat_id'].notna().sum()
    players_with_xg = players_df['xG'].notna().sum()

    # Check for duplicate player entries
    duplicate_fpl_ids = players_df['fpl_id'].duplicated().sum()

    # Check for missing essential data
    missing_position = players_df['position_id'].isna().sum()
    missing_team = players_df['team_id'].isna().sum()
    missing_name = players_df['web_name'].isna().sum()

    # Calculate position distribution
    position_distribution = players_df['position'].value_counts().to_dict() if 'position' in players_df.columns else {}

    # Calculate team distribution
    team_distribution = players_df['team_name'].value_counts().to_dict() if 'team_name' in players_df.columns else {}

    return {
        'status': 'success',
        'player_count': total_players,
        'completeness': {
            'understat_mapping': f"{players_with_understat}/{total_players} ({players_with_understat / total_players * 100:.1f}%)",
            'xg_data': f"{players_with_xg}/{total_players} ({players_with_xg / total_players * 100:.1f}%)"
        },
        'data_quality': {
            'duplicate_fpl_ids': duplicate_fpl_ids,
            'missing_position': missing_position,
            'missing_team': missing_team,
            'missing_name': missing_name
        },
        'position_distribution': position_distribution,
        'team_distribution': team_distribution
    }


def validate_fixtures(db_handler: DatabaseHandler) -> Dict[str, Any]:
    """
    Validate fixture data completeness and quality.

    Args:
        db_handler: Database handler instance

    Returns:
        Dictionary with validation results
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
    ORDER BY f.gameweek, f.id
    """

    # Execute query
    conn = db_handler.engine.connect()
    fixtures_df = pd.read_sql(query, conn)
    conn.close()

    if fixtures_df.empty:
        return {
            'status': 'error',
            'message': 'No fixture data found in database',
            'fixture_count': 0
        }

    # Calculate completeness metrics
    total_fixtures = len(fixtures_df)
    fixtures_with_date = fixtures_df['date'].notna().sum()
    fixtures_with_difficulty = (fixtures_df['home_team_difficulty'].notna() &
                                fixtures_df['away_team_difficulty'].notna()).sum()

    # Calculate gameweek distribution
    gameweek_distribution = fixtures_df['gameweek'].value_counts().to_dict()

    # Check for missing gameweeks
    max_gameweek = fixtures_df['gameweek'].max() if not fixtures_df.empty else 0
    expected_gameweeks = set(range(1, max_gameweek + 1))
    actual_gameweeks = set(fixtures_df['gameweek'].unique())
    missing_gameweeks = expected_gameweeks - actual_gameweeks

    return {
        'status': 'success',
        'fixture_count': total_fixtures,
        'completeness': {
            'fixtures_with_date': f"{fixtures_with_date}/{total_fixtures} ({fixtures_with_date / total_fixtures * 100:.1f}%)",
            'fixtures_with_difficulty': f"{fixtures_with_difficulty}/{total_fixtures} ({fixtures_with_difficulty / total_fixtures * 100:.1f}%)"
        },
        'data_quality': {
            'missing_gameweeks': list(missing_gameweeks) if missing_gameweeks else "None"
        },
        'gameweek_distribution': gameweek_distribution
    }


def generate_report(validation_results: Dict[str, Dict[str, Any]], output_file: str):
    """
    Generate a validation report.

    Args:
        validation_results: Dictionary with validation results
        output_file: Output file path
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        f.write("# Fantasy Draft Assistant Data Validation Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Player validation
        f.write("## Player Data Validation\n\n")
        player_results = validation_results.get('players', {})

        if player_results.get('status') == 'error':
            f.write(f"**Error:** {player_results.get('message')}\n\n")
        else:
            f.write(f"**Player Count:** {player_results.get('player_count', 0)}\n\n")

            f.write("### Data Completeness\n\n")
            completeness = player_results.get('completeness', {})
            for key, value in completeness.items():
                f.write(f"- **{key.replace('_', ' ').title()}:** {value}\n")

            f.write("\n### Data Quality Issues\n\n")
            quality = player_results.get('data_quality', {})
            for key, value in quality.items():
                f.write(f"- **{key.replace('_', ' ').title()}:** {value}\n")

            f.write("\n### Position Distribution\n\n")
            position_dist = player_results.get('position_distribution', {})
            for position, count in position_dist.items():
                f.write(f"- **{position}:** {count}\n")

        # Fixture validation
        f.write("\n## Fixture Data Validation\n\n")
        fixture_results = validation_results.get('fixtures', {})

        if fixture_results.get('status') == 'error':
            f.write(f"**Error:** {fixture_results.get('message')}\n\n")
        else:
            f.write(f"**Fixture Count:** {fixture_results.get('fixture_count', 0)}\n\n")

            f.write("### Data Completeness\n\n")
            completeness = fixture_results.get('completeness', {})
            for key, value in completeness.items():
                f.write(f"- **{key.replace('_', ' ').title()}:** {value}\n")

            f.write("\n### Data Quality Issues\n\n")
            quality = fixture_results.get('data_quality', {})
            for key, value in quality.items():
                f.write(f"- **{key.replace('_', ' ').title()}:** {value}\n")

            f.write("\n### Gameweek Distribution\n\n")
            gameweek_dist = fixture_results.get('gameweek_distribution', {})
            for gameweek, count in sorted(gameweek_dist.items()):
                f.write(f"- **Gameweek {gameweek}:** {count} fixtures\n")

        f.write("\n## Recommendations\n\n")

        # Generate recommendations based on validation results
        recommendations = []

        player_results = validation_results.get('players', {})
        if player_results.get('status') == 'success':
            understat_mapping = player_results.get('completeness', {}).get('understat_mapping', '0/0 (0%)')
            mapping_percentage = float(understat_mapping.split('(')[1].split('%')[0])

            if mapping_percentage < 80:
                recommendations.append("Improve player mapping between FPL and Understat")

            missing_position = player_results.get('data_quality', {}).get('missing_position', 0)
            if missing_position > 0:
                recommendations.append(f"Fix {missing_position} players with missing position data")

        fixture_results = validation_results.get('fixtures', {})
        if fixture_results.get('status') == 'success':
            missing_gameweeks = fixture_results.get('data_quality', {}).get('missing_gameweeks', [])
            if missing_gameweeks and missing_gameweeks != "None":
                recommendations.append(f"Add missing fixtures for gameweeks: {', '.join(map(str, missing_gameweeks))}")

        if not recommendations:
            recommendations.append("Data validation completed successfully with no major issues")

        for i, recommendation in enumerate(recommendations, 1):
            f.write(f"{i}. {recommendation}\n")

    logger.info(f"Generated validation report: {output_file}")


def main():
    """Main function to coordinate data validation."""
    # Parse command line arguments
    args = parse_arguments()

    # Ensure logs directory exists
    os.makedirs('data/logs', exist_ok=True)

    logger.info("Starting data validation process")

    # Initialize database handler
    db_handler = DatabaseHandler(db_path=args.db_path)

    # Validate data
    validation_results = {
        'players': validate_players(db_handler),
        'fixtures': validate_fixtures(db_handler)
    }

    # Generate report
    generate_report(validation_results, args.output)

    logger.info("Data validation process completed")


if __name__ == "__main__":
    main()