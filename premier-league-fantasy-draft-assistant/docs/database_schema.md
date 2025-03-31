# Database Schema Design for Fantasy Draft Assistant

This document outlines the proposed database schema for storing and organizing data for the Premier League Fantasy Draft Assistant.

## Database Selection: SQLite

We've chosen SQLite for this project because:
- Lightweight and requires no server setup
- Perfect for single-user applications
- Easy to distribute with the application
- Good performance for read-heavy workloads
- Supports SQL for flexible querying

## Entity Relationship Diagram (Conceptual)

```
+-------------+       +---------------+        +-----------------+
|    Team     |------>|    Player     |<-------|   Position      |
+-------------+       +---------------+        +-----------------+
      |                  |        |
      |                  |        |
      v                  v        v
+-------------+     +----------+     +------------------+
|   Fixture   |     | History  |     | PlayerProjection |
+-------------+     +----------+     +------------------+
```

## Table Definitions

### teams
Stores information about Premier League teams.

| Column                | Type    | Description                              |
|-----------------------|---------|------------------------------------------|
| id                    | INTEGER | Primary key (from FPL API)               |
| name                  | TEXT    | Full team name                           |
| short_name            | TEXT    | Abbreviated name (3 chars)               |
| code                  | INTEGER | Team code                                |
| strength              | INTEGER | Overall team strength                    |
| strength_attack_home  | INTEGER | Home attack strength                     |
| strength_attack_away  | INTEGER | Away attack strength                     |
| strength_defence_home | INTEGER | Home defense strength                    |
| strength_defence_away | INTEGER | Away defense strength                    |

### positions
Stores player position categories.

| Column        | Type    | Description                   |
|---------------|---------|-------------------------------|
| id            | INTEGER | Primary key (from FPL API)    |
| singular_name | TEXT    | Position name (e.g., Defender)|
| plural_name   | TEXT    | Plural name                   |

### players
Stores core player information and current season stats.

| Column            | Type    | Description                              |
|-------------------|---------|------------------------------------------|
| id                | INTEGER | Primary key (auto-increment)             |
| fpl_id            | INTEGER | FPL API player ID                        |
| understat_id      | TEXT    | Understat player ID                      |
| first_name        | TEXT    | First name                               |
| second_name       | TEXT    | Last name                                |
| web_name          | TEXT    | Display name used in FPL                 |
| team_id           | INTEGER | Foreign key to teams                     |
| position_id       | INTEGER | Foreign key to positions                 |
| now_cost          | REAL    | Current price (in £M)                    |
| cost_change_start | REAL    | Price change since season start          |
| selected_by_percent| REAL   | Ownership percentage                     |
| minutes           | INTEGER | Minutes played                           |
| goals_scored      | INTEGER | Goals scored                             |
| assists           | INTEGER | Assists                                  |
| clean_sheets      | INTEGER | Clean sheets                             |
| goals_conceded    | INTEGER | Goals conceded                           |
| own_goals         | INTEGER | Own goals                                |
| penalties_saved   | INTEGER | Penalties saved                          |
| penalties_missed  | INTEGER | Penalties missed                         |
| yellow_cards      | INTEGER | Yellow cards                             |
| red_cards         | INTEGER | Red cards                                |
| saves             | INTEGER | Saves                                    |
| bonus             | INTEGER | Bonus points                             |
| bps               | INTEGER | Bonus point system score                 |
| influence         | REAL    | Influence score                          |
| creativity        | REAL    | Creativity score                         |
| threat            | REAL    | Threat score                             |
| ict_index         | REAL    | ICT index                                |
| xG                | REAL    | Expected goals                           |
| xA                | REAL    | Expected assists                         |
| npxG              | REAL    | Non-penalty expected goals               |
| npxG_per_90       | REAL    | Non-penalty expected goals per 90 min    |
| xA_per_90         | REAL    | Expected assists per 90 min              |
| points_per_game   | REAL    | FPL points per game                      |
| form              | REAL    | Form metric                              |

### player_histories
Stores historical performance data for players.

| Column            | Type    | Description                              |
|-------------------|---------|------------------------------------------|
| id                | INTEGER | Primary key (auto-increment)             |
| player_id         | INTEGER | Foreign key to players                   |
| season            | TEXT    | Season identifier (e.g., "2023/24")      |
| gameweek          | INTEGER | Gameweek number                          |
| minutes           | INTEGER | Minutes played                           |
| points            | INTEGER | FPL points earned                        |
| goals_scored      | INTEGER | Goals scored                             |
| assists           | INTEGER | Assists                                  |
| clean_sheets      | INTEGER | Clean sheets                             |
| goals_conceded    | INTEGER | Goals conceded                           |
| own_goals         | INTEGER | Own goals                                |
| penalties_saved   | INTEGER | Penalties saved                          |
| penalties_missed  | INTEGER | Penalties missed                         |
| yellow_cards      | INTEGER | Yellow cards                             |
| red_cards         | INTEGER | Red cards                                |
| saves             | INTEGER | Saves                                    |
| bonus             | INTEGER | Bonus points                             |
| bps               | INTEGER | Bonus point system score                 |
| xG                | REAL    | Expected goals                           |
| xA                | REAL    | Expected assists                         |

### fixtures
Stores Premier League fixture information.

| Column               | Type    | Description                              |
|----------------------|---------|------------------------------------------|
| id                   | INTEGER | Primary key (from FPL API)               |
| gameweek             | INTEGER | Gameweek number                          |
| home_team_id         | INTEGER | Foreign key to teams (home team)         |
| away_team_id         | INTEGER | Foreign key to teams (away team)         |
| home_team_difficulty | INTEGER | Difficulty rating for home team          |
| away_team_difficulty | INTEGER | Difficulty rating for away team          |
| date                 | TEXT    | Fixture date and time                    |

### player_projections
Stores projection and analysis data for players.

| Column           | Type    | Description                              |
|------------------|---------|------------------------------------------|
| id               | INTEGER | Primary key (auto-increment)             |
| player_id        | INTEGER | Foreign key to players                   |
| projected_points | REAL    | Projected fantasy points for next GW     |
| season_projection| REAL    | Projected season total points            |
| risk_score       | REAL    | Risk assessment (0-100)                  |
| consistency_score| REAL    | Consistency metric (0-100)               |
| value_score      | REAL    | Value calculation                        |
| form_trend       | TEXT    | Form trend indicator (up/down/stable)    |
| minutes_risk     | REAL    | Risk of limited minutes (0-100)          |
| updated_at       | TEXT    | Last update timestamp                    |

## Indexing Strategy

### Primary Keys
- All tables have integer primary keys for efficient joins

### Foreign Keys
- player.team_id → teams.id
- player.position_id → positions.id
- player_histories.player_id → players.id
- fixtures.home_team_id → teams.id
- fixtures.away_team_id → teams.id
- player_projections.player_id → players.id

### Additional Indexes
- players(web_name) - For player name searches
- players(fpl_id, understat_id) - For external ID lookups
- player_histories(player_id, gameweek) - For gameweek queries
- fixtures(gameweek) - For gameweek queries
- fixtures(home_team_id), fixtures(away_team_id) - For team fixture lookups

## Data Update Strategy

### Static/Reference Data
- teams, positions: Update once per season or when changes occur

### Regular Updates
- players: Update core stats weekly after games
- player_histories: Add new entries weekly after games
- fixtures: Update at season start, refresh regularly for changes
- player_projections: Recalculate after each gameweek

## Data Migration and Versioning

The schema includes core tables needed for the application. As the project evolves, we may need to:

1. Add new tables for additional features
2. Add columns to existing tables for new metrics
3. Create views for commonly used queries
4. Implement a schema versioning mechanism for tracking changes

## Implementation with SQLAlchemy

We'll use SQLAlchemy ORM to interact with the database, which provides:
- Object-oriented access to database tables
- Automatic SQL generation
- Connection pooling
- Migration support via Alembic

## Next Steps

1. Implement the database schema using SQLAlchemy models
2. Create database initialization scripts
3. Develop data collection modules that populate these tables
4. Implement data validation and cleaning procedures
5. Create data access layer for the application logic