# 📊 IPL Dashboard

Welcome to the IPL Dashboard! This is an interactive web dashboard built with Dash and Plotly for exploring IPL cricket statistics, team comparisons, and player insights. 🏏 The dashboard provides rich visualizations, season-wise analytics, and CSV export features for deep cricket data analysis.

---

## 🚀 Features

- **Multi-Tab Dashboard**: Overview, Batting Stats, Bowling Stats, Team Comparison, and Player Insights tabs for easy navigation.
- **Season & Team Filtering**: Filter all stats and charts by season and/or team. 📅
- **KPI Cards**: Key metrics (runs, wickets, averages, strike rates, best figures, etc.) in visually appealing cards. 🏆
- **Interactive Charts**: Bar, line, pie, and heatmap charts for top performers, run distributions, economy rates, and more. 📈
- **Player Insights**: Deep-dive into individual player stats, including season-wise and venue-wise breakdowns. 👤
- **CSV Export**: Save player stats to CSV for further analysis. 📤
- **Modern UI**: Custom CSS and dark theme for a polished, professional look. 🎨

---

## 🛠️ Technologies Used

- **Dash**: Python web framework for analytical apps. 🐍
- **Plotly**: Interactive charting library. 📊
- **Pandas**: Data manipulation and analysis. 🐼
- **CSV**: For data export and import. 📄

---

## 📂 Project Structure

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
│   └── data_loader.py      # Data loading, transformation, and chart logic
├── batter_stats.csv        # (Generated) Batting stats export
├── bowler_stats.csv        # (Generated) Bowling stats export
├── allrounder_stats.csv    # (Generated) Allrounder stats export
└── README.md               # This file
```

---

## 📋 Installation

### Prerequisites

- Python 3.7+ 🐍
- pip (Python package installer) 📦

### Clone the repository

```sh
git clone https://github.com/ChRaviTeja1901/ipl_dashboard.git
cd ipl_dashboard
```

### Install dependencies

```sh
pip install -r requirements.txt
```

### Add Data

- Place `matches.csv` and `deliveries.csv` in the `data/` folder.

### Run the app

```sh
python app.py
```

- Open your browser at [http://127.0.0.1:8050/](http://127.0.0.1:8050/)

---

## 📡 Dashboard Tabs & API

- **Overview**: IPL summary stats, most successful teams, venues, and more.
- **Batting Stats**: Top scorers, run distributions, team-wise averages, and grouped bar charts.
- **Bowling Stats**: Top wicket-takers, best figures, economy/strike rate/average by team and season.
- **Team Comparison**: Compare two teams head-to-head across seasons and venues.
- **Player Insights**: Select a player to view season-wise, venue-wise, and role-based stats, with CSV export.

### Key Functions (in `utils/data_loader.py`)

- `load_data()`: Loads and normalizes all IPL data.
- `get_summary_stats()`: Computes overall IPL summary metrics.
- `get_batsman_stats()`, `get_bowler_stats()`, `get_allrounder_stats()`: Compute detailed stats for each player type.
- `get_best_team_economy_by_season()`, `get_best_team_strike_rate_by_season()`, `get_best_team_average_by_season()`: Efficiently compute best team metrics for each season using groupby/idxmin.
- `get_most_expensive_overs()`: Returns a bar chart of the most expensive overs, using the filtered_df pattern.
- `get_player_stats()`: Returns player stats and can save them to CSV with the player's name included.

---

## 🤝 Contributing

We welcome contributions! To contribute:

1. Fork the repository. 🍴
2. Create a feature branch: `git checkout -b feature/your-feature` 🌱
3. Commit your changes: `git commit -am 'Add your feature'` 📦
4. Push to the branch: `git push origin feature/your-feature` ⬆️
5. Create a new Pull Request. 🔃

---

## 📜 License

This project is licensed under the MIT License ⚖️

---

## Credits

- Data: [IPL official datasets](https://www.kaggle.com/datasets/patrickb1912/ipl-complete-dataset-20082020)
- Built with Dash, Plotly, and Pandas

## 💡 Acknowledgements

- Dash, Plotly, and Pandas for making analytics easy and beautiful

---

For more details, see the code in each file or open an issue on GitHub!
