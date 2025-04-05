"""
Player mapping module for Premier League Fantasy Draft Assistant.
Handles matching players between different data sources.
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional
from difflib import SequenceMatcher
import json
import os

logger = logging.getLogger(__name__)


class PlayerMapper:
    """Maps players between different data sources."""

    def __init__(self, mapping_file: str = 'data/processed/player_mapping.json'):
        """
        Initialize the player mapper.

        Args:
            mapping_file: Path to store/load the player mapping
        """
        self.mapping_file = mapping_file
        self.manual_mappings = {}

        # Load existing mappings if available
        self._load_mappings()

        logger.info("Initialized player mapper")

    def _load_mappings(self) -> None:
        """Load existing manual mappings from file."""
        try:
            if os.path.exists(self.mapping_file):
                with open(self.mapping_file, 'r') as f:
                    self.manual_mappings = json.load(f)
                logger.info(f"Loaded {len(self.manual_mappings)} manual player mappings")
        except Exception as e:
            logger.error(f"Error loading player mappings: {e}")
            self.manual_mappings = {}

    def _save_mappings(self) -> None:
        """Save manual mappings to file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.mapping_file), exist_ok=True)

            with open(self.mapping_file, 'w') as f:
                json.dump(self.manual_mappings, f, indent=2)
            logger.info(f"Saved {len(self.manual_mappings)} manual player mappings")
        except Exception as e:
            logger.error(f"Error saving player mappings: {e}")

    def add_manual_mapping(self, fpl_id: int, understat_id: str) -> None:
        """
        Add a manual mapping between FPL and Understat IDs.

        Args:
            fpl_id: FPL player ID
            understat_id: Understat player ID
        """
        self.manual_mappings[str(fpl_id)] = understat_id
        self._save_mappings()
        logger.info(f"Added manual mapping: FPL ID {fpl_id} -> Understat ID {understat_id}")

    def get_name_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two player names.

        Args:
            name1: First player name
            name2: Second player name

        Returns:
            Similarity score (0-1)
        """
        # Clean names for comparison
        name1 = str(name1).lower().strip()
        name2 = str(name2).lower().strip()

        # Use SequenceMatcher for similarity
        return SequenceMatcher(None, name1, name2).ratio()

    def map_players(self, fpl_df: pd.DataFrame, understat_df: pd.DataFrame,
                    threshold: float = 0.8) -> pd.DataFrame:
        """
        Map players between FPL and Understat DataFrames.

        Args:
            fpl_df: DataFrame with FPL player data
            understat_df: DataFrame with Understat player data
            threshold: Similarity threshold for matching (0-1)

        Returns:
            DataFrame with mapped player IDs
        """
        if fpl_df.empty or understat_df.empty:
            logger.warning("Empty DataFrame provided for player mapping")
            return pd.DataFrame()

        # Prepare column names
        fpl_id_col = 'id' if 'id' in fpl_df.columns else 'fpl_id'
        fpl_name_col = 'web_name' if 'web_name' in fpl_df.columns else 'name'
        fpl_team_col = 'team_name' if 'team_name' in fpl_df.columns else 'team'

        understat_id_col = 'id' if 'id' in understat_df.columns else 'understat_id'
        understat_name_col = 'player_name' if 'player_name' in understat_df.columns else 'name'
        understat_team_col = 'team_title' if 'team_title' in understat_df.columns else 'team'

        mappings = []

        # Apply manual mappings first
        for fpl_id_str, understat_id in self.manual_mappings.items():
            fpl_id = int(fpl_id_str)

            # Find player in FPL data
            fpl_player = fpl_df[fpl_df[fpl_id_col] == fpl_id]
            if fpl_player.empty:
                continue

            # Find player in Understat data
            understat_player = understat_df[understat_df[understat_id_col] == understat_id]
            if understat_player.empty:
                continue

            mappings.append({
                'fpl_id': fpl_id,
                'understat_id': understat_id,
                'fpl_name': fpl_player.iloc[0][fpl_name_col],
                'understat_name': understat_player.iloc[0][understat_name_col],
                'matching_type': 'manual',
                'similarity': 1.0  # Manual matches have perfect similarity
            })

        # Automated matching for remaining players
        matched_fpl_ids = [int(fpl_id) for fpl_id in self.manual_mappings.keys()]
        matched_understat_ids = list(self.manual_mappings.values())

        # Filter out already matched players
        remaining_fpl = fpl_df[~fpl_df[fpl_id_col].isin(matched_fpl_ids)]
        remaining_understat = understat_df[~understat_df[understat_id_col].isin(matched_understat_ids)]

        # Add team normalization for better matching
        from data_cleaner import DataCleaner
        cleaner = DataCleaner()

        # Normalize team names
        remaining_fpl = cleaner.normalize_team_names(remaining_fpl, team_col=fpl_team_col)
        remaining_understat = cleaner.normalize_team_names(remaining_understat, team_col=understat_team_col)

        # Match by name similarity within same team
        for _, fpl_player in remaining_fpl.iterrows():
            fpl_id = fpl_player[fpl_id_col]
            fpl_name = fpl_player[fpl_name_col]
            fpl_team = fpl_player.get(f'normalized_{fpl_team_col}', fpl_player[fpl_team_col])

            best_match = None
            best_similarity = 0

            # Find matching players from same team
            same_team_players = remaining_understat[
                remaining_understat.get(f'normalized_{understat_team_col}',
                                        remaining_understat[understat_team_col]) == fpl_team
                ]

            for _, understat_player in same_team_players.iterrows():
                understat_id = understat_player[understat_id_col]
                understat_name = understat_player[understat_name_col]

                # Calculate name similarity
                similarity = self.get_name_similarity(fpl_name, understat_name)

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = understat_player

            # If we found a good match
            if best_match is not None and best_similarity >= threshold:
                mappings.append({
                    'fpl_id': fpl_id,
                    'understat_id': best_match[understat_id_col],
                    'fpl_name': fpl_name,
                    'understat_name': best_match[understat_name_col],
                    'matching_type': 'automated',
                    'similarity': best_similarity
                })

        # Create DataFrame from mappings
        mappings_df = pd.DataFrame(mappings)

        logger.info(
            f"Mapped {len(mappings_df)} players: {len(mappings_df[mappings_df['matching_type'] == 'manual'])} manual, "
            f"{len(mappings_df[mappings_df['matching_type'] == 'automated'])} automated")

        return mappings_df

    def export_missing_mappings(self, fpl_df: pd.DataFrame, mappings_df: pd.DataFrame,
                                output_file: str = 'data/processed/missing_mappings.csv') -> pd.DataFrame:
        """
        Export players that couldn't be automatically mapped for manual review.

        Args:
            fpl_df: DataFrame with FPL player data
            mappings_df: DataFrame with mapped player IDs
            output_file: Path to save the missing mappings

        Returns:
            DataFrame with unmapped players
        """
        if fpl_df.empty:
            return pd.DataFrame()

        # Identify unmapped players
        fpl_id_col = 'id' if 'id' in fpl_df.columns else 'fpl_id'
        mapped_ids = mappings_df['fpl_id'].tolist() if not mappings_df.empty else []

        unmapped_players = fpl_df[~fpl_df[fpl_id_col].isin(mapped_ids)]

        # Save to CSV
        if not unmapped_players.empty:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            unmapped_players.to_csv(output_file, index=False)
            logger.info(f"Exported {len(unmapped_players)} unmapped players to {output_file}")

        return unmapped_players