from setuptools import setup, find_packages

setup(
    name="premier-league-fantasy-draft-assistant",
    version="0.1.0",
    description="A data-driven Premier League fantasy draft assistant tool",
    author="Alon Bril",
    author_email="alonbril5@gmail.com",
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
