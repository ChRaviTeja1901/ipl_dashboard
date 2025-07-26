# IPL Dashboard

A comprehensive IPL analytics dashboard built with Dash and Plotly for interactive cricket statistics, team comparisons, and player insights.

## Features

- **Interactive Dashboard**: Multi-tab layout for batting, bowling, overview, player insights, and team comparison.
- **Season & Team Filtering**: All major stats and charts can be filtered by season and/or team.
- **KPI Cards**: Key metrics for batting and bowling (runs, wickets, averages, strike rates, best figures, etc.) are shown in visually consistent cards.
- **Charts**: Bar, line, pie, and heatmap charts for top performers, run distributions, economy rates, and more.
- **Player Insights**: Deep-dive into individual player stats, including season-wise breakdowns, venue performance, and role-based KPIs.
- **CSV Data Export**: Player stats can be saved to CSV for further analysis.
- **Custom Styling**: Modern dark theme with custom CSS for a polished look.

## Project Structure

```
ipl_dashboard/
├── app.py                  # Main Dash app entry point
├── assets/
│   └── style.css           # Custom dashboard styling
├── data/
│   ├── matches.csv         # Raw IPL match data
│   └── deliveries.csv      # Raw IPL ball-by-ball data
├── tabs/
│   ├── overview.py         # Overview tab
│   ├── batting_stats.py    # Batting stats tab
│   ├── bowling_stats.py    # Bowling stats tab
│   ├── player_insights.py  # Player insights tab
│   └── teams_comparison.py # Team comparison tab
├── utils/
│   └── data_loader.py      # All data loading, transformation, and chart logic
└── README.md               # This file
```

## Data Flow & Key Patterns

- **Data Loading**: All data is loaded and normalized in `utils/data_loader.py`.
- **Filtered DataFrames**: All stats and charts use the `filtered_df = ...` pattern for season/team filtering.
- **Chart Generation**: All charts are built with Plotly and use a consistent dark theme and custom hovertemplates.
- **KPI Cards**: KPI values are computed using dictionary comprehensions and displayed in multi-row, multi-column layouts.
- **Team/Venue Normalization**: Team and venue names are normalized using `TEAM_MAP` and `VENUE_MAP`.
- **Color Schemes**: Team colors are defined in `TEAM_COLORS` for consistent chart coloring.
- **CSV Export**: Player stats can be saved to CSV using a DataFrame and `to_csv` with header management.

## Notable Functions & Logic

- `load_data()`: Loads and normalizes all IPL data.
- `get_summary_stats()`: Computes overall IPL summary metrics.
- `get_batsman_stats()`, `get_bowler_stats()`, `get_allrounder_stats()`: Compute detailed stats for each player type.
- `get_best_team_economy_by_season()`, `get_best_team_strike_rate_by_season()`, `get_best_team_average_by_season()`: Efficiently compute best team metrics for each season using groupby/idxmin.
- `get_most_expensive_overs()`: Returns a bar chart of the most expensive overs, using the filtered_df pattern.
- `get_player_stats()`: Returns player stats and can save them to CSV with the player's name included.
- All tab files use Dash callbacks to update KPIs and charts based on user input.

## How to Run

1. Place `matches.csv` and `deliveries.csv` in the `data/` folder.
2. Install requirements: `pip install dash plotly pandas`
3. Run the app: `python app.py`
4. Open the dashboard in your browser (usually at http://127.0.0.1:8050/)

## Developer Notes

- To add a new tab, create a file in `tabs/` and register it in `app.py`.
- To add a new metric, add logic in `data_loader.py` and update the relevant tab.
- To change the UI, edit `assets/style.css`.
- All code uses the `filtered_df` pattern for maintainability and consistency.
- Player stats CSVs are generated with the player's name included for clarity.

## Credits

- Data: [IPL official datasets](https://www.kaggle.com/datasets/patrickb1912/ipl-complete-dataset-20082020)
- Built with Dash, Plotly, and Pandas
