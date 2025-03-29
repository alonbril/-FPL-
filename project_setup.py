#!/usr/bin/env python3
"""
Premier League Fantasy Draft Assistant project setup script.
Run this script to create the project structure and initial files.
"""
import os
import shutil
import sys
from pathlib import Path


def create_directory(path):
    """Create directory if it doesn't exist."""
    try:
        os.makedirs(path, exist_ok=True)
        print(f"Created directory: {path}")
    except Exception as e:
        print(f"Error creating directory {path}: {e}")
        sys.exit(1)


def create_file(file_path, content=""):
    """Create a file with the given content."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created file: {file_path}")
    except Exception as e:
        print(f"Error creating file {file_path}: {e}")
        sys.exit(1)


def create_project_structure():
    """Create the full project structure."""
    # Project name
    project_name = "premier-league-fantasy-draft-assistant"

    # Create root project directory
    create_directory(project_name)

    # Change to project directory
    os.chdir(project_name)

    # Create main directories
    directories = [
        "data/raw",
        "data/processed",
        "data/test",
        "data/db",
        "src/data/collectors",
        "src/data/processors",
        "src/data/storage",
        "src/analysis",
        "src/draft",
        "src/cli",
        "src/web/templates",
        "src/web/static",
        "tests",
        "notebooks",
    ]

    for directory in directories:
        create_directory(directory)

    # Create __init__.py files for all Python packages
    python_dirs = [
        "src",
        "src/data",
        "src/data/collectors",
        "src/data/processors",
        "src/data/storage",
        "src/analysis",
        "src/draft",
        "src/cli",
        "src/web",
        "tests",
    ]

    for py_dir in python_dirs:
        create_file(f"{py_dir}/__init__.py")

    # Create .gitkeep files for empty directories to track them in git
    for directory in ["data/raw", "data/processed", "data/test", "data/db"]:
        create_file(f"{directory}/.gitkeep")

    # Create core project files
    create_file("README.md", README_CONTENT)
    create_file("requirements.txt", REQUIREMENTS_CONTENT)
    create_file("setup.py", SETUP_CONTENT)
    create_file(".gitignore", GITIGNORE_CONTENT)

    print("\nProject structure created successfully!")
    print(f"Project directory: {os.path.abspath(os.getcwd())}")
    print("\nNext steps:")
    print("1. Create a virtual environment: python -m venv venv")
    print("2. Activate the environment:")
    print("   - Windows: venv\\Scripts\\activate")
    print("   - Mac/Linux: source venv/bin/activate")
    print("3. Install dependencies: pip install -r requirements.txt")
    print("4. Initialize git repository: git init")
    print("5. Make initial commit: git add . && git commit -m 'Initial project setup'")


# Content for README.md
README_CONTENT = """# Premier League Fantasy Draft Assistant

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
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
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
"""

# Content for requirements.txt
REQUIREMENTS_CONTENT = """# Core packages
numpy>=1.20.0
pandas>=1.3.0
scikit-learn>=0.24.0
matplotlib>=3.4.0
seaborn>=0.11.0

# Data collection and APIs
requests>=2.25.0
beautifulsoup4>=4.9.0
lxml>=4.6.0
aiohttp>=3.7.0  # For async requests
fpl>=0.6.0      # Python wrapper for Fantasy Premier League API

# Database
sqlalchemy>=1.4.0

# Web development (for later weeks)
flask>=2.0.0
flask-wtf>=0.15.0
jinja2>=3.0.0

# CLI enhancements
colorama>=0.4.4
tqdm>=4.60.0
click>=8.0.0
tabulate>=0.8.9  # For formatting tabular data in the terminal

# Testing
pytest>=6.2.0
pytest-cov>=2.12.0

# Development tools
black>=21.5b0
flake8>=3.9.0
mypy>=0.812
jupyter>=1.0.0
"""

# Content for setup.py
SETUP_CONTENT = """from setuptools import setup, find_packages

setup(
    name="premier-league-fantasy-draft-assistant",
    version="0.1.0",
    description="A data-driven Premier League fantasy draft assistant tool",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy",
        "pandas",
        "scikit-learn",
        "matplotlib",
        "seaborn",
        "requests",
        "beautifulsoup4",
        "lxml",
        "aiohttp",
        "fpl",
        "sqlalchemy",
        "flask",
        "colorama",
        "tqdm",
        "click",
        "tabulate",
    ],
    entry_points={
        "console_scripts": [
            "fantasy-draft=src.cli.commands:main",
        ],
    },
    python_requires=">=3.8",
)
"""

# Content for .gitignore
GITIGNORE_CONTENT = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE specific files
.idea/
.vscode/
*.swp
*.swo

# Project specific
data/raw/*
data/processed/*
data/db/*
!data/raw/.gitkeep
!data/processed/.gitkeep
!data/db/.gitkeep

# API keys and secrets
.env
config.ini
secrets.json

# Database files
*.db
*.sqlite
*.sqlite3

# Logs
logs/
*.log
"""

if __name__ == "__main__":
    create_project_structure()