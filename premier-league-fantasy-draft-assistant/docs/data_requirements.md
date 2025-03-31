# Data Points Required for Premier League Fantasy Draft Assistant

This document outlines the essential and desired data points for the Premier League Fantasy Draft Assistant project, sorted by category and priority.

## Core Player Information

### Essential
- **Player ID**: Unique identifiers from FPL API and other sources (for matching)
- **Name**: Full name and display name
- **Team**: Current team
- **Position**: GK, DEF, MID, FWD
- **Price**: Current price in fantasy league
- **Availability**: Injury status, suspensions, international duty
- **Selected By %**: Ownership percentage
- **Form**: Recent performance metric

### Nice-to-Have
- **Age**: Player's age
- **Height/Weight**: Physical attributes
- **Nationality**: Country of origin
- **Contract Information**: Expiry date, potential transfers
- **Years in Premier League**: Experience metric

## Performance Statistics

### Essential
- **Minutes Played**: Total and per game
- **Goals**: Total goals scored
- **Assists**: Total assists provided
- **Clean Sheets**: For defenders and goalkeepers
- **Saves**: For goalkeepers
- **Bonus Points**: FPL bonus points received
- **Total Points**: Season fantasy points
- **Points Per Game**: Average fantasy points per appearance
- **ICT Index**: Influence, Creativity, and Threat metrics

### Nice-to-Have
- **Shots**: Total shots and shots on target
- **Passes**: Total passes and pass completion rate
- **Key Passes**: Passes leading to shots
- **Crosses**: Total crosses and accuracy
- **Tackles**: Successful tackles
- **Interceptions**: Ball interceptions
- **Clearances**: Defensive clearances
- **Blocks**: Shots and crosses blocked
- **Errors Leading to Goals**: Defensive errors

## Advanced Metrics

### Essential
- **xG (Expected Goals)**: Statistical probability of scoring
- **xA (Expected Assists)**: Statistical probability of assists
- **npxG (Non-Penalty Expected Goals)**: xG excluding penalties
- **xG per 90**: Expected goals per 90 minutes
- **xA per 90**: Expected assists per 90 minutes
- **xGI (Expected Goal Involvement)**: Combined xG and xA

### Nice-to-Have
- **xGChain**: Expected goals from every possession the player is involved in
- **xGBuildup**: xGChain excluding shots and assists
- **xGD (Expected Goal Difference)**: Team-level metric when player is on field
- **VAEP (Valuing Actions by Estimating Probabilities)**: Advanced player contribution metric
- **Defensive xG Prevention**: Expected goals prevented by defensive actions

## Consistency and Risk Metrics

### Essential
- **Minutes Risk**: Probability of limited playing time
- **Injury Proneness**: Historical injury frequency and severity
- **Consistency Score**: Variance in performance
- **Home/Away Performance Split**: Difference in performance by venue
- **Form Trajectory**: Improving or declining recent performances

### Nice-to-Have
- **Performance vs. Top Teams**: Points against top-6 opposition
- **Performance vs. Bottom Teams**: Points against bottom-6 opposition
- **Weather Impact**: Performance in different weather conditions
- **Rotation Risk**: Likelihood of being rotated in/out of the team
- **European Competition Impact**: Effect of Champions/Europa League on performances

## Fixture Analysis

### Essential
- **Upcoming Fixtures**: Next 5-10 opponents
- **Fixture Difficulty Rating (FDR)**: Difficulty assessment of upcoming games
- **Double/Blank Gameweeks**: Weeks with 0 or 2+ fixtures
- **Team Attacking Strength**: Team's overall attacking potential
- **Team Defensive Strength**: Team's overall defensive reliability

### Nice-to-Have
- **Historical Performance vs. Opponents**: Player's record against upcoming opponents
- **Team Playstyle Compatibility**: How opposition tactics might affect the player
- **Home Advantage Metrics**: Specific home/away fixture analysis
- **Distance Traveled**: Impact of travel on team performance
- **Rest Days Between Fixtures**: Schedule congestion analysis

## Draft Strategy Data

### Essential
- **Position Scarcity**: Relative value of positions in draft format
- **Replacement Value**: Value over replacement player in same position
- **Value-Based Ranking**: Overall ranking based on value calculations
- **Tier Groupings**: Players grouped by expected output tiers
- **Positional Flexibility**: Players eligible in multiple positions

### Nice-to-Have
- **ADP (Average Draft Position)**: Where players typically get drafted
- **Sleeper Rating**: Undervalued players with high potential
- **Bust Potential**: Overvalued players with high risk
- **Positional Balance Strategy**: Recommended position drafting sequence
- **Handcuff Players**: Strategic backups for injury-prone stars

## Data Integration Requirements

### Essential
- **Player Name Mapping**: System to match players across different data sources
- **Data Freshness Tracking**: Last update timestamps for all data sources
- **Data Source Credibility Rating**: Reliability assessment of each source
- **Historical Data Storage**: At least 2-3 seasons of past performance
- **Update Frequency**: Minimum update requirements by data category

### Nice-to-Have
- **API Rate Limit Tracking**: Usage monitoring for external APIs
- **Data Quality Scoring**: Assessment of data completeness and accuracy
- **Fallback Data Sources**: Alternative sources when primary sources fail
- **Data Conflict Resolution**: Rules for handling contradictory information
- **Import/Export Capabilities**: Support for common fantasy platform formats