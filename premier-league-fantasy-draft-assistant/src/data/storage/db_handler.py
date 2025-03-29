"""
Database handler module for the Premier League Fantasy Draft Assistant.
Manages the SQLite database for storing player data and analysis.
"""
import os
import logging
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

logger = logging.getLogger(__name__)
Base = declarative_base()


# Define the database models (SQLAlchemy ORM)
class Team(Base):
    """Premier League team."""
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    short_name = Column(String)
    code = Column(Integer)
    strength = Column(Integer)
    strength_attack_home = Column(Integer)
    strength_attack_away = Column(Integer)
    strength_defence_home = Column(Integer)
    strength_defence_away = Column(Integer)

    # Relationships
    players = relationship("Player", back_populates="team")
    fixtures = relationship("Fixture",
                            primaryjoin="or_(Team.id==Fixture.home_team_id, Team.id==Fixture.away_team_id)")

    def __repr__(self):
        return f"<Team(name='{self.name}')>"


class Position(Base):
    """Player position (GK, DEF, MID, FWD)."""
    __tablename__ = 'positions'

    id = Column(Integer, primary_key=True)
    singular_name = Column(String, nullable=False)
    plural_name = Column(String)

    # Relationships
    players = relationship("Player", back_populates="position")

    def __repr__(self):
        return f"<Position(name='{self.singular_name}')>"


class Player(Base):
    """Fantasy Premier League player."""
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    fpl_id = Column(Integer, nullable=False, unique=True)
    understat_id = Column(String)

    first_name = Column(String)
    second_name = Column(String)
    web_name = Column(String, nullable=False)

    team_id = Column(Integer, ForeignKey('teams.id'))
    position_id = Column(Integer, ForeignKey('positions.id'))

    # FPL data
    now_cost = Column(Float)
    cost_change_start = Column(Float)
    selected_by_percent = Column(Float)
    minutes = Column(Integer)
    goals_scored = Column(Integer)
    assists = Column(Integer)
    clean_sheets = Column(Integer)
    goals_conceded = Column(Integer)
    own_goals = Column(Integer)
    penalties_saved = Column(Integer)
    penalties_missed = Column(Integer)
    yellow_cards = Column(Integer)
    red_cards = Column(Integer)
    saves = Column(Integer)
    bonus = Column(Integer)
    bps = Column(Integer)
    influence = Column(Float)
    creativity = Column(Float)
    threat = Column(Float)
    ict_index = Column(Float)

    # Understat data
    xG = Column(Float)
    xA = Column(Float)
    npxG = Column(Float)
    npxG_per_90 = Column(Float)
    xA_per_90 = Column(Float)

    # Analysis
    points_per_game = Column(Float)
    value = Column(Float)
    form = Column(Float)

    # Calculated fields
    projected_points = Column(Float)
    risk_score = Column(Float)

    # Relationships
    team = relationship("Team", back_populates="players")
    position = relationship("Position", back_populates="players")
    histories = relationship("PlayerHistory", back_populates="player")

    def __repr__(self):
        return f"<Player(name='{self.web_name}', team='{self.team.name if self.team else None}')>"


class PlayerHistory(Base):
    """Player's gameweek history."""
    __tablename__ = 'player_histories'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'))
    season = Column(String)
    gameweek = Column(Integer)

    minutes = Column(Integer)
    points = Column(Integer)
    goals_scored = Column(Integer)
    assists = Column(Integer)
    clean_sheets = Column(Integer)
    goals_conceded = Column(Integer)
    own_goals = Column(Integer)
    penalties_saved = Column(Integer)
    penalties_missed = Column(Integer)
    yellow_cards = Column(Integer)
    red_cards = Column(Integer)
    saves = Column(Integer)
    bonus = Column(Integer)
    bps = Column(Integer)

    # Calculated/advanced stats
    xG = Column(Float)
    xA = Column(Float)

    # Relationships
    player = relationship("Player", back_populates="histories")

    def __repr__(self):
        return f"<PlayerHistory(player='{self.player.web_name if self.player else None}', gw={self.gameweek})>"


class Fixture(Base):
    """Premier League fixture."""
    __tablename__ = 'fixtures'

    id = Column(Integer, primary_key=True)
    gameweek = Column(Integer)

    home_team_id = Column(Integer, ForeignKey('teams.id'))
    away_team_id = Column(Integer, ForeignKey('teams.id'))

    home_team_difficulty = Column(Integer)
    away_team_difficulty = Column(Integer)

    date = Column(DateTime)

    def __repr__(self):
        return f"<Fixture(gw={self.gameweek}, home={self.home_team_id}, away={self.away_team_id})>"


class DatabaseHandler:
    """Handles database operations for the application."""

    def __init__(self, db_path: str = 'data/db/fantasy.db'):
        """
        Initialize the database handler.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path

        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Create database engine
        self.engine = create_engine(f'sqlite:///{db_path}')

        # Create session factory
        self.Session = sessionmaker(bind=self.engine)

        logger.info(f"Initialized database handler with database at {db_path}")

    def create_tables(self) -> None:
        """Create all database tables if they don't exist."""
        Base.metadata.create_all(self.engine)
        logger.info("Created database tables")

    def drop_tables(self) -> None:
        """Drop all database tables."""
        Base.metadata.drop_all(self.engine)
        logger.info("Dropped all database tables")

    def save_teams(self, teams_data: List[Dict[str, Any]]) -> None:
        """
        Save team data to the database.

        Args:
            teams_data: List of team dictionaries
        """
        session = self.Session()
        try:
            for team_data in teams_data:
                team = Team(
                    id=team_data.get('id'),
                    name=team_data.get('name'),
                    short_name=team_data.get('short_name'),
                    code=team_data.get('code'),
                    strength=team_data.get('strength'),
                    strength_attack_home=team_data.get('strength_attack_home'),
                    strength_attack_away=team_data.get('strength_attack_away'),
                    strength_defence_home=team_data.get('strength_defence_home'),
                    strength_defence_away=team_data.get('strength_defence_away')
                )
                session.merge(team)

            session.commit()
            logger.info(f"Saved {len(teams_data)} teams to database")
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving teams: {e}")
        finally:
            session.close()

    def save_positions(self, positions_data: List[Dict[str, Any]]) -> None:
        """
        Save position data to the database.

        Args:
            positions_data: List of position dictionaries
        """
        session = self.Session()
        try:
            for position_data in positions_data:
                position = Position(
                    id=position_data.get('id'),
                    singular_name=position_data.get('singular_name'),
                    plural_name=position_data.get('plural_name')
                )
                session.merge(position)

            session.commit()
            logger.info(f"Saved {len(positions_data)} positions to database")
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving positions: {e}")
        finally:
            session.close()

    def save_players(self, players_data: List[Dict[str, Any]]) -> None:
        """
        Save player data to the database.

        Args:
            players_data: List of player dictionaries
        """
        session = self.Session()
        try:
            for player_data in players_data:
                player = Player(
                    fpl_id=player_data.get('id'),
                    first_name=player_data.get('first_name'),
                    second_name=player_data.get('second_name'),
                    web_name=player_data.get('web_name'),
                    team_id=player_data.get('team'),
                    position_id=player_data.get('element_type'),
                    now_cost=player_data.get('now_cost') / 10 if player_data.get('now_cost') else None,
                    cost_change_start=player_data.get('cost_change_start') / 10 if player_data.get(
                        'cost_change_start') else None,
                    selected_by_percent=player_data.get('selected_by_percent'),
                    minutes=player_data.get('minutes'),
                    goals_scored=player_data.get('goals_scored'),
                    assists=player_data.get('assists'),
                    clean_sheets=player_data.get('clean_sheets'),
                    goals_conceded=player_data.get('goals_conceded'),
                    own_goals=player_data.get('own_goals'),
                    penalties_saved=player_data.get('penalties_saved'),
                    penalties_missed=player_data.get('penalties_missed'),
                    yellow_cards=player_data.get('yellow_cards'),
                    red_cards=player_data.get('red_cards'),
                    saves=player_data.get('saves'),
                    bonus=player_data.get('bonus'),
                    bps=player_data.get('bps'),
                    influence=player_data.get('influence'),
                    creativity=player_data.get('creativity'),
                    threat=player_data.get('threat'),
                    ict_index=player_data.get('ict_index'),
                    points_per_game=player_data.get('points_per_game'),
                    form=player_data.get('form')
                )
                session.merge(player)

            session.commit()
            logger.info(f"Saved {len(players_data)} players to database")
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving players: {e}")
        finally:
            session.close()

    def save_fixtures(self, fixtures_data: List[Dict[str, Any]]) -> None:
        """
        Save fixture data to the database.

        Args:
            fixtures_data: List of fixture dictionaries
        """
        session = self.Session()
        try:
            for fixture_data in fixtures_data:
                # Parse date if it exists
                date = None
                if 'kickoff_time' in fixture_data and fixture_data['kickoff_time']:
                    try:
                        date = datetime.strptime(fixture_data['kickoff_time'], '%Y-%m-%dT%H:%M:%SZ')
                    except ValueError:
                        pass

                fixture = Fixture(
                    id=fixture_data.get('id'),
                    gameweek=fixture_data.get('event'),
                    home_team_id=fixture_data.get('team_h'),
                    away_team_id=fixture_data.get('team_a'),
                    home_team_difficulty=fixture_data.get('team_h_difficulty'),
                    away_team_difficulty=fixture_data.get('team_a_difficulty'),
                    date=date
                )
                session.merge(fixture)

            session.commit()
            logger.info(f"Saved {len(fixtures_data)} fixtures to database")
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving fixtures: {e}")
        finally:
            session.close()

    def update_player_understat_data(self, player_id: int, understat_data: Dict[str, Any]) -> None:
        """
        Update a player with Understat advanced statistics.

        Args:
            player_id: FPL player ID
            understat_data: Dictionary with Understat data
        """
        session = self.Session()
        try:
            player = session.query(Player).filter_by(fpl_id=player_id).first()

            if player:
                player.understat_id = understat_data.get('id')
                player.xG = understat_data.get('xG')
                player.xA = understat_data.get('xA')
                player.npxG = understat_data.get('npxG')

                # Calculate per 90 stats if minutes are available
                if player.minutes and player.minutes > 0:
                    minutes_90 = player.minutes / 90
                    player.npxG_per_90 = float(understat_data.get('npxG', 0)) / minutes_90 if minutes_90 > 0 else 0
                    player.xA_per_90 = float(understat_data.get('xA', 0)) / minutes_90 if minutes_90 > 0 else 0

                session.commit()
                logger.info(f"Updated player {player_id} with Understat data")
            else:
                logger.warning(f"Player with FPL ID {player_id} not found in database")

        except Exception as e:
            session.rollback()
            logger.error(f"Error updating player with Understat data: {e}")
        finally:
            session.close()

    def update_player_projections(self, player_id: int, projected_points: float, risk_score: float) -> None:
        """
        Update a player with projection and risk data.

        Args:
            player_id: FPL player ID
            projected_points: Projected fantasy points
            risk_score: Risk assessment score (0-100)
        """
        session = self.Session()
        try:
            player = session.query(Player).filter_by(fpl_id=player_id).first()

            if player:
                player.projected_points = projected_points
                player.risk_score = risk_score

                session.commit()
                logger.info(f"Updated player {player_id} with projections")
            else:
                logger.warning(f"Player with FPL ID {player_id} not found in database")

        except Exception as e:
            session.rollback()
            logger.error(f"Error updating player projections: {e}")
        finally:
            session.close()

    def save_player_histories(self, player_id: int, histories: List[Dict[str, Any]]) -> None:
        """
        Save player gameweek histories.

        Args:
            player_id: FPL player ID
            histories: List of gameweek history dictionaries
        """
        session = self.Session()
        try:
            # Get the internal player ID
            player = session.query(Player).filter_by(fpl_id=player_id).first()

            if not player:
                logger.warning(f"Player with FPL ID {player_id} not found in database")
                return

            for history in histories:
                ph = PlayerHistory(
                    player_id=player.id,
                    season=history.get('season_name', ''),
                    gameweek=history.get('round'),
                    minutes=history.get('minutes'),
                    points=history.get('total_points'),
                    goals_scored=history.get('goals_scored'),
                    assists=history.get('assists'),
                    clean_sheets=history.get('clean_sheets'),
                    goals_conceded=history.get('goals_conceded'),
                    own_goals=history.get('own_goals'),
                    penalties_saved=history.get('penalties_saved'),
                    penalties_missed=history.get('penalties_missed'),
                    yellow_cards=history.get('yellow_cards'),
                    red_cards=history.get('red_cards'),
                    saves=history.get('saves'),
                    bonus=history.get('bonus'),
                    bps=history.get('bps')
                )
                session.add(ph)

            session.commit()
            logger.info(f"Saved {len(histories)} history entries for player {player_id}")

        except Exception as e:
            session.rollback()
            logger.error(f"Error saving player histories: {e}")
        finally:
            session.close()

    def get_players_dataframe(self) -> pd.DataFrame:
        """
        Get all players as a pandas DataFrame.

        Returns:
            DataFrame with all player data
        """
        try:
            query = """
            SELECT p.*, t.name as team_name, pos.singular_name as position_name
            FROM players p
            JOIN teams t ON p.team_id = t.id
            JOIN positions pos ON p.position_id = pos.id
            """
            df = pd.read_sql(query, self.engine)
            logger.info(f"Retrieved {len(df)} players from database")
            return df

        except Exception as e:
            logger.error(f"Error retrieving players as DataFrame: {e}")
            return pd.DataFrame()

    def get_fixtures_by_team(self, team_id: int) -> pd.DataFrame:
        """
        Get upcoming fixtures for a specific team.

        Args:
            team_id: Team ID

        Returns:
            DataFrame with fixture data
        """
        try:
            query = """
            SELECT f.*, 
                   ht.name as home_team_name, 
                   at.name as away_team_name,
                   CASE WHEN f.home_team_id = ? THEN f.home_team_difficulty
                        ELSE f.away_team_difficulty END as difficulty
            FROM fixtures f
            JOIN teams ht ON f.home_team_id = ht.id
            JOIN teams at ON f.away_team_id = at.id
            WHERE (f.home_team_id = ? OR f.away_team_id = ?)
            AND f.date >= CURRENT_TIMESTAMP
            ORDER BY f.date
            """
            df = pd.read_sql(query, self.engine, params=(team_id, team_id, team_id))
            logger.info(f"Retrieved {len(df)} fixtures for team {team_id}")
            return df

        except Exception as e:
            logger.error(f"Error retrieving fixtures for team {team_id}: {e}")
            return pd.DataFrame()


# Example usage
if __name__ == "__main__":
    db = DatabaseHandler()

    # Create all tables
    db.create_tables()

    # Some example data
    teams = [
        {
            'id': 1,
            'name': 'Arsenal',
            'short_name': 'ARS',
            'code': 3,
            'strength': 4,
            'strength_attack_home': 1300,
            'strength_attack_away': 1200,
            'strength_defence_home': 1250,
            'strength_defence_away': 1200
        },
        {
            'id': 2,
            'name': 'Aston Villa',
            'short_name': 'AVL',
            'code': 7,
            'strength': 3,
            'strength_attack_home': 1100,
            'strength_attack_away': 1000,
            'strength_defence_home': 1050,
            'strength_defence_away': 950
        }
    ]

    positions = [
        {
            'id': 1,
            'singular_name': 'Goalkeeper',
            'plural_name': 'Goalkeepers'
        },
        {
            'id': 2,
            'singular_name': 'Defender',
            'plural_name': 'Defenders'
        },
        {
            'id': 3,
            'singular_name': 'Midfielder',
            'plural_name': 'Midfielders'
        },
        {
            'id': 4,
            'singular_name': 'Forward',
            'plural_name': 'Forwards'
        }
    ]

    # Save example data
    db.save_teams(teams)
    db.save_positions(positions)

    # Get data back as DataFrame
    players_df = db.get_players_dataframe()
    print(f"Players in database: {len(players_df)}")