# Data Sources Research Summary and Recommendations

## Executive Summary

After evaluating available data sources for the Premier League Fantasy Draft Assistant, we recommend a hybrid approach using:

1. **Official Fantasy Premier League (FPL) API** as the primary source for player data, fixtures, and fantasy-specific metrics
2. **Understat** as a complementary source for advanced analytics (xG, xA)
3. **SQLite database** for efficient storage and retrieval

This approach balances data quality, accessibility, and technical feasibility while meeting the project's requirements.

## Key Findings

### FPL API Evaluation

✅ **Strengths**:
- Comprehensive coverage of all Premier League players
- Official source of fantasy points, prices, and ownership
- Reliable availability during the season
- No authentication required for basic endpoints
- Well-structured JSON responses

⚠️ **Limitations**:
- No official documentation (community-driven only)
- Limited historical data (current season emphasis)
- No advanced metrics like xG, xA
- Potential rate limiting

### Understat Evaluation

✅ **Strengths**:
- Rich advanced metrics (xG, xA, shot maps)
- Historical data going back several seasons
- Player performance details at match level
- Position-specific analytics

⚠️ **Limitations**:
- Requires web scraping (no official API)
- Player name mapping challenges
- Potential website structure changes
- Ethical/legal considerations with scraping

### Other Data Sources Considered

| Source | Verdict | Reasoning |
|--------|---------|-----------|
| FBref | Not recommended | Complex scraping, ToS concerns, redundant data |
| WhoScored | Not recommended | Strict anti-scraping measures, legal risks |
| Transfermarkt | Not recommended | Limited performance data, scraping complexity |
| Opta | Not viable | Requires paid enterprise subscription |

## Implementation Recommendations

### 1. Data Collection Strategy

**Primary Collection (Weekly)**:
- Full player data from FPL API
- Fixtures and results from FPL API
- Advanced statistics from Understat

**Quick Updates (Daily)**:
- Player status changes (injuries, suspensions)
- Price changes
- Ownership changes

**Season Initialization (Annual)**:
- Team data
- Position categories
- Player reference data

### 2. Technical Implementation

**FPL API Access**:
- Implement rate limiting (max 1 request per second)
- Use async requests for efficiency
- Cache responses to reduce API load
- Implement error handling and retries

**Understat Scraping**:
- Respect robots.txt directives
- Implement 2-3 second delays between requests
- Extract data from embedded JSON (avoid HTML parsing)
- Create robust player matching system

**Database Schema**:
- Implement the schema defined in `database-schema.md`
- Use SQLAlchemy ORM for database operations
- Create indexes for frequent query patterns
- Implement regular database backups

### 3. Player Mapping Strategy

The most challenging aspect will be mapping players between FPL and Understat due to naming differences. Recommended approach:

1. **Primary Matching**: Team + fuzzy name matching
2. **Secondary Matching**: Position + performance stats correlation
3. **Manual Mapping**: Build and maintain a mapping table for edge cases
4. **Regular Verification**: Weekly check for new players or transfers

### 4. Legal and Ethical Considerations

- **FPL API**: While unofficial, public access is well-established
- **Understat**: 
  - No explicit prohibition against scraping
  - Implement rate limiting to avoid server impact
  - Consider caching data to reduce request frequency
  - Don't circumvent any new anti-scraping measures they might implement

## Next Steps

1. **Build Data Collection Foundation**:
   - Implement FPL API client (already in progress in `fpl_api.py`)
   - Develop Understat scraper with player mapping (started in `understat_api.py`)
   - Create database schema and handler (in progress in `db_handler.py`)

2. **Test Data Collection**:
   - Verify complete data flow from sources to database
   - Validate player mapping accuracy
   - Measure collection time and optimize if needed

3. **Schedule Updates**:
   - Create automation for regular data refreshes
   - Implement change detection to minimize processing
   - Add logging for collection process monitoring

4. **Documentation**:
   - Document API endpoints and parameters
   - Create data dictionary for all collected fields
   - Document player mapping algorithm
   - Maintain changelog for data source changes

5. **Data Validation**:
   - Implement validation checks for incoming data
   - Create tests to verify data integrity
   - Build alerting for data collection failures
   - Develop reconciliation tools for inconsistencies

## Data Fields Selection

Based on our research, we've identified the following key data fields for collection:

### From Fantasy Premier League API

**Core Player Information**:
- Player ID, first name, second name, web name
- Team and position
- Current price and price changes
- Form and fitness status
- Ownership percentage
- Availability status (injuries, suspensions)

**Performance Statistics**:
- Minutes played
- Goals, assists, clean sheets
- Yellow/red cards
- Saves (goalkeepers)
- Bonus points
- Total fantasy points and points per game
- Bonus Point System (BPS) components
- ICT index (influence, creativity, threat)

**Fixture Information**:
- Match schedule
- Fixture difficulty ratings
- Home/away designation
- Gameweek number
- Blank/double gameweeks

### From Understat

**Advanced Metrics**:
- Expected Goals (xG)
- Expected Assists (xA)
- Non-penalty Expected Goals (npxG)
- xG per 90 minutes
- xA per 90 minutes
- Shot statistics (number, location, result)
- Key passes

### Calculated/Derived Fields

Once we have collected the raw data, we'll calculate additional metrics:
- Value metrics (points per cost)
- Points over replacement player
- Risk assessment scores
- Consistency metrics
- Form trajectory
- Position scarcity metrics
- Draft value rankings

## Technical Implementation Outline

We recommend implementing the data collection in stages:

1. **Stage 1**: Core FPL API integration
   - Connect to all essential endpoints
   - Build database storage layer
   - Create basic data processing pipeline

2. **Stage 2**: Understat Integration
   - Implement web scraping module
   - Create player mapping system
   - Integrate advanced statistics

3. **Stage 3**: Data Enrichment
   - Calculate derived metrics
   - Implement projection algorithms
   - Build consistency and risk metrics

4. **Stage 4**: Automation
   - Schedule regular updates
   - Implement change detection
   - Add monitoring and alerting

## Conclusion

The research conducted confirms that combining data from the FPL API and Understat will provide a comprehensive dataset for the Fantasy Draft Assistant. The implementation plan outlined above provides a clear roadmap for the data collection phase of the project.

By following these recommendations, we can build a robust data foundation that will support all the planned features of the Premier League Fantasy Draft Assistant, including value calculations, risk assessment, and draft strategy components.

---

**Next Task**: Proceed to "Implement data collection" as outlined in the project timeline.