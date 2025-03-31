# Premier League Fantasy Draft Assistant

A comprehensive tool to help Premier League fantasy football players make data-driven decisions during their drafts.

## Features (Planned)

- **Player Data Collection**: Automated gathering of player stats, projections, and news
- **Value Calculations**: Advanced value calculations to identify the best picks
- **Risk Assessment**: Injury risk and consistency metrics for informed decision-making
- **Draft Strategy**: Position scarcity analysis and team needs assessment
- **Mock Draft Simulator**: Practice against AI drafters with different strategies
- **Command-Line Interface**: User-friendly terminal-based draft assistant
- **Web Interface**: Interactive draft board with real-time recommendations (coming later)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/premier-league-fantasy-draft-assistant.git
cd premier-league-fantasy-draft-assistant
```

2. Create and activate a virtual environment:
```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

*Detailed usage instructions will be added as features are implemented.*

## Project Structure

```
premier-league-fantasy-draft-assistant/
├── data/                      # Data directory
├── src/                       # Source code
│   ├── data/                  # Data collection and processing
│   ├── analysis/              # Analysis and projection modules
│   ├── draft/                 # Draft strategy components
│   ├── cli/                   # Command Line Interface
│   └── web/                   # Web application (future)
├── tests/                     # Test directory
└── notebooks/                 # Jupyter notebooks for exploration
```

## Development Timeline

This project is being developed according to a 7-week timeline:

- Week 1: Project Setup & Data Collection
- Week 2: Core Data Processing & Analysis
- Week 3: Draft Strategy Components
- Week 4: Command-Line Interface & Core Testing
- Week 5: Advanced Features (Part 1)
- Week 6: Web Interface & Advanced Features (Part 2)
- Week 7: Testing, Refinement & Documentation

## Contributing

This is a personal project in active development. Contributions, suggestions, and feedback are welcome!

## License

[MIT License](LICENSE)

## Data Sources

This project collects data from multiple sources:

- **Official Fantasy Premier League API**: Player data, fixtures, and fantasy metrics
- **Understat**: Advanced statistics (xG, xA, etc.)

See the `/docs` directory for detailed information on data collection.