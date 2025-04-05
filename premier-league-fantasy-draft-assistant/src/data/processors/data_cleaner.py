"""
Data cleaning module for Premier League Fantasy Draft Assistant.
Handles standardization, normalization, and validation of player data.
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class DataCleaner:
    """Cleans and prepares data for analysis."""

    def __init__(self):
        """Initialize the data cleaner."""
        logger.info("Initialized data cleaner")

    def clean_player_names(self, df: pd.DataFrame, name_col: str = 'name') -> pd.DataFrame:
        """
        Standardize player names for better matching between data sources.

        Args:
            df: DataFrame with player data
            name_col: Column name containing player names

        Returns:
            DataFrame with cleaned names
        """
        if df.empty or name_col not in df.columns:
            return df

        # Create a copy to avoid modifying the original
        cleaned_df = df.copy()

        # Convert to lowercase
        cleaned_df[f'clean_{name_col}'] = cleaned_df[name_col].str.lower()

        # Remove special characters and accents
        special_chars = {
            'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
            'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
            'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
            'ç': 'c', 'ñ': 'n'
        }

        for char, replacement in special_chars.items():
            cleaned_df[f'clean_{name_col}'] = cleaned_df[f'clean_{name_col}'].str.replace(char, replacement)

        # Remove suffixes like Jr., Sr., etc.
        cleaned_df[f'clean_{name_col}'] = cleaned_df[f'clean_{name_col}'].str.replace(r'\s+(jr|sr|i{1,3}|iv)\.?$', '',
                                                                                      regex=True)

        # Remove middle initials
        cleaned_df[f'clean_{name_col}'] = cleaned_df[f'clean_{name_col}'].str.replace(r'\s+[a-z]\.?\s+', ' ',
                                                                                      regex=True)

        logger.info(f"Cleaned {name_col} column in DataFrame with {len(df)} rows")
        return cleaned_df

    def normalize_team_names(self, df: pd.DataFrame, team_col: str = 'team') -> pd.DataFrame:
        """
        Standardize team names across data sources.

        Args:
            df: DataFrame with team data
            team_col: Column name containing team names

        Returns:
            DataFrame with normalized team names
        """
        if df.empty or team_col not in df.columns:
            return df

        # Create a copy to avoid modifying the original
        normalized_df = df.copy()

        # Standardization mapping
        team_mapping = {
            # Official names to standardized names
            'manchester united': 'man utd',
            'manchester city': 'man city',
            'newcastle united': 'newcastle',
            'tottenham': 'spurs',
            'tottenham hotspur': 'spurs',
            'wolverhampton': 'wolves',
            'wolverhampton wanderers': 'wolves',
            'brighton': 'brighton',
            'brighton and hove albion': 'brighton',
            'brighton & hove albion': 'brighton',
            'leicester': 'leicester',
            'leicester city': 'leicester',
            # Add more as needed
        }

        # Apply mapping using a lambda function to handle case differences
        normalized_df[f'normalized_{team_col}'] = normalized_df[team_col].apply(
            lambda x: team_mapping.get(str(x).lower(), x) if pd.notna(x) else x
        )

        logger.info(f"Normalized {team_col} column in DataFrame with {len(df)} rows")
        return normalized_df

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in the DataFrame with appropriate strategies.

        Args:
            df: DataFrame with missing values

        Returns:
            DataFrame with handled missing values
        """
        if df.empty:
            return df

        # Create a copy to avoid modifying the original
        handled_df = df.copy()

        # Count nulls before
        nulls_before = handled_df.isnull().sum().sum()

        # Strategy for different column types
        numeric_cols = handled_df.select_dtypes(include=['number']).columns
        categorical_cols = handled_df.select_dtypes(include=['object', 'category']).columns

        # For numeric columns: fill with 0 for counting stats, median for others
        for col in numeric_cols:
            # Determine if column is a counting stat (goals, assists, etc.)
            if col.lower() in ['goals', 'assists', 'yellow_cards', 'red_cards', 'clean_sheets', 'saves']:
                handled_df[col].fillna(0, inplace=True)
            else:
                handled_df[col].fillna(handled_df[col].median(), inplace=True)

        # For categorical columns: fill with mode or 'Unknown'
        for col in categorical_cols:
            # Get the most common value
            most_common = handled_df[col].mode().iloc[0] if not handled_df[col].mode().empty else 'Unknown'
            handled_df[col].fillna(most_common, inplace=True)

        # Count nulls after
        nulls_after = handled_df.isnull().sum().sum()

        logger.info(f"Handled missing values: {nulls_before} nulls before, {nulls_after} nulls after")
        return handled_df

    def validate_player_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate player data and flag suspicious values.

        Args:
            df: DataFrame with player data

        Returns:
            DataFrame with validation flags
        """
        if df.empty:
            return df

        # Create a copy to avoid modifying the original
        validated_df = df.copy()

        # Add a validation flag column
        validated_df['data_flags'] = ""

        # Check for suspicious values
        if 'minutes' in validated_df.columns:
            # Flag suspiciously high minutes (more than 90*38 = 3420)
            suspicious_minutes = validated_df['minutes'] > 3420
            validated_df.loc[suspicious_minutes, 'data_flags'] += "high_minutes,"

        if 'goals' in validated_df.columns and 'position' in validated_df.columns:
            # Flag suspiciously high goals for defenders (more than 10)
            suspicious_goals = (validated_df['position'].isin(['Defender', 'Goalkeeper'])) & (
                        validated_df['goals'] > 10)
            validated_df.loc[suspicious_goals, 'data_flags'] += "high_goals_for_position,"

        # Remove trailing comma from flags
        validated_df['data_flags'] = validated_df['data_flags'].str.rstrip(',')

        # Count flagged records
        flagged_count = (validated_df['data_flags'] != "").sum()
        logger.info(f"Validated player data: {flagged_count} records flagged out of {len(validated_df)}")

        return validated_df