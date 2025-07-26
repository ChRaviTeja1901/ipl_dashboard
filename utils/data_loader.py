import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import colorsys

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_lighter_shades(hex_color, n):
    rgb = hex_to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(*(c/255.0 for c in rgb))
    # Generate n shades from original lightness to 0.85
    return [
        f"rgb({int(r*255)},{int(g*255)},{int(b*255)})"
        for l_val in [l + (0.85 - l) * (i / max(n-1,1)) for i in range(n)]
        for r, g, b in [colorsys.hls_to_rgb(h, min(l_val, 0.95), s)]
    ]

VENUE_MAP = {
    'Arun Jaitley Stadium, Delhi': 'Arun Jaitley Stadium',
    'Brabourne Stadium, Mumbai': 'Brabourne Stadium',
    'Dr DY Patil Sports Academy, Mumbai': 'Dr DY Patil Sports Academy',
    'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam': 'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium',
    'Eden Gardens, Kolkata': 'Eden Gardens',
    'M Chinnaswamy Stadium, Bengaluru': 'M Chinnaswamy Stadium',
    'M.Chinnaswamy Stadium': 'M Chinnaswamy Stadium',
    'MA Chidambaram Stadium, Chepauk': 'MA Chidambaram Stadium',
    'MA Chidambaram Stadium, Chepauk, Chennai': 'MA Chidambaram Stadium',
    'Maharashtra Cricket Association Stadium, Pune': 'Maharashtra Cricket Association Stadium',
    'Narendra Modi Stadium, Ahmedabad': 'Narendra Modi Stadium',
    'Punjab Cricket Association IS Bindra Stadium, Mohali': 'Punjab Cricket Association IS Bindra Stadium',
    'Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh': 'Punjab Cricket Association IS Bindra Stadium',
    'Punjab Cricket Association Stadium, Mohali': 'Punjab Cricket Association IS Bindra Stadium',
    'Rajiv Gandhi International Stadium, Uppal': 'Rajiv Gandhi International Stadium',
    'Rajiv Gandhi International Stadium, Uppal, Hyderabad': 'Rajiv Gandhi International Stadium',
    'Sardar Patel Stadium, Motera': 'Narendra Modi Stadium',
    'Sawai Mansingh Stadium, Jaipur': 'Sawai Mansingh Stadium',
    'Zayed Cricket Stadium, Abu Dhabi': 'Sheikh Zayed Stadium',
    'Himachal Pradesh Cricket Association Stadium, Dharamsala': 'Himachal Pradesh Cricket Association Stadium',
    'Wankhede Stadium, Mumbai': 'Wankhede Stadium'
}

TEAM_MAP = {
    'Deccan Chargers': 'Sunrisers Hyderabad',
    'Delhi Daredevils': 'Delhi Capitals',
    'Rising Pune Supergiant': 'Rising Pune Supergiants',
    'Pune Warriors': 'Rising Pune Supergiants',
    'Royal Challengers Bangalore': 'Royal Challengers Bengaluru',
    'Kings XI Punjab': 'Punjab Kings',
    'Gujarat Lions': 'Gujarat Titans'
}

TEAM_COLORS = {
    'Sunrisers Hyderabad': '#FF6F00',
    'Rajasthan Royals': '#EA1C81',
    'Gujarat Titans': '#0F1C3F',
    'Mumbai Indians': '#004BA0',
    'Chennai Super Kings': '#FFCB05',
    'Punjab Kings': "#E52E1A",
    'Kolkata Knight Riders': '#3B0A55',
    'Lucknow Super Giants': '#5DC2E8',
    'Delhi Capitals': "#17179B",
    'Royal Challengers Bengaluru': "#b50303",
    'Kochi Tuskers Kerala': "#FFAE42",
    'Rising Pune Supergiants': "#DA70D6"
}

TEAM_SHORT_NAMES = {
    'Sunrisers Hyderabad': 'SRH',
    'Rajasthan Royals': 'RR',
    'Gujarat Titans': 'GT',
    'Mumbai Indians': 'MI',
    'Chennai Super Kings': 'CSK',
    'Punjab Kings': "PK",
    'Kolkata Knight Riders': 'KKR',
    'Lucknow Super Giants': 'LSG',
    'Delhi Capitals': "DC",
    'Royal Challengers Bengaluru': "RCB",
    'Kochi Tuskers Kerala': "KTK",
    'Rising Pune Supergiants': "RPS"
}

def player_played_team_each_season(df, player):
    marker_colors = []
    played_teams = []
    df = df[df['batter'] == player]
    for season in df['season'].unique():
        season_matches_row = df[df['season'] == season]
        if not season_matches_row.empty:
            team_name = season_matches_row['batting_team'].iloc[0]
            if team_name in TEAM_COLORS:
                marker_colors.append(TEAM_COLORS[team_name])
                played_teams.append(team_name)
            else:
                marker_colors.append('#888888')  
        else:
            marker_colors.append('#888888')
    return played_teams, marker_colors

def player_last_played_team(df, player):
    df = df[df['batter'] == player]
    if df.empty:
        return '#888888'
    last_season = df['season'].max()
    last_season_rows = df[df['season'] == last_season]
    if last_season_rows.empty:
        return '#888888'
    team = last_season_rows['batting_team'].iloc[0]
    return TEAM_COLORS.get(team, '#888888')

def top_players():
    deliveries_df = pd.read_csv('data/deliveries.csv')
    deliveries_df.columns = deliveries_df.columns.str.strip().str.lower()

    # Batting Stats
    batting_stats = deliveries_df.groupby('batter').agg(
        runs_scored=('batsman_runs', 'sum'),
        balls_faced=('batter', 'count')
    ).reset_index().rename(columns={'batter': 'player'})

    # Bowling Stats
    bowling_stats = deliveries_df[deliveries_df['bowler'].notnull()].groupby('bowler').agg(
        balls_bowled=('bowler', 'count'),
        wickets=('dismissal_kind', lambda x: x.isin([
            'caught', 'bowled', 'lbw', 'stumped', 'caught and bowled', 'hit wicket'
        ]).sum())
    ).reset_index().rename(columns={'bowler': 'player'})

    # Merge
    player_stats = pd.merge(batting_stats, bowling_stats, on='player', how='outer').fillna(0)

    # Classify and Rank
    batsmen_df = player_stats[(player_stats['runs_scored'] > 1000) | (player_stats['balls_faced'] > 500)].copy()
    bowlers_df = player_stats[(player_stats['wickets'] > 50) | (player_stats['balls_bowled'] > 300)].copy()
    allrounders_df = player_stats[
        ((player_stats['runs_scored'] > 1000) | (player_stats['balls_faced'] > 500)) &
        ((player_stats['wickets'] > 50) | (player_stats['balls_bowled'] > 300))
    ].copy()

    # Ranking
    batsmen_df = batsmen_df.sort_values(by='runs_scored', ascending=False).head(20)
    bowlers_df = bowlers_df.sort_values(by='wickets', ascending=False).head(20)
    allrounders_df['allrounder_score'] = allrounders_df['runs_scored'] + (20 * allrounders_df['wickets'])
    allrounders_df = allrounders_df.sort_values(by='allrounder_score', ascending=False).head(20)

    return batsmen_df['player'].tolist(), bowlers_df['player'].tolist(), allrounders_df['player'].tolist()

BATSMANS, BOWLERS, ALL_ROUNDERS = top_players()

def load_data():
    """
    Load IPL match and delivery data from CSV files, normalize venue and team names, and merge for analysis.
    Returns:
        matches_df (DataFrame): Match-level data
        deliveries_df (DataFrame): Ball-by-ball data
        ipl_df (DataFrame): Merged ball-by-ball with match info
    """
    # Load raw CSV data
    matches_df = pd.read_csv('data/matches.csv')
    deliveries_df = pd.read_csv('data/deliveries.csv')

    # Normalize venue names in matches
    matches_df['venue'] = matches_df['venue'].replace(VENUE_MAP)

    # Normalize team names in both matches and deliveries
    deliveries_df.replace(TEAM_MAP, inplace=True)
    matches_df.replace(TEAM_MAP, inplace=True)

    # Merge ball-by-ball data with match info
    ipl_df = deliveries_df.merge(matches_df, left_on='match_id', right_on='id')

    return matches_df, deliveries_df, ipl_df

def update_layout(fig):
    """
    Apply a consistent dark theme and white font to Plotly figures for the dashboard.
    Args:
        fig (go.Figure): Plotly figure object
    Returns:
        go.Figure: Updated figure with dashboard styling
    """
    fig.update_layout(
        paper_bgcolor='#1e1e2f',  # Dashboard background
        plot_bgcolor='#1e1e2f',   # Chart background
        font_color='white',       # Font color for all text
        xaxis=dict(
            showline=False,
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(
            showline=False,
            showgrid=False,
            zeroline=False,
        )
    )
    # Add white border to markers and white font for hover labels
    fig.update_traces(marker=dict(line=dict(color='white', width=1)), hoverlabel=dict(font=dict(color='white')))
    return fig

def add_tick_labels(fig):
    """
    Add season tick labels to the x-axis of a Plotly figure for IPL charts.
    Args:
        fig (go.Figure): Plotly figure object
    """
    season_labels = list(map(str, range(2008, 2025)))
    fig.update_layout(xaxis=dict(
        categoryorder='array',
        categoryarray=season_labels,
        tickangle=0,
        tickmode='array',
        tickvals=season_labels
    ))

def get_summary_stats(matches):
    """
    Get summary statistics for the IPL dataset.
    Args:
        matches (DataFrame): Match-level data
    Returns:
        tuple: (total_matches, total_seasons, total_teams, total_venues)
    """
    num_matches = matches.shape[0]
    num_seasons = matches['season'].nunique()
    num_teams = matches['team1'].nunique()
    num_venues = matches['venue'].nunique()
    most_successful_team = matches['winner'].value_counts().idxmax()
    most_successful_team_wins = matches['winner'].value_counts().max()
    highest_match_aggregate = matches['result_margin'].max()
    most_common_venue = matches['venue'].value_counts().idxmax()
    most_common_venue_count = matches['venue'].value_counts().max()
    return {
        'total_matches': num_matches,
        'total_seasons': num_seasons,
        'total_teams': num_teams,
        'total_venues': num_venues,
        'most_successful_team': most_successful_team,
        'most_successful_team_wins': most_successful_team_wins,
        'highest_match_aggregate': highest_match_aggregate,
        'most_common_venue': most_common_venue,
        'most_common_venue_count': most_common_venue_count
    }

def get_total_matches_per_season(matches):
    """
    Plot total matches played per season as a bar chart.
    Args:
        matches (DataFrame): Match-level data
    Returns:
        go.Figure: Bar chart of matches per season
    """
    matches_count_by_season = matches['season'].value_counts().sort_index()
    bar_trace = go.Bar(
        x=matches_count_by_season.index,
        y=matches_count_by_season.values,
        hovertemplate='Season: %{x}<br>Matches: %{y}<extra></extra>'
    )
    fig = go.Figure([bar_trace])
    fig.update_layout(title='Matches per Season')
    add_tick_labels(fig)
    return update_layout(fig)

def get_matches_won(matches):
    """
    Plot pie chart of matches won after batting or fielding first.
    Args:
        matches (DataFrame): Match-level data
    Returns:
        go.Figure: Pie chart of win type distribution
    """
    win_type_df = matches[matches['result'].isin(['runs', 'wickets'])]
    win_type_df = win_type_df.groupby('result').size().reset_index(name='count')
    win_type_df.replace({'runs': 'Batting First', 'wickets': 'Fielding First'}, inplace=True)
    pie_trace = go.Pie(
        labels=win_type_df['result'],
        values=win_type_df['count'],
        textinfo='label+percent',
        hoverinfo='label+value+percent',
        hole=0.3,
        hoverlabel=dict(font=dict(color='white')),
        hovertemplate='Type: %{label}<br>Count: %{value}<extra></extra>'
    )
    fig = go.Figure([pie_trace])
    fig.update_layout(title=dict(text='No.of Matches won after batting/fielding first', x=0.5, xanchor='center'), legend=dict(title='Innings Type'))
    return update_layout(fig)

def get_toss_decision(matches):
    """
    Plot pie chart of toss decisions (batting/fielding).
    Args:
        matches (DataFrame): Match-level data
    Returns:
        go.Figure: Pie chart of toss decisions
    """
    toss_decision_counts = matches.groupby('toss_decision').size().reset_index(name='count')
    labels = ['Batting', 'Fielding']
    pie_trace = go.Pie(
        labels=labels,
        values=toss_decision_counts['count'],
        insidetextfont=dict(color='white'),
        textinfo='label+percent',
        hoverinfo='label+value+percent',
        hole=0.3,
        hoverlabel=dict(font=dict(color='white')),
        hovertemplate='Decision: %{label}<br>Count: %{value}<extra></extra>'
    )
    fig = go.Figure([pie_trace])
    fig.update_layout(legend=dict(title='Toss Decision'), title=dict(text='Toss Decision'))
    return update_layout(fig)

def get_team_wins(matches):
    """
    Plot horizontal bar chart of total wins by each team.
    Args:
        matches (DataFrame): Match-level data
    Returns:
        go.Figure: Bar chart of team wins
    """
    team_win_counts = matches.groupby('winner').size().reset_index(name='total_wins').sort_values(by='total_wins')
    bar_trace = go.Bar(
        x=team_win_counts['total_wins'],
        y=team_win_counts['winner'],
        orientation='h',
        hovertemplate='Team: %{y}<br>Wins: %{x}<extra></extra>'
    )
    fig = go.Figure([bar_trace])
    fig.update_layout(title='Most Wins by Team', xaxis=dict(showticklabels=False))
    return update_layout(fig)

def get_top_scorers(ipl, n, seasons=None):
    """
    Plot top N batsmen by total runs as a horizontal bar chart or return top batsman as string.
    Args:
        ipl (DataFrame): Ball-by-ball data merged with match info
        n (int): Number of top batsmen to show
        seasons (list, optional): Filter by seasons
    Returns:
        str: If n==1, returns formatted string for top batsman
        go.Figure: Otherwise, returns bar chart
    """
    filtered_ipl_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    batsman_run_stats = filtered_ipl_df.groupby('batter')['batsman_runs'].sum().reset_index(name='Total Runs')
    batsman_run_stats.rename(columns={'batter': 'Batsman'}, inplace=True)
    top_batsmen_df = batsman_run_stats.sort_values(by='Total Runs', ascending=False).head(n)[::-1]
    if n == 1:
        top_batsman = top_batsmen_df['Batsman'].values[0]
        top_runs = top_batsmen_df['Total Runs'].values[0]
        return f"{top_batsman} ({top_runs} runs)"
    bar_trace = go.Bar(
        x=top_batsmen_df['Total Runs'],
        y=top_batsmen_df['Batsman'],
        orientation='h',
        hovertemplate='Batsman: %{y}<br>Runs: %{x}<extra></extra>'
    )
    fig = go.Figure([bar_trace])
    fig.update_layout(title=dict(text='Top Scorers'), xaxis=dict(showticklabels=False))
    return update_layout(fig)

def get_top_bowlers(ipl, n, seasons=None):
    """
    Plot top N bowlers by wickets and by economy (min 100 overs).
    Args:
        ipl (DataFrame): Ball-by-ball data merged with match info
        n (int): Number of top bowlers to show
        seasons (list, optional): Filter by seasons
    Returns:
        str: If n==1, returns formatted string for top bowler
        tuple(go.Figure, go.Figure): Bar charts for wickets and economy
    """
    filtered_ipl_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    valid_dismissals = ['bowled', 'caught', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
    filtered_ipl_df = filtered_ipl_df[filtered_ipl_df['dismissal_kind'].isin(valid_dismissals) | filtered_ipl_df['dismissal_kind'].isnull()]
    legal_deliveries_df = filtered_ipl_df[~filtered_ipl_df['extra_runs'].isin(['wides', 'noballs'])]
    bowler_agg_stats = legal_deliveries_df.groupby('bowler').agg(
        total_runs_conceded=('total_runs', 'sum'),
        total_wickets_taken=('is_wicket', 'sum'),
        total_balls_bowled=('ball', 'count')
    ).reset_index()

    bowler_agg_stats['total_overs_bowled'] = bowler_agg_stats['total_balls_bowled'] / 6
    bowler_agg_stats['economy'] = bowler_agg_stats['total_runs_conceded'] / bowler_agg_stats['total_overs_bowled']
    
    # Top Bowlers by Wickets
    top_wicket_bowlers_df = bowler_agg_stats.sort_values(by='total_wickets_taken', ascending=False).head(n)[::-1]
    if n == 1:
        top_bowler = top_wicket_bowlers_df['bowler'].values[0]
        top_wickets = top_wicket_bowlers_df['total_wickets_taken'].values[0]
        return f"{top_bowler} ({top_wickets} wickets)"
    wickets_bar_trace = go.Bar(
        x=top_wicket_bowlers_df['total_wickets_taken'],
        y=top_wicket_bowlers_df['bowler'],
        orientation='h',
        hovertemplate='Bowler: %{y}<br>Wickets: %{x}<extra></extra>'
    )
    fig_wickets = go.Figure([wickets_bar_trace])
    fig_wickets.update_layout(title=dict(text='Top Bowlers by Wickets'), xaxis=dict(showticklabels=False))
    
    # Top Bowlers by Economy (min 100 overs)
    top_economy_bowlers_df = bowler_agg_stats[bowler_agg_stats['total_overs_bowled'] >= 100].sort_values(by='economy').head(n)[::-1]
    economy_bar_trace = go.Bar(
        x=top_economy_bowlers_df['economy'],
        y=top_economy_bowlers_df['bowler'],
        orientation='h',
        hovertemplate='Bowler: %{y}<br>Economy: %{x:.2f}<extra></extra>'
    )
    fig_economy = go.Figure([economy_bar_trace])
    fig_economy.update_layout(title=dict(text='Top Bowlers by Economy (Min 100 Overs)'), xaxis=dict(showticklabels=False))
    return update_layout(fig_wickets), update_layout(fig_economy)

def get_total_runs(ipl, seasons=None):
    """
    Calculate total runs scored, optionally filtered by season.
    Args:
        ipl (DataFrame): Ball-by-ball data
        seasons (list, optional): Filter by seasons
    Returns:
        int: Total runs
    """
    filtered_ipl_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    total_runs_scored = filtered_ipl_df['total_runs'].sum()
    return int(total_runs_scored)

def get_total_wickets(ipl, seasons=None):
    """
    Calculate total wickets taken, optionally filtered by season.
    Args:
        ipl (DataFrame): Ball-by-ball data
        seasons (list, optional): Filter by seasons
    Returns:
        int: Total wickets
    """
    filtered_ipl_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    total_wickets_taken = filtered_ipl_df['is_wicket'].sum()
    return int(total_wickets_taken)

def get_total_matches(matches, seasons=None):
    """
    Calculate total matches played, optionally filtered by season.
    Args:
        matches (DataFrame): Match-level data
        seasons (list, optional): Filter by seasons
    Returns:
        int: Total matches
    """
    if seasons:
        filtered_matches_df = matches[matches['season'].isin(seasons)].copy()
        total_matches_played = filtered_matches_df['id'].size
        return total_matches_played
    else:
        total_matches_played = matches['id'].size
        return total_matches_played

def get_runs_distribution(ipl, seasons=None):
    """
    Plot pie chart of runs distribution (4s, 6s, other).
    Args:
        ipl (DataFrame): Ball-by-ball data
        seasons (list, optional): Filter by seasons
    Returns:
        go.Figure: Pie chart of runs distribution
    """
    filtered_ipl_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    filtered_ipl_df = filtered_ipl_df[filtered_ipl_df['total_runs'] != 0]
    filtered_ipl_df['run_type'] = filtered_ipl_df['total_runs'].apply(lambda runs: '4s' if runs == 4 else ('6s' if runs == 6 else 'Other'))
    run_type_stats_df = filtered_ipl_df.groupby('run_type').size().reset_index(name='count')
    pie_trace = go.Pie(
        labels=run_type_stats_df['run_type'],
        values=run_type_stats_df['count'],
        insidetextfont=dict(color='white'),
        textinfo='label+percent',
        hoverinfo='label+value+percent',
        hole=0.3,
        hoverlabel=dict(font=dict(color='white')),
        hovertemplate='Type: %{label}<br>Count: %{value}<extra></extra>'
    )
    fig = go.Figure([pie_trace])
    fig.update_layout(legend=dict(title='Runs Distribution'), title='Overall Runs Distribution')
    return update_layout(fig)

def get_runs_distribution_per_over(ipl, seasons=None):
    """
    Plot line chart of runs scored per over, with phase regions and annotations.
    Args:
        ipl (DataFrame): Ball-by-ball data
        seasons (list, optional): Filter by seasons
    Returns:
        go.Figure: Line chart of runs per over
    """
    filtered_ipl_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    runs_by_over = filtered_ipl_df.groupby('over')['total_runs'].sum()
    line_trace = go.Scatter(
        x=runs_by_over.index + 1,
        y=runs_by_over.values,
        mode='lines+markers',
        line=dict(shape='spline', width=3, color='deepskyblue'),
        marker=dict(size=10, color='deepskyblue', line=dict(width=2, color='white')),
        hovertemplate='Over: %{x}<br>Runs: %{y}<extra></extra>'
    )
    fig = go.Figure([line_trace])
    max_y = runs_by_over.max() + 1000  # dynamic height for annotation
    # Add phase regions (Powerplay, Middle, Death)
    fig.add_shape(type='rect', x0=1, x1=6, y0=0, y1=max_y, fillcolor='rgba(30,144,255, 0.2)', layer='below', line_width=0)
    fig.add_shape(type='rect', x0=6, x1=15, y0=0, y1=max_y, fillcolor='rgba(255,105,180, 0.2)', layer='below', line_width=0)
    fig.add_shape(type='rect', x0=15, x1=20, y0=0, y1=max_y, fillcolor='rgba(60,179,113, 0.2)', layer='below', line_width=0)
    # Add phase annotations
    fig.add_annotation(x=3.5, y=max_y, text='Powerplay Overs', showarrow=False, font=dict(size=13), bgcolor="deepskyblue", borderpad=6)
    fig.add_annotation(x=10.5, y=max_y, text='Middle Overs', showarrow=False, font=dict(size=13), bgcolor="hotpink", borderpad=6)
    fig.add_annotation(x=18, y=max_y, text='Death Overs', showarrow=False, font=dict(size=13), bgcolor="mediumseagreen", borderpad=6)
    fig.update_layout(title='Runs Distribution by Over', xaxis=dict(categoryorder='array', categoryarray=list(map(str, range(1, 21))), tickmode='array', tickvals=list(map(str, range(1, 21)))))
    return update_layout(fig)

def get_batting_runrate_by_team(ipl, seasons=None):
    """
    Generate a line chart of average batting run rate (runs per over) for each team.
    Args:
        ipl (DataFrame): Ball-by-ball IPL data
        seasons (list, optional): List of seasons to filter by
    Returns:
        go.Figure: Plotly line chart of run rate by team
    """
    filtered_ipl_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    team_runrate_df = filtered_ipl_df.groupby('batting_team').agg(
        total_runs=('total_runs', 'sum'),
        total_balls=('ball', 'count')
    ).reset_index()
    team_runrate_df['overs'] = team_runrate_df['total_balls'] / 6
    team_runrate_df['run_rate'] = team_runrate_df['total_runs'] / team_runrate_df['overs']
    team_runrate_df = team_runrate_df.round({'overs': 2, 'run_rate': 2})
    
    line_trace = go.Scatter(
        x=team_runrate_df['batting_team'],
        y=team_runrate_df['run_rate'],
        mode='lines+markers',
        line=dict(shape='spline', width=3, color='deepskyblue'),
        marker=dict(size=10, color='deepskyblue', line=dict(width=2, color='white')),
        hovertemplate='Team: %{x}<br>Run Rate: %{y:.2f}<extra></extra>'
        )
    fig = go.Figure([line_trace])
    fig.update_layout(title='Batting Run Rate by Team')
    return update_layout(fig)

def get_batting_average_by_team(ipl, seasons=None):
    """
    Generate a line chart of average runs scored per match for each team.
    Args:
        ipl (DataFrame): Ball-by-ball IPL data
        seasons (list, optional): List of seasons to filter by
    Returns:
        go.Figure: Plotly line chart of batting average by team
    """
    filtered_ipl_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    # Aggregate total runs and number of matches played by each team
    team_avg_df = filtered_ipl_df.groupby('batting_team').agg(
        total_runs=('total_runs', 'sum')
    )
    team_avg_df['num_matches'] = filtered_ipl_df.groupby('batting_team')['match_id'].nunique()
    team_avg_df['average_runs'] = team_avg_df['total_runs'] / team_avg_df['num_matches']
    team_avg_df = team_avg_df.round({'average_runs': 2}).reset_index()
    # Create line chart
    
    line_trace = go.Scatter(
            x=team_avg_df['batting_team'],
            y=team_avg_df['average_runs'],
            mode='lines+markers',
            line=dict(shape='spline', width=3, color='deepskyblue'),
            marker=dict(size=10, color='deepskyblue', line=dict(width=2, color='white')),
            hovertemplate='Team: %{x}<br>Avg Runs: %{y:.2f}<extra></extra>'
        )
    fig = go.Figure([line_trace])
    fig.update_layout(title='Batting Average by Team')
    return update_layout(fig)

def get_highest_run_chase(matches, seasons=None):
    """
    Get the highest successful run chase (target runs) in IPL matches, optionally filtered by season.
    Args:
        matches (DataFrame): Match-level IPL data
        seasons (list, optional): List of seasons to filter by
    Returns:
        int: Highest run chase value
    """
    filtered_matches_df = matches[matches['season'].isin(seasons)].copy() if seasons else matches.copy()
    chasing_wins_df = filtered_matches_df[filtered_matches_df['result'] == 'wickets']
    highest_chase_row = chasing_wins_df.sort_values(by='target_runs', ascending=False).iloc[0]
    return int(highest_chase_row['target_runs'])

def get_lowest_total(ipl, seasons=None):
    """
    Get the lowest total runs scored in a completed 20-over innings, optionally filtered by season.
    Args:
        ipl (DataFrame): Ball-by-ball IPL data
        seasons (list, optional): List of seasons to filter by
    Returns:
        int: Lowest total runs in a completed 20-over innings
    """
    filtered_ipl_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    completed_df = filtered_ipl_df.dropna(subset=['winner'])  # Only consider completed 20-over innings (both innings)
    completed_20_df = completed_df[(completed_df['target_overs'] == 20) & (completed_df['inning'].isin([1, 2]))]
    lowest_total_df = completed_20_df.groupby(['match_id', 'batting_team'])['total_runs'].sum().reset_index(name='lowest_total')
    return int(lowest_total_df.sort_values(by='lowest_total').iloc[0]['lowest_total'])

def get_batting_strike_rate_by_team(ipl, seasons=None):
    """
    Generate a line chart of batting strike rate (runs per 100 balls) for each team.
    Args:
        ipl (DataFrame): Ball-by-ball IPL data
        seasons (list, optional): List of seasons to filter by
    Returns:
        go.Figure: Plotly line chart of batting strike rate by team
    """
    filtered_ipl_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    # Filter legal deliveries (exclude wides and no-balls)
    legal_deliveries_df = filtered_ipl_df[~filtered_ipl_df['extras_type'].isin(['wides', 'noballs'])]
    # Aggregate total runs and balls faced per team
    team_runs = legal_deliveries_df.groupby('batting_team')['batsman_runs'].sum()
    balls_faced = legal_deliveries_df.groupby('batting_team').size()
    strike_rate_df = pd.concat([team_runs, balls_faced], axis=1)
    strike_rate_df.columns = ['total_runs', 'balls_faced']
    strike_rate_df['strike_rate'] = (strike_rate_df['total_runs'] / strike_rate_df['balls_faced']) * 100
    # Create line chart trace
    line_trace = go.Scatter(
        x=strike_rate_df.index,
        y=strike_rate_df['strike_rate'],
        mode='lines+markers',
        line=dict(shape='spline', width=3, color='deepskyblue'),
        marker=dict(size=10, color='deepskyblue', line=dict(width=2, color='white')),
        hovertemplate='Team: %{x}<br>Strike Rate: %{y:.2f}<extra></extra>'
    )
    fig = go.Figure([line_trace])
    fig.update_layout(title='Batting Strike Rate by Team')
    return update_layout(fig)

def get_best_bowling_figures(ipl, seasons=None, player=None):
    """
    Get the best bowling figures (most wickets, least runs) in a match, optionally filtered by season and/or player.
    Args:
        ipl (DataFrame): Ball-by-ball IPL data
        seasons (list, optional): List of seasons to filter by
        player (str, optional): Player name to get best figures for
    Returns:
        str: Best bowling figures in format 'Bowler (wickets/runs)'
    """
    filtered_ipl_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    # Only valid dismissals for wickets
    valid_dismissals = [
        'bowled', 'caught', 'lbw', 'stumped', 'caught and bowled', 'hit wicket'
    ]
    wickets_df = filtered_ipl_df[filtered_ipl_df['dismissal_kind'].isin(valid_dismissals)].copy()
    # If player is specified, filter for that bowler
    if player:
        filtered_ipl_df = filtered_ipl_df[filtered_ipl_df['bowler'] == player]
        wickets_df = wickets_df[wickets_df['bowler'] == player]
    # Group runs and wickets by match and bowler
    runs_per_bowler_match = filtered_ipl_df.groupby(['match_id', 'bowler'])['total_runs'].sum().reset_index()
    wickets_per_bowler_match = wickets_df.groupby(['match_id', 'bowler'])['is_wicket'].sum().reset_index()
    # Merge runs and wickets
    figures_df = pd.merge(runs_per_bowler_match, wickets_per_bowler_match, on=['match_id', 'bowler'], how='left')
    figures_df['is_wicket'] = figures_df['is_wicket'].fillna(0)
    figures_df.rename(columns={'is_wicket': 'total_wickets'}, inplace=True)
    # Sort by wickets (desc), then runs (asc)
    figures_df = figures_df.sort_values(by=['total_wickets', 'total_runs'], ascending=[False, True])
    if not figures_df.empty:
        top_row = figures_df.iloc[0]
        bowler_name = top_row['bowler']
        wickets = int(top_row['total_wickets'])
        runs = int(top_row['total_runs'])
        return f"{bowler_name} ({wickets}/{runs})"
    return "-"

def get_most_expensive_overs(ipl, n, seasons=None):
    """
    Generate a horizontal bar chart of the most expensive overs (most runs conceded) in IPL.
    Args:
        ipl (DataFrame): Ball-by-ball IPL data
        n (int): Number of top expensive overs to show
        seasons (list, optional): List of seasons to filter by
    Returns:
        go.Figure: Bar chart of most expensive overs
    """
    filtered_ipl_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    # Group by match, innings, bowler, and over
    over_stats_df = filtered_ipl_df.groupby(['match_id', 'inning', 'bowler', 'over']).agg(
        runs_conceded=('total_runs', 'sum')
    ).reset_index()
    # Sort by most runs in a single over
    top_expensive_overs_df = over_stats_df.sort_values(by='runs_conceded', ascending=False).head(n)[::-1]
    
    bar_trace = go.Bar(
            x=top_expensive_overs_df['runs_conceded'],
            y=top_expensive_overs_df['bowler'],
            orientation='h',
            hovertemplate='Bowler: %{y}<br>Over: %{customdata[0]}<br>Runs: %{x}<extra></extra>',
            customdata=top_expensive_overs_df[['over']].values
        )
    fig = go.Figure([bar_trace])
    fig.update_layout(title=dict(text='Most Runs Conceded in a Single Over'))
    return update_layout(fig)

def get_dismissal_kind(ipl, seasons=None):
    """
    Generate a pie chart of dismissal kinds (bowled, caught, etc.) in IPL.
    Args:
        ipl (DataFrame): Ball-by-ball IPL data
        seasons (list, optional): List of seasons to filter by
    Returns:
        go.Figure: Pie chart of dismissal kinds
    """
    filtered_ipl_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    labels = ['Bowled', 'Caught', 'LBW', 'Stumped', 'Caught and Bowled', 'Hit Wicket']
    valid_dismissals = [
        'bowled', 'caught', 'lbw', 'stumped', 'caught and bowled', 'hit wicket'
    ]
    dismissals_df = filtered_ipl_df[filtered_ipl_df['dismissal_kind'].isin(valid_dismissals)]
    dismissals_count_df = dismissals_df.groupby(['dismissal_kind']).size().reset_index(name='count')
    
    pie_trace = go.Pie(
            labels=labels,
            values=dismissals_count_df['count'],
            insidetextfont=dict(color='white'),
            hovertemplate='Kind: %{label}<br>Count: %{value}<extra></extra>'
        )
    fig = go.Figure([pie_trace])
    fig.update_layout(legend=dict(title='Dismissal Kind'), title=f'Overall Dismissals Distribution', xaxis=dict(showticklabels=False))
    fig.update_traces(textinfo='label+percent', hoverinfo='label+value+percent', hole=0.3, hoverlabel=dict(font=dict(color='white')))
    return update_layout(fig)


def get_most_number_of_hattricks(ipl, seasons=None):
    """
    Get the bowler with the most hat-tricks, optionally filtered by season.
    Args:
        ipl (DataFrame): Ball-by-ball IPL data
        seasons (list, optional): List of seasons to filter by
    Returns:
        str: Bowler and number of hat-tricks
    """
    filtered_ipl_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    valid_dismissals = [
        'bowled', 'caught', 'lbw', 'stumped', 'caught and bowled', 'hit wicket'
    ]
    # Only legal deliveries (no extras)
    legal_deliveries_df = filtered_ipl_df[filtered_ipl_df['extras_type'].isna()]
    # Mark legal wickets
    legal_deliveries_df = legal_deliveries_df.copy()
    legal_deliveries_df['is_wicket'] = legal_deliveries_df['dismissal_kind'].isin(valid_dismissals).astype(int)
    # Sort by match, bowler, and ball order
    legal_deliveries_df = legal_deliveries_df.sort_values(by=['match_id', 'bowler', 'over', 'ball'])
    # Rolling sum over 3 balls for each bowler per match
    def find_hattricks(df):
        df['hat_sum'] = df['is_wicket'].rolling(window=3).sum()
        return df
    legal_deliveries_df = legal_deliveries_df.groupby(['match_id', 'bowler']).apply(find_hattricks, include_groups=False)
    # Filter rows where rolling sum is 3 => hat-trick detected
    hat_tricks_df = legal_deliveries_df[legal_deliveries_df['hat_sum'] == 3]
    # Count number of hat-tricks per bowler
    hattrick_counts_df = hat_tricks_df.groupby('bowler').size().reset_index(name='hat_tricks')
    # Sort in descending order to get most hat-tricks
    hattrick_counts_df = hattrick_counts_df.sort_values(by='hat_tricks', ascending=False)
    if not hattrick_counts_df.empty:
        top_row = hattrick_counts_df.iloc[0]
        bowler_name = top_row['bowler']
        hat_tricks = top_row['hat_tricks']
        if hat_tricks > 1:
            return f"{bowler_name} ({hat_tricks} Hattricks)"
        return f"{bowler_name} ({hat_tricks} Hattrick)"
    return "-"

def get_bowling_average_by_team(ipl, seasons=None):
    """
    Generate a line chart of bowling average (runs per wicket) for each team.
    Args:
        ipl (DataFrame): Ball-by-ball IPL data
        seasons (list, optional): List of seasons to filter by
    Returns:
        go.Figure: Plotly line chart of bowling average by team
    """
    filtered_ipl_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    # Aggregate total runs conceded and wickets taken by each team
    team_bowl_avg_df = filtered_ipl_df.groupby('bowling_team').agg(
        total_runs=('total_runs', 'sum'),
        total_wickets=('is_wicket', 'sum')
    ).reset_index()
    team_bowl_avg_df['average'] = team_bowl_avg_df['total_runs'] / team_bowl_avg_df['total_wickets']
    # Create line chart trace
    line_trace = go.Scatter(
        x=team_bowl_avg_df['bowling_team'],
        y=team_bowl_avg_df['average'],
        mode='lines+markers',
        line=dict(shape='spline', width=3, color='deepskyblue'),
        marker=dict(size=10, color='deepskyblue', line=dict(width=2, color='white')),
        hovertemplate='Team: %{x}<br>Average: %{y:.2f}<extra></extra>'
    )
    fig = go.Figure([line_trace])
    fig.update_layout(title='Bowling Average by Team')
    return update_layout(fig)

def get_bowling_strike_rate_by_team(ipl, seasons=None):
    """
    Generate a line chart of bowling strike rate (balls per wicket) for each team.
    Args:
        ipl (DataFrame): Ball-by-ball IPL data
        seasons (list, optional): List of seasons to filter by
    Returns:
        go.Figure: Plotly line chart of bowling strike rate by team
    """
    filtered_ipl_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    # Filter legal deliveries (exclude wides and no-balls)
    legal_deliveries_df = filtered_ipl_df[~filtered_ipl_df['extras_type'].isin(['wides', 'noballs'])]
    # Count legal balls bowled per team
    balls_bowled = legal_deliveries_df.groupby('bowling_team').size()
    # Valid dismissals that count for bowlers
    valid_dismissals = ['bowled', 'caught', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
    wickets_df = filtered_ipl_df[filtered_ipl_df['dismissal_kind'].isin(valid_dismissals)]
    wickets_by_team = wickets_df.groupby('bowling_team').size()
    # Combine and compute strike rate
    strike_rate_df = pd.concat([balls_bowled, wickets_by_team], axis=1)
    strike_rate_df.columns = ['total_balls', 'total_wickets']
    strike_rate_df = strike_rate_df.fillna(0)
    strike_rate_df['strike_rate'] = (strike_rate_df['total_balls'] / strike_rate_df['total_wickets']).replace([float('inf'), -float('inf')], 0)
    # Create line chart trace
    line_trace = go.Scatter(
        x=strike_rate_df.index,
        y=strike_rate_df['strike_rate'],
        mode='lines+markers',
        line=dict(shape='spline', width=3, color='deepskyblue'),
        marker=dict(size=10, color='deepskyblue', line=dict(width=2, color='white')),
        hovertemplate='Team: %{x}<br>Strike Rate: %{y:.2f}<extra></extra>'
    )
    fig = go.Figure([line_trace])
    fig.update_layout(title='Bowling Strike Rate by Team')
    return update_layout(fig)

def get_bowling_economy_by_team(ipl, seasons=None):
    """
    Generate a line chart of bowling economy (runs per over) for each team.
    Args:
        ipl (DataFrame): Ball-by-ball IPL data
        seasons (list, optional): List of seasons to filter by
    Returns:
        go.Figure: Plotly line chart of bowling economy by team
    """
    filtered_ipl_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    # Aggregate total runs conceded and balls bowled by each team
    team_economy_df = filtered_ipl_df.groupby('bowling_team').agg(
        total_runs=('total_runs', 'sum'),
        total_balls=('ball', 'size')
    ).reset_index()
    team_economy_df['overs'] = team_economy_df['total_balls'] / 6
    team_economy_df['economy'] = team_economy_df['total_runs'] / team_economy_df['overs']
    # Create line chart trace
    line_trace = go.Scatter(
        x=team_economy_df['bowling_team'],
        y=team_economy_df['economy'],
        mode='lines+markers',
        line=dict(shape='spline', width=3, color='deepskyblue'),
        marker=dict(size=10, color='deepskyblue', line=dict(width=2, color='white')),
        hovertemplate='Team: %{x}<br>Economy: %{y:.2f}<extra></extra>'
    )
    fig = go.Figure([line_trace])
    fig.update_layout(title='Bowling Economy by Team')
    return update_layout(fig)

def get_best_team_economy(ipl, seasons=None):
    """
    Returns a str of best (lowest) team economy.
    Args:
        ipl (DataFrame): Ball-by-ball IPL data
        seasons (list, optional): List of seasons to filter by
    Returns:
        dict: {season: (team, value)}
    """
    filtered_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    grouped = filtered_df.groupby(['season', 'bowling_team']).agg(total_runs=('total_runs', 'sum'), total_balls=('ball', 'size')).reset_index()
    grouped['overs'] = grouped['total_balls'] / 6
    grouped['economy'] = grouped['total_runs'] / grouped['overs']
    idx = grouped['economy'].idxmin()
    best = grouped.loc[idx, ['bowling_team', 'economy']]
    return f"{TEAM_SHORT_NAMES[best[0]]} ({round(float(best[1]), 2)})"

def get_best_team_strike_rate(ipl, seasons=None):
    """
    Returns a str of best (lowest) team strike rate.
    Args:
        ipl (DataFrame): Ball-by-ball IPL data
        seasons (list, optional): List of seasons to filter by
    Returns:
        dict: {season: (team, value)}
    """
    filtered_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    legal_deliveries = filtered_df[~filtered_df['extras_type'].isin(['wides', 'noballs'])]
    balls_bowled = legal_deliveries.groupby(['season', 'bowling_team']).size().rename('total_balls')
    valid_dismissals = ['bowled', 'caught', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
    wickets_df = filtered_df[filtered_df['dismissal_kind'].isin(valid_dismissals)]
    wickets_by_team = wickets_df.groupby(['season', 'bowling_team']).size().rename('total_wickets')
    sr_df = pd.concat([balls_bowled, wickets_by_team], axis=1).fillna(0)
    sr_df['strike_rate'] = (sr_df['total_balls'] / sr_df['total_wickets']).replace([float('inf'), -float('inf')], 0)
    sr_df = sr_df.reset_index()
    idx = sr_df['strike_rate'].idxmin()
    best = sr_df.loc[idx, ['bowling_team', 'strike_rate']]
    return f"{TEAM_SHORT_NAMES[best[0]]} ({round(float(best[1]), 2)})"


def get_best_team_average(ipl, seasons=None):
    """
    Returns a str of best (lowest) team bowling average.
    Args:
        ipl (DataFrame): Ball-by-ball IPL data
        seasons (list, optional): List of seasons to filter by
    Returns:
        dict: {season: (team, value)}
    """
    filtered_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    grouped = filtered_df.groupby('bowling_team').agg(total_runs=('total_runs', 'sum'), total_wickets=('is_wicket', 'sum')).reset_index()
    grouped['average'] = grouped['total_runs'] / grouped['total_wickets']
    idx = grouped['average'].idxmin()
    best = grouped.loc[idx, ['bowling_team', 'average']]
    return f"{TEAM_SHORT_NAMES[best[0]]} ({round(float(best[1]), 2)})"

def get_team_stats(ipl, team_name, seasons=None):
    """
    Calculate and return a DataFrame of key batting and bowling stats for a given team.
    Args:
        ipl (DataFrame): Ball-by-ball IPL data
        team_name (str): Team name to analyze
        seasons (list, optional): List of seasons to filter by
    Returns:
        DataFrame: Stats with columns [Stat, Batting, Bowling]
    """
    # Filter IPL data by selected seasons
    filtered_ipl_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()

    # Total matches played by the team (batting or bowling)
    total_matches = filtered_ipl_df[
        (filtered_ipl_df['batting_team'] == team_name) |
        (filtered_ipl_df['bowling_team'] == team_name)
    ]['match_id'].nunique()

    # Batting stats
    batting_df = filtered_ipl_df[filtered_ipl_df['batting_team'] == team_name]
    batting_total_runs = batting_df['total_runs'].sum()
    batting_matches = batting_df['match_id'].nunique()
    # Batting average: runs per match
    batting_average = round(batting_total_runs / batting_matches, 2) if batting_matches else 0
    wickets_lost = batting_df['is_wicket'].sum()
    # Only legal balls (exclude wides/noballs)
    legal_balls = batting_df[~batting_df['extra_runs'].isin(['wides', 'noballs'])].shape[0]
    total_overs = legal_balls / 6 if legal_balls else 0
    batting_run_rate = round(batting_total_runs / total_overs, 2) if total_overs else 0
    batting_strike_rate = round((batting_total_runs / legal_balls) * 100, 2) if legal_balls else 0

    # Bowling stats
    bowling_df = filtered_ipl_df[filtered_ipl_df['bowling_team'] == team_name]
    bowling_total_runs = bowling_df['total_runs'].sum()
    wickets_taken = bowling_df['is_wicket'].sum()
    legal_balls_bowled = bowling_df[~bowling_df['extra_runs'].isin(['wides', 'noballs'])].shape[0]
    bowling_overs = legal_balls_bowled / 6 if legal_balls_bowled else 0
    bowling_economy = round(bowling_total_runs / bowling_overs, 2) if bowling_overs else 0
    bowling_average = round(bowling_total_runs / wickets_taken, 2) if wickets_taken else 0
    bowling_strike_rate = round(legal_balls_bowled / wickets_taken, 2) if wickets_taken else 0

    # Match results for win/toss stats
    match_results_df = filtered_ipl_df.drop_duplicates(subset='match_id')[['match_id', 'winner', 'toss_winner', 'toss_decision']]
    team_wins = match_results_df[match_results_df['winner'] == team_name].shape[0]
    win_percentage = round((team_wins / total_matches) * 100, 2) if total_matches else 0

    # Toss stats
    toss_wins = match_results_df[match_results_df['toss_winner'] == team_name].shape[0]
    toss_win_percentage = round((toss_wins / total_matches) * 100, 2) if total_matches else 0

    # Batting First & Bowling First Win %
    batted_first_wins = match_results_df[
        (match_results_df['toss_winner'] == team_name) &
        (match_results_df['toss_decision'] == 'bat') &
        (match_results_df['winner'] == team_name)
    ].shape[0]
    bowled_first_wins = match_results_df[
        (match_results_df['toss_winner'] == team_name) &
        (match_results_df['toss_decision'] == 'field') &
        (match_results_df['winner'] == team_name)
    ].shape[0]
    batting_first_win_percentage = round((batted_first_wins / toss_wins) * 100, 2) if toss_wins else 0
    bowling_first_win_percentage = round((bowled_first_wins / toss_wins) * 100, 2) if toss_wins else 0

    # Assemble stats into DataFrame
    stats = [
        ["Total Matches", total_matches, total_matches],
        ["Win %", win_percentage, win_percentage],
        ["Toss Win %", toss_win_percentage, toss_win_percentage],
        ["Batting First Win %", batting_first_win_percentage, None],
        ["Bowling First Win %", None, bowling_first_win_percentage],
        ["Wickets Lost", wickets_lost, None],
        ["Total Runs", batting_total_runs, None],
        ["Batting Average", batting_average, None],
        ["Run Rate", batting_run_rate, None],
        ["Strike Rate", batting_strike_rate, None],
        ["Wickets Taken", None, wickets_taken],
        ["Bowling Average", None, bowling_average],
        ["Bowling Economy", None, bowling_economy],
        ["Bowling Strike Rate", None, bowling_strike_rate]
    ]
    stats_df = pd.DataFrame(stats, columns=["Stat", "Batting", "Bowling"])
    return stats_df

def get_teams_stats_figs(ipl, team1, team2, seasons=None):
    """
    Generate three DataFrames for team comparison:
    1. Basic stats (Total Matches, Win %, Toss Win %)
    2. Batting stats (Wickets Lost, Total Runs, Batting Average, Run Rate, Strike Rate, Batting First Win %)
    3. Bowling stats (Wickets Taken, Bowling Average, Bowling Economy, Bowling Strike Rate, Bowling First Win %)
    Args:
        ipl (DataFrame): Ball-by-ball data
        team1 (str): First team name
        team2 (str): Second team name
        seasons (list, optional): Filter by seasons
    Returns:
        tuple: (basic_stats_df, batting_stats_df, bowling_stats_df)
    """
    """
    Generate normalized bar charts for team comparison: basic, batting, and bowling stats.
    Args:
        ipl (DataFrame): Ball-by-ball IPL data
        team1 (str): First team name
        team2 (str): Second team name
        seasons (list, optional): List of seasons to filter by
    Returns:
        tuple: (basic_stats_fig, batting_stats_fig, bowling_stats_fig)
    """
    # Get stats DataFrames for both teams
    team1_stats_df = get_team_stats(ipl, team1, seasons)
    team2_stats_df = get_team_stats(ipl, team2, seasons)

    # Select basic stats
    basic_stats_list = ["Total Matches", "Win %", "Toss Win %"]
    basic_stats_df = pd.DataFrame({
        team1: team1_stats_df[team1_stats_df["Stat"].isin(basic_stats_list)][["Batting"]].values.flatten(),
        team2: team2_stats_df[team2_stats_df["Stat"].isin(basic_stats_list)][["Batting"]].values.flatten()
    }, index=basic_stats_list)

    # Select batting stats
    batting_stats_list = [
        "Batting First Win %", "Wickets Lost", "Total Runs", "Batting Average", "Run Rate", "Strike Rate"
    ]
    batting_stats_df = pd.DataFrame({
        team1: team1_stats_df[team1_stats_df["Stat"].isin(batting_stats_list)][["Batting"]].values.flatten(),
        team2: team2_stats_df[team2_stats_df["Stat"].isin(batting_stats_list)][["Batting"]].values.flatten()
    }, index=batting_stats_list)

    # Select bowling stats
    bowling_stats_list = [
        "Bowling First Win %", "Wickets Taken", "Bowling Average", "Bowling Economy", "Bowling Strike Rate"
    ]
    bowling_stats_df = pd.DataFrame({
        team1: team1_stats_df[team1_stats_df["Stat"].isin(bowling_stats_list)][["Bowling"]].values.flatten(),
        team2: team2_stats_df[team2_stats_df["Stat"].isin(bowling_stats_list)][["Bowling"]].values.flatten()
    }, index=bowling_stats_list)

    # Helper function to normalize bar heights for each stat
    def get_normalized_bar(stat_names, stat_values, color, team_name):
        norm_values = []
        for idx, value in enumerate(stat_values):
            stat = stat_names[idx]
            # Get both teams' values for this stat
            values = [
                basic_stats_df.loc[stat, team1] if stat in basic_stats_df.index else None,
                basic_stats_df.loc[stat, team2] if stat in basic_stats_df.index else None,
                batting_stats_df.loc[stat, team1] if stat in batting_stats_df.index else None,
                batting_stats_df.loc[stat, team2] if stat in batting_stats_df.index else None,
                bowling_stats_df.loc[stat, team1] if stat in bowling_stats_df.index else None,
                bowling_stats_df.loc[stat, team2] if stat in bowling_stats_df.index else None
            ]
            # Filter out None values
            values = [v for v in values if v is not None]
            max_value = max([abs(v) for v in values] + [1])
            norm_values.append(value / max_value)
        # Create bar trace
        return go.Bar(
            x=stat_names,
            y=norm_values,
            marker_color=color,
            name=team_name,
            hovertemplate='%{x}: %{customdata:.2f}<extra></extra>',
            customdata=stat_values,  # Original values in tooltip
        )

    # Basic stats figure
    basic_fig = go.Figure()
    basic_fig.add_trace(get_normalized_bar(basic_stats_df.index, basic_stats_df[team1].values, TEAM_COLORS[team1], team1))
    basic_fig.add_trace(get_normalized_bar(basic_stats_df.index, basic_stats_df[team2].values, TEAM_COLORS[team2], team2))
    basic_fig.update_layout(title="Basic Stats (Normalized)", showlegend=False)

    # Batting stats figure
    batting_fig = go.Figure()
    batting_fig.add_trace(get_normalized_bar(batting_stats_df.index, batting_stats_df[team1].values, TEAM_COLORS[team1], team1))
    batting_fig.add_trace(get_normalized_bar(batting_stats_df.index, batting_stats_df[team2].values, TEAM_COLORS[team2], team2))
    batting_fig.update_layout(title="Batting Stats (Normalized)", showlegend=False)

    # Bowling stats figure
    bowling_fig = go.Figure()
    bowling_fig.add_trace(get_normalized_bar(bowling_stats_df.index, bowling_stats_df[team1].values, TEAM_COLORS[team1], team1))
    bowling_fig.add_trace(get_normalized_bar(bowling_stats_df.index, bowling_stats_df[team2].values, TEAM_COLORS[team2], team2))
    bowling_fig.update_layout(title="Bowling Stats (Normalized)", showlegend=False)

    return update_layout(basic_fig), update_layout(batting_fig), update_layout(bowling_fig)

def get_team_wins_fig(matches, team1, team2):
    """
    Generate a line chart of total wins per season for two teams.
    Args:
        matches (DataFrame): Match-level IPL data
        team1 (str): First team name
        team2 (str): Second team name
    Returns:
        go.Figure: Plotly line chart of team wins per season
    """
    # Filter matches where either team is the winner
    filtered_matches_df = matches[matches['winner'].isin([team1, team2])]
    # Group by season and winner, count wins
    team_wins_df = filtered_matches_df.groupby(['season', 'winner']).size().reset_index(name='Wins')
    # Pivot to get seasons as index, teams as columns
    team_wins_pivot_df = team_wins_df.pivot_table(index='season', columns='winner', values='Wins', fill_value=0)

    # Create line chart for each team
    fig = go.Figure()
    for team in [team1, team2]:
        trace = go.Scatter(
            x=team_wins_pivot_df.index.tolist(),
            y=team_wins_pivot_df[team],
            name=team,
            mode='lines+markers',
            line=dict(shape='spline', width=3, color=TEAM_COLORS[team]),
            marker=dict(size=10, color=TEAM_COLORS[team], line=dict(width=2, color='white')),
            hovertemplate='Wins: %{y}<extra></extra>'
        )
        fig.add_trace(trace)
    fig.update_layout(title='Total Wins in each Season', showlegend=False, hovermode='x unified')
    # Add season tick labels for x-axis
    add_tick_labels(fig)
    return update_layout(fig)

def get_head_to_head_win_stats(matches, team1, team2, seasons=None):
    """
    Generate a pie chart of head-to-head win stats for two teams.
    Args:
        matches (DataFrame): Match-level IPL data
        team1 (str): First team name
        team2 (str): Second team name
        seasons (list, optional): List of seasons to filter by
    Returns:
        go.Figure: Plotly pie chart of head-to-head wins
    """
    # Filter matches by selected seasons
    filtered_matches_df = matches[matches['season'].isin(seasons)].copy() if seasons else matches.copy()
    # Only matches where both teams played
    head_to_head_df = filtered_matches_df[(filtered_matches_df['team1'].isin([team1, team2])) & (filtered_matches_df['team2'].isin([team1, team2]))]
    # Group by winner and count wins
    win_stats_df = head_to_head_df.groupby('winner').size().reset_index(name='count')
    # Assign colors for pie chart
    color_map = {team1: TEAM_COLORS[team1], team2: TEAM_COLORS[team2]}
    colors = [color_map.get(team, '#888') for team in win_stats_df['winner']]
    # Create pie chart trace
    trace = go.Pie(
        labels=win_stats_df['winner'],
        values=win_stats_df['count'],
        textinfo='value+percent',
        hoverinfo='label+value+percent',
        hole=0.3,
        hoverlabel=dict(font=dict(color='white')),
        hovertemplate='Team: %{label}<br>Wins: %{value}<extra></extra>',
        marker=dict(colors=colors),
    )
    fig = go.Figure()
    fig.add_trace(trace)
    fig.update_layout(title="Head-to-Head", showlegend=False)
    return update_layout(fig)
    

def get_powerplay_death_batting_stats(ipl, team1, team2):    
    """
    Generate line charts for Powerplay and Death Overs batting performance for two teams.
    Args:
        ipl (DataFrame): Ball-by-ball IPL data
        team1 (str): First team name
        team2 (str): Second team name
    Returns:
        tuple: (powerplay_fig, death_fig)
    """
    # Filter IPL data for selected teams
    filtered_ipl_df = ipl[ipl['batting_team'].isin([team1, team2])]

    # Powerplay overs (0-5)
    powerplay_df = filtered_ipl_df[filtered_ipl_df['over'].isin([0, 1, 2, 3, 4, 5])]
    powerplay_stats_df = powerplay_df.groupby(['season', 'batting_team'])['total_runs'].sum().reset_index(name='total_runs')

    # Death overs (15-19)
    death_df = filtered_ipl_df[filtered_ipl_df['over'].isin([15, 16, 17, 18, 19])]
    death_stats_df = death_df.groupby(['season', 'batting_team'])['total_runs'].sum().reset_index(name='total_runs')

    # Create Powerplay line chart
    powerplay_fig = go.Figure()
    for team in [team1, team2]:
        team_powerplay_df = powerplay_stats_df[powerplay_stats_df['batting_team'] == team]
        trace = go.Scatter(
            x=team_powerplay_df['season'],
            y=team_powerplay_df['total_runs'],
            name=team,
            mode='lines+markers',
            line=dict(shape='spline', width=3, color=TEAM_COLORS[team]),
            marker=dict(size=10, color=TEAM_COLORS[team], line=dict(width=2, color='white')),
            hovertemplate='Total Runs: %{y}<extra></extra>'
        )
        powerplay_fig.add_trace(trace)

    # Create Death Overs line chart
    death_fig = go.Figure()
    for team in [team1, team2]:
        team_death_df = death_stats_df[death_stats_df['batting_team'] == team]
        trace = go.Scatter(
            x=team_death_df['season'],
            y=team_death_df['total_runs'],
            name=team,
            mode='lines+markers',
            line=dict(shape='spline', width=3, color=TEAM_COLORS[team]),
            marker=dict(size=10, color=TEAM_COLORS[team], line=dict(width=2, color='white')),
            hovertemplate='Total Runs: %{y}<extra></extra>'
        )
        death_fig.add_trace(trace)

    # Add season tick labels and update layout
    add_tick_labels(powerplay_fig)
    add_tick_labels(death_fig)
    powerplay_fig.update_layout(title='Powerplay Overs Batting Performance', showlegend=False, xaxis_tickangle=45, hovermode='x unified')
    death_fig.update_layout(title='Death Overs Batting Performance', showlegend=False, xaxis_tickangle=45, hovermode='x unified')
    return update_layout(powerplay_fig), update_layout(death_fig)

def get_powerplay_death_bowling_stats(ipl, team1, team2):
    """
    Generate line charts for Powerplay and Death Overs bowling performance for two teams.
    Args:
        ipl (DataFrame): Ball-by-ball IPL data
        team1 (str): First team name
        team2 (str): Second team name
    Returns:
        tuple: (powerplay_fig, death_fig)
    """
    # Filter IPL data for selected teams
    filtered_ipl_df = ipl[ipl['bowling_team'].isin([team1, team2])]

    # Powerplay overs (0-5)
    powerplay_df = filtered_ipl_df[filtered_ipl_df['over'].isin([0, 1, 2, 3, 4, 5])]
    powerplay_stats_df = powerplay_df.groupby(['season', 'bowling_team'])['is_wicket'].sum().reset_index(name='total_wickets')

    # Death overs (15-19)
    death_df = filtered_ipl_df[filtered_ipl_df['over'].isin([15, 16, 17, 18, 19])]
    death_stats_df = death_df.groupby(['season', 'bowling_team'])['is_wicket'].sum().reset_index(name='total_wickets')

    # Create Powerplay line chart
    powerplay_fig = go.Figure()
    for team in [team1, team2]:
        team_powerplay_df = powerplay_stats_df[powerplay_stats_df['bowling_team'] == team]
        trace = go.Scatter(
            x=team_powerplay_df['season'],
            y=team_powerplay_df['total_wickets'],
            name=team,
            mode='lines+markers',
            line=dict(shape='spline', width=3, color=TEAM_COLORS[team]),
            marker=dict(size=10, color=TEAM_COLORS[team], line=dict(width=2, color='white')),
            hovertemplate='Total Wickets: %{y}<extra></extra>'
        )
        powerplay_fig.add_trace(trace)

    # Create Death Overs line chart
    death_fig = go.Figure()
    for team in [team1, team2]:
        team_death_df = death_stats_df[death_stats_df['bowling_team'] == team]
        trace = go.Scatter(
            x=team_death_df['season'],
            y=team_death_df['total_wickets'],
            name=team,
            mode='lines+markers',
            line=dict(shape='spline', width=3, color=TEAM_COLORS[team]),
            marker=dict(size=10, color=TEAM_COLORS[team], line=dict(width=2, color='white')),
            hovertemplate='Total Wickets: %{y}<extra></extra>'
        )
        death_fig.add_trace(trace)

    # Add season tick labels and update layout
    add_tick_labels(powerplay_fig)
    add_tick_labels(death_fig)
    powerplay_fig.update_layout(title='Powerplay Overs Bowling Performance', showlegend=False, xaxis_tickangle=45, hovermode='x unified')
    death_fig.update_layout(title='Death Overs Bowling Performance', showlegend=False, xaxis_tickangle=45, hovermode='x unified')
    return update_layout(powerplay_fig), update_layout(death_fig)
    
def get_top_scorer_top_bowler_stats(ipl, team1, team2, seasons=None):
    """
    Returns a grouped bar chart of top scorer and top wicket-taker for each team in head-to-head matches.
    Args:
        ipl (DataFrame): Ball-by-ball data
        team1 (str): First team name
        team2 (str): Second team name
        seasons (list, optional): Filter by seasons
    Returns:
        go.Figure: Grouped bar chart
    """
    """
    Generate a grouped bar chart of top scorer and top wicket-taker for each team in head-to-head matches.
    Args:
        ipl (DataFrame): Ball-by-ball IPL data
        team1 (str): First team name
        team2 (str): Second team name
        seasons (list, optional): List of seasons to filter by
    Returns:
        go.Figure: Plotly grouped bar chart
    """
    # Filter IPL data for head-to-head matches and selected seasons
    filtered_ipl_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    filtered_ipl_df = filtered_ipl_df[
        (filtered_ipl_df['batting_team'].isin([team1, team2])) |
        (filtered_ipl_df['bowling_team'].isin([team1, team2]))
    ]

    # Top scorer per team
    scorer_stats_df = (
        filtered_ipl_df.groupby(['batting_team', 'batter'])['batsman_runs']
        .sum()
        .reset_index()
    )
    top_scorers_df = scorer_stats_df.loc[
        scorer_stats_df.groupby('batting_team')['batsman_runs'].idxmax()
    ]
    top_scorers_df['type'] = 'Top Scorer'
    top_scorers_df.rename(columns={'batting_team': 'team', 'batter': 'Player', 'batsman_runs': 'Value'}, inplace=True)

    # Top wicket-taker per team
    valid_dismissals = [
        'bowled', 'caught', 'lbw', 'stumped', 'caught and bowled', 'hit wicket'
    ]
    wickets_df = filtered_ipl_df[filtered_ipl_df['dismissal_kind'].isin(valid_dismissals)]
    bowler_stats_df = (
        wickets_df.groupby(['bowling_team', 'bowler'])['is_wicket']
        .sum()
        .reset_index()
    )
    top_bowlers_df = bowler_stats_df.loc[
        bowler_stats_df.groupby('bowling_team')['is_wicket'].idxmax()
    ]
    top_bowlers_df['type'] = 'Top Wicket Taker'
    top_bowlers_df.rename(columns={'bowling_team': 'team', 'bowler': 'Player', 'is_wicket': 'Value'}, inplace=True)

    # Combine top scorers and bowlers for grouped bar chart
    combined_df = pd.concat([top_scorers_df, top_bowlers_df], ignore_index=True)
    combined_df = combined_df[combined_df['team'].isin([team1, team2])]

    # Create grouped bar chart
    fig = go.Figure()
    for team in [team1, team2]:
        team_data_df = combined_df[combined_df['team'] == team]
        trace = go.Bar(
            x=team_data_df['type'],
            y=team_data_df['Value'],
            marker_color=TEAM_COLORS[team],
            customdata=team_data_df['Player'],
            hovertemplate="%{customdata}: %{y}<extra></extra>",
            name=team
        )
        fig.add_trace(trace)
    fig.update_layout(
        title='Top Scorer and Top Wicket Taker per Team',
        barmode='group',
        showlegend=False
    )
    return update_layout(fig)

def get_boundary_count(ipl, team1, team2, seasons=None):
    """
    Generate a bar chart of total boundaries (4s and 6s) per team in head-to-head matches.
    Args:
        ipl (DataFrame): Ball-by-ball IPL data
        team1 (str): First team name
        team2 (str): Second team name
        seasons (list, optional): List of seasons to filter by
    Returns:
        go.Figure: Plotly bar chart of boundaries per team
    """
    # Filter IPL data for selected seasons and teams
    filtered_ipl_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    filtered_ipl_df = filtered_ipl_df[filtered_ipl_df['batting_team'].isin([team1, team2])]

    # Only 4s and 6s
    boundaries_df = filtered_ipl_df[filtered_ipl_df['total_runs'].isin([4, 6])]
    # Group by team and run type, count boundaries
    boundaries_stats_df = boundaries_df.groupby(['batting_team', 'total_runs']).size().reset_index(name='total_boundaries')

    # Create bar chart
    fig = go.Figure()
    for team in [team1, team2]:
        team_data_df = boundaries_stats_df[boundaries_stats_df['batting_team'] == team]
        trace = go.Bar(
            x=["4's", "6's"],
            y=team_data_df['total_boundaries'],
            marker_color=TEAM_COLORS[team],
            hovertemplate="%{x}: %{y}<extra></extra>"
        )
        fig.add_trace(trace)

    fig.update_layout(title="Total Boundaries per Team", showlegend=False)
    return update_layout(fig)

def get_dismissal_type_distribution(ipl, team1, team2, seasons=None):
    """
    Generate pie charts for dismissal type distribution (wickets taken and lost) for two teams.
    Args:
        ipl (DataFrame): Ball-by-ball IPL data
        team1 (str): First team name
        team2 (str): Second team name
        seasons (list, optional): List of seasons to filter by
    Returns:
        tuple: (wickets_taken_fig, wickets_lost_fig)
    """
    # Filter IPL data for selected seasons
    filtered_ipl_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()

    # Only valid dismissal kinds
    valid_dismissals = [
        'bowled', 'caught', 'lbw', 'stumped', 'caught and bowled', 'hit wicket'
    ]
    filtered_ipl_df = filtered_ipl_df[filtered_ipl_df['dismissal_kind'].isin(valid_dismissals)]

    # Wickets taken by each team
    wickets_taken_df = filtered_ipl_df[filtered_ipl_df['bowling_team'].isin([team1, team2])]
    wickets_taken_stats_df = wickets_taken_df.groupby(['bowling_team', 'dismissal_kind'])['is_wicket'].size().reset_index(name='count')

    # Wickets lost by each team
    wickets_lost_df = filtered_ipl_df[filtered_ipl_df['batting_team'].isin([team1, team2])]
    wickets_lost_stats_df = wickets_lost_df.groupby(['batting_team', 'dismissal_kind'])['is_wicket'].size().reset_index(name='count')

    # Pie chart: Wickets Taken by Team (lighter shades)
    wickets_taken_fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]])
    for i, team in enumerate([team1, team2]):
        team_data_df = wickets_taken_stats_df[wickets_taken_stats_df['bowling_team'] == team]
        base_color = TEAM_COLORS.get(team, '#888')
        colors = get_lighter_shades(base_color, len(team_data_df)) if base_color.startswith('#') and len(base_color) == 7 else [base_color] * len(team_data_df)
        trace = go.Pie(
            labels=team_data_df['dismissal_kind'],
            values=team_data_df['count'],
            textinfo='percent+value',
            insidetextorientation='horizontal',
            showlegend=False,
            marker=dict(colors=colors),
            insidetextfont=dict(color='white'),
            hole=0.3,
            hovertemplate='Type: %{label}<br>Count: %{value}<extra></extra>',
        )
        wickets_taken_fig.add_trace(trace, row=1, col=i+1)
    wickets_taken_fig.update_layout(title_text='Dismissal Type Distribution - Wickets Taken')

    # Pie chart: Wickets Lost by Team (lighter shades)
    wickets_lost_fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]])
    for i, team in enumerate([team1, team2]):
        team_data_df = wickets_lost_stats_df[wickets_lost_stats_df['batting_team'] == team]
        base_color = TEAM_COLORS.get(team, '#888')
        colors = get_lighter_shades(base_color, len(team_data_df)) if base_color.startswith('#') and len(base_color) == 7 else [base_color] * len(team_data_df)
        trace = go.Pie(
            labels=team_data_df['dismissal_kind'],
            values=team_data_df['count'],
            textinfo='percent+value',
            insidetextorientation='horizontal',
            showlegend=False,
            marker=dict(colors=colors),
            insidetextfont=dict(color='white'),
            hole=0.3,
            hovertemplate='Type: %{label}<br>Count: %{value}<extra></extra>',
        )
        wickets_lost_fig.add_trace(trace, row=1, col=i+1)
    wickets_lost_fig.update_layout(title_text='Dismissal Type Distribution - Wickets Lost')

    return update_layout(wickets_taken_fig), update_layout(wickets_lost_fig)

def get_batting_strike_rate(ipl, team1, team2):
    """
    Generate a line chart of batting strike rate (runs per 100 balls) for two teams, season-wise.
    Args:
        ipl (DataFrame): Ball-by-ball IPL data
        team1 (str): First team name
        team2 (str): Second team name
    Returns:
        go.Figure: Plotly line chart of batting strike rate
    """
    # Filter IPL data for selected teams
    filtered_ipl_df = ipl[ipl['batting_team'].isin([team1, team2])].copy()
    # Filter legal deliveries (exclude wides and no-balls)
    legal_deliveries_df = filtered_ipl_df[~filtered_ipl_df['extras_type'].isin(['wides', 'noballs'])]
    # Aggregate total runs and balls faced per team per season
    team_runs = legal_deliveries_df.groupby(['season', 'batting_team'])['batsman_runs'].sum()
    balls_faced = legal_deliveries_df.groupby(['season', 'batting_team']).size()
    strike_rate_df = pd.concat([team_runs, balls_faced], axis=1)
    strike_rate_df.columns = ['total_runs', 'balls_faced']
    strike_rate_df = strike_rate_df.reset_index()
    strike_rate_df['strike_rate'] = (strike_rate_df['total_runs'] / strike_rate_df['balls_faced']) * 100

    # Create line chart
    fig = go.Figure()
    for team in [team1, team2]:
        team_season_df = strike_rate_df[strike_rate_df['batting_team'] == team]
        trace = go.Scatter(
            x=team_season_df['season'],
            y=team_season_df['strike_rate'],
            mode='lines+markers',
            line=dict(shape='spline', width=3, color=TEAM_COLORS[team]),
            marker=dict(size=10, color=TEAM_COLORS[team], line=dict(width=2, color='white')),
            hovertemplate='Strike Rate: %{y:.2f}<extra></extra>'
        )
        fig.add_trace(trace)
    fig.update_layout(title='Batting Strike Rate', hovermode='x unified', showlegend=False)
    add_tick_labels(fig)
    return update_layout(fig)

def get_bowling_economy(ipl, team1, team2):
    """
    Generate a line chart of bowling economy (runs per over) for two teams, season-wise.
    Args:
        ipl (DataFrame): Ball-by-ball IPL data
        team1 (str): First team name
        team2 (str): Second team name
    Returns:
        go.Figure: Plotly line chart of bowling economy
    """
    # Filter IPL data for selected teams
    filtered_ipl_df = ipl[ipl['bowling_team'].isin([team1, team2])].copy()
    # Aggregate total runs and balls bowled per team per season
    bowling_economy_df = filtered_ipl_df.groupby(['season', 'bowling_team']).agg(
        total_runs=('total_runs', 'sum'),
        total_balls=('ball', 'size')
    ).reset_index()
    bowling_economy_df['overs'] = bowling_economy_df['total_balls'] / 6
    bowling_economy_df['economy'] = bowling_economy_df['total_runs'] / bowling_economy_df['overs']

    # Create line chart
    fig = go.Figure()
    for team in [team1, team2]:
        team_season_df = bowling_economy_df[bowling_economy_df['bowling_team'] == team]
        trace = go.Scatter(
            x=team_season_df['season'],
            y=team_season_df['economy'],
            mode='lines+markers',
            line=dict(shape='spline', width=3, color=TEAM_COLORS[team]),
            marker=dict(size=10, color=TEAM_COLORS[team], line=dict(width=2, color='white')),
            hovertemplate='Economy: %{y:.2f}<extra></extra>'
        )
        fig.add_trace(trace)
    fig.update_layout(title='Bowling Economy', hovermode='x unified', showlegend=False)
    add_tick_labels(fig)
    return update_layout(fig)

def get_batsman_stats(ipl, player, seasons=None):
    filtered_ipl_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    
    batting_stats_df = filtered_ipl_df[filtered_ipl_df['batter'] == player]
    
    mask = (
        (filtered_ipl_df['batter'] == player) |
        (filtered_ipl_df['bowler'] == player) |
        (filtered_ipl_df['fielder'] == player)
    )
    total_matches = filtered_ipl_df.loc[mask, 'match_id'].nunique()
    total_innings = batting_stats_df[['match_id', 'inning']].drop_duplicates()
    total_innings = len(total_innings)
    total_runs = batting_stats_df['batsman_runs'].sum()
    total_balls = batting_stats_df['ball'].size
    strike_rate = (total_runs / total_balls) * 100 if total_balls > 0 else 0
    dismissals = batting_stats_df['player_dismissed'].notnull().sum()
    average = total_runs / dismissals if dismissals > 0 else total_runs
    
    total_fours = (batting_stats_df['batsman_runs'] == 4).sum()
    total_sixes = (batting_stats_df['batsman_runs'] == 6).sum()
    
    match_runs = batting_stats_df.groupby('match_id')['batsman_runs'].sum()
    fifties = (match_runs.between(50, 99)).sum()
    hundreds = (match_runs >= 100).sum()

    best_score = match_runs.max() if not match_runs.empty else 0
    
    dismissal_type_often = batting_stats_df.groupby('dismissal_kind').size().idxmax()
    potm = batting_stats_df[batting_stats_df['player_of_match'] == player]
    potm = potm['match_id'].nunique()
    
    return {
        'total_matches': total_matches,
        'total_innings': total_innings,
        'total_runs': total_runs,
        'batting_strike_rate': strike_rate,
        'dismissals': dismissals,
        'batting_average': average,
        'total_fours': total_fours,
        'total_sixes': total_sixes,
        'fifties': fifties,
        'hundreds': hundreds,
        'best_score': best_score,
        'dismissal_type_often': dismissal_type_often,
        'player_of_the_match': potm
    }

def get_bowler_stats(ipl, player, seasons=None):

    filtered_ipl_df = ipl[ipl['season'].isin(seasons)].copy() if seasons else ipl.copy()
    bowling_stats_df = filtered_ipl_df[filtered_ipl_df['bowler'] == player]

    total_matches = bowling_stats_df['match_id'].nunique()
    total_innings = bowling_stats_df[['match_id', 'inning']].drop_duplicates().shape[0]
    
    valid_dismissals = ['bowled', 'caught', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
    bowling_stats_df = bowling_stats_df[bowling_stats_df['dismissal_kind'].isin(valid_dismissals) | bowling_stats_df['dismissal_kind'].isnull()]
    legal_deliveries_df = bowling_stats_df[~bowling_stats_df['extra_runs'].isin(['wides', 'noballs'])]

    total_wickets = bowling_stats_df['is_wicket'].sum()
    run_conceded = bowling_stats_df['total_runs'].sum()
    balls_bowled = legal_deliveries_df['ball'].size
    total_overs = balls_bowled / 6 if balls_bowled else 0

    average = run_conceded / total_wickets if total_wickets else run_conceded
    economy_rate = run_conceded / total_overs if total_overs else 0
    strike_rate = balls_bowled / total_wickets if total_wickets else 0

    best_bowling_figures = get_best_bowling_figures(ipl, seasons, player)

    match_wickets_df = bowling_stats_df.groupby('match_id')['is_wicket'].sum().reset_index(name='wickets')
    four_wicket_hauls = match_wickets_df[match_wickets_df['wickets'] == 4].shape[0]
    five_wicket_hauls = match_wickets_df[match_wickets_df['wickets'] == 5].shape[0]

    if not bowling_stats_df.empty and 'dismissal_kind' in bowling_stats_df.columns:
        dismissal_type_often = bowling_stats_df.groupby('dismissal_kind').size().idxmax()
    else:
        dismissal_type_often = None

    maiden_overs_df = bowling_stats_df.groupby(['match_id', 'over'])['total_runs'].sum().reset_index(name='total_runs')
    maiden_overs = maiden_overs_df[maiden_overs_df['total_runs'] == 0].shape[0]

    return {
        'total_matches': total_matches,
        'total_innings': total_innings,
        'total_wickets': total_wickets,
        'run_conceded': run_conceded,
        'balls_bowled': balls_bowled,
        'total_overs': total_overs,
        'bowling_average': average,
        'economy_rate': economy_rate,
        'bowling_strike_rate': strike_rate,
        'best_bowling_figures': best_bowling_figures,
        'four_wicket_hauls': four_wicket_hauls,
        'five_wicket_hauls': five_wicket_hauls,
        'dismissal_type_often': dismissal_type_often,
        'maiden_overs': maiden_overs
    }

def get_allrounder_stats(ipl, player, seasons=None):
    batsman_stats = get_batsman_stats(ipl, player, seasons)
    bowler_stats = get_bowler_stats(ipl, player, seasons)
    # Combine both dictionaries under separate keys
    return {
        'batting': batsman_stats,
        'bowling': bowler_stats
    }
    
import os
def get_player_stats(ipl, player, seasons=None):
    if player in BATSMANS:
        stats = get_batsman_stats(ipl, player, seasons)
        stats['batsman'] = player
        df = pd.DataFrame([stats])
        write_header = not os.path.exists('batter_stats.csv')
        df.to_csv('batter_stats.csv', mode='a', header=write_header, index=False)
    elif player in BOWLERS:
        stats = get_bowler_stats(ipl, player, seasons)
        stats['bowler'] = player
        df = pd.DataFrame([stats])
        write_header = not os.path.exists('bowler_stats.csv')
        df.to_csv('bowler_stats.csv', mode='a', header=write_header, index=False)
    else:
        stats = get_allrounder_stats(ipl, player, seasons)
        stats['all_rounder'] = player
        df = pd.DataFrame([stats])
        write_header = not os.path.exists('allrounder_stats.csv')
        df.to_csv('allrounder_stats.csv', mode='a', header=write_header, index=False)
    return stats

def get_batter_runs(ipl, player1, player2=None):
    filtered_ipl_df = ipl[ipl['batter'].isin([player1, player2])] if player2 else ipl[ipl['batter'] == player1]
    player_runs_df = (
        filtered_ipl_df.groupby(['season', 'batter'])['batsman_runs']
        .sum()
        .reset_index()
    )

    fig = go.Figure()
    for player in player_runs_df['batter'].unique():
        player_df = player_runs_df[player_runs_df['batter'] == player]
        played_teams, marker_colors = player_played_team_each_season(filtered_ipl_df, player)
        line_trace = go.Scatter(
            x=player_df['season'],
            y=player_df['batsman_runs'],
            mode='lines+markers',
            hovertemplate="Player: %{text}<br>Played Team: %{customdata}<br>Season: %{x}<br>Runs: %{y}<extra></extra>",
            name=player,
            text=[player]*len(player_df),
            line=dict(shape='spline', width=3, color=player_last_played_team(ipl, player)),
            marker=dict(size=10, color=marker_colors, line=dict(width=2, color='white')),
            customdata=played_teams
        )
        fig.add_trace(line_trace)

    fig.update_layout(
        title='Players Comparison by Runs per season' if player2 else 'Player Runs per season',
        hovermode='x unified', showlegend=False
    )
    add_tick_labels(fig)
    return update_layout(fig)

def get_batter_strike_rate_average(ipl, player1, player2=None):
    filtered_ipl_df = ipl[ipl['batter'].isin([player1, player2])] if player2 else ipl[ipl['batter'] == player1]
    player_average_strike_rate_df = filtered_ipl_df.groupby(['season', 'batter']).agg(
        total_runs=('batsman_runs', 'sum'),
        total_balls=('ball', 'size'),
        total_dismissals=('is_wicket', 'sum')
    ).reset_index()
    player_average_strike_rate_df['strike_rate'] = (player_average_strike_rate_df['total_runs'] / player_average_strike_rate_df['total_balls']) * 100
    player_average_strike_rate_df['average'] = player_average_strike_rate_df.apply(
        lambda row: row['total_runs'] / row['total_dismissals'] if row['total_dismissals'] > 0 else row['total_runs'],
        axis=1
    )
    
    fig = go.Figure()
    fig2 = go.Figure()
    for player in player_average_strike_rate_df['batter'].unique():
        player_df = player_average_strike_rate_df[player_average_strike_rate_df['batter'] == player]
        played_teams, marker_colors = player_played_team_each_season(filtered_ipl_df, player)
        strike_rate_line_trace = go.Scatter(
            x=player_df['season'],
            y=player_df['strike_rate'],
            mode='lines+markers',
            hovertemplate="Player: %{text}<br>Played Team: %{customdata}<br>Season: %{x}<br>Strike_rate: %{y}<extra></extra>",
            name=player,
            text=[player]*len(player_df),
            line=dict(shape='spline', width=3, color=player_last_played_team(ipl, player)),
            marker=dict(size=10, color=marker_colors, line=dict(width=2, color='white')),
            customdata=played_teams
        )
        average_line_trace = go.Scatter(
            x=player_df['season'],
            y=player_df['average'],
            mode='lines+markers',
            hovertemplate="Player: %{text}<br>Played Team: %{customdata}<br>Season: %{x}<br>Average: %{y}<extra></extra>",
            name=player,
            text=[player]*len(player_df),
            line=dict(shape='spline', width=3, color=player_last_played_team(ipl, player)),
            marker=dict(size=10, color=marker_colors, line=dict(width=2, color='white')),
            customdata=played_teams
        )
        fig2.add_trace(average_line_trace)
        fig.add_trace(strike_rate_line_trace)

    fig.update_layout(
        title=f'{player1} and {player2} Comparison by Strike Rate per season' if player2 else f'{player1} Strike Rate per season',
        hovermode='x unified', showlegend=False
    )
    fig2.update_layout(
        title=f'{player1} and {player2} Comparison by Average per season' if player2 else f'{player1} Average per season',
        hovermode='x unified', showlegend=False
    )
    add_tick_labels(fig)
    add_tick_labels(fig2)
    return update_layout(fig), update_layout(fig2)


def get_batter_runs_against_other_teams(ipl, player1, player2, seasons=None):
    filtered_ipl_df = ipl[ipl['batter'].isin([player1, player2])].copy() if player2 else ipl[ipl['batter'] == player1].copy()
    player_runs_df = filtered_ipl_df.groupby(['batter','bowling_team'])['batsman_runs'].sum().reset_index()
    
    fig = go.Figure()
    for player in [player1, player2]:
        player_df = player_runs_df[player_runs_df['batter'] == player]
        if player_df.empty:
            continue
        bar_color = player_last_played_team(ipl, player)
        fig.add_trace(go.Bar(
            x=player_df['bowling_team'],
            y=player_df['batsman_runs'],
            marker_color=bar_color,
            name=player,
            hovertemplate="Bowling Team: %{x}<br>Runs: %{y}<extra></extra>"
        ))
    fig.update_layout(title='Player Runs against other teams', showlegend=False)
    return update_layout(fig)

def get_batter_runs_at_each_venue(ipl, player1, player2, seasons=None):
    if player2:
        filtered_ipl_df = ipl[ipl['batter'].isin([player1, player2])].copy()
        venue_runs = filtered_ipl_df.groupby('venue')['batsman_runs'].sum().reset_index()
    else:
        filtered_ipl_df = ipl[ipl['batter'] == player1].copy()
        venue_runs = filtered_ipl_df.groupby('venue')['batsman_runs'].sum().reset_index()
    
    top_venues = venue_runs.sort_values(by='batsman_runs', ascending=False)['venue'].head(10).tolist()
    player_runs_df = filtered_ipl_df[filtered_ipl_df['venue'].isin(top_venues)].groupby(['batter','venue'])['batsman_runs'].sum().reset_index()

    fig = go.Figure()
    for player in [player1, player2]:
        if not player:
            continue
        player_df = player_runs_df[player_runs_df['batter'] == player]
        if player_df.empty:
            continue
        bar_color = player_last_played_team(ipl, player)
        short_names = player_df['venue'].apply(lambda v: VENUE_MAP.get(v, v.split(',')[0][:18] + ("..." if len(v.split(',')[0]) > 18 else "")))
        fig.add_trace(go.Bar(
            x=short_names,
            y=player_df['batsman_runs'],
            marker_color=bar_color,
            name=player,
            hovertemplate=[f"Venue: {venue}<br>Runs: {runs}<extra></extra>" for venue, runs in zip(player_df['venue'], player_df['batsman_runs'])],
        ))
    fig.update_layout(
        title='Runs by Player at Each Venue (Top 10)', showlegend=False
    )
    return update_layout(fig)


def get_bowler_wickets(ipl, player1, player2=None):
    filtered_ipl_df = ipl[ipl['bowler'].isin([player1, player2])] if player2 else ipl[ipl['bowler'] == player1]
    valid_dismissals = ['bowled', 'caught', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
    filtered_ipl_df = filtered_ipl_df[filtered_ipl_df['dismissal_kind'].isin(valid_dismissals) | filtered_ipl_df['dismissal_kind'].isnull()]
    
    bowler_wickets_df = (
        filtered_ipl_df.groupby(['season', 'bowler'])['is_wicket']
        .sum()
        .reset_index(name='total_wickets')
    )

    fig = go.Figure()
    for player in bowler_wickets_df['bowler'].unique():
        player_df = bowler_wickets_df[bowler_wickets_df['bowler'] == player]
        played_teams, marker_colors = player_played_team_each_season(filtered_ipl_df, player)
        line_trace = go.Scatter(
            x=player_df['season'],
            y=player_df['total_wickets'],
            mode='lines+markers',
            hovertemplate="Player: %{text}<br>Played Team: %{customdata}<br>Season: %{x}<br>Wickets: %{y}<extra></extra>",
            name=player,
            text=[player]*len(player_df),
            line=dict(shape='spline', width=3, color=player_last_played_team(ipl, player)),
            marker=dict(size=10, color=marker_colors, line=dict(width=2, color='white')),
            customdata=played_teams
        )
        fig.add_trace(line_trace)

    fig.update_layout(
        title='Players Comparison by Wickets per season' if player2 else 'Player Wickets per season',
        hovermode='x unified', showlegend=False
    )
    add_tick_labels(fig)
    return update_layout(fig)

def get_bowler_strike_rate_average(ipl, player1, player2=None):
    filtered_ipl_df = ipl[ipl['bowler'].isin([player1, player2])] if player2 else ipl[ipl['bowler'] == player1]
    
    valid_dismissals = ['bowled', 'caught', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
    filtered_ipl_df = filtered_ipl_df[filtered_ipl_df['dismissal_kind'].isin(valid_dismissals) | filtered_ipl_df['dismissal_kind'].isnull()]
    legal_deliveries_df = filtered_ipl_df[~filtered_ipl_df['extra_runs'].isin(['wides', 'noballs'])]
    bowler_average_strike_rate_df = legal_deliveries_df.groupby(['season','bowler']).agg(
        total_runs_conceded=('total_runs', 'sum'),
        total_wickets_taken=('is_wicket', 'sum'),
        total_balls_bowled=('ball', 'count')
    ).reset_index()

    bowler_average_strike_rate_df['strike_rate'] = bowler_average_strike_rate_df['total_balls_bowled'] / bowler_average_strike_rate_df['total_wickets_taken']
    bowler_average_strike_rate_df['average'] = bowler_average_strike_rate_df['total_runs_conceded'] / bowler_average_strike_rate_df['total_wickets_taken']
    
    fig = go.Figure()
    fig2 = go.Figure()
    for player in bowler_average_strike_rate_df['bowler'].unique():
        player_df = bowler_average_strike_rate_df[bowler_average_strike_rate_df['bowler'] == player]
        played_teams, marker_colors = player_played_team_each_season(filtered_ipl_df, player)
        strike_rate_line_trace = go.Scatter(
            x=player_df['season'],
            y=player_df['strike_rate'],
            mode='lines+markers',
            hovertemplate="Player: %{text}<br>Played Team: %{customdata}<br>Season: %{x}<br>Strike_rate: %{y}<extra></extra>",
            name=player,
            text=[player]*len(player_df),
            line=dict(shape='spline', width=3, color=player_last_played_team(ipl, player)),
            marker=dict(size=10, color=marker_colors, line=dict(width=2, color='white')),
            customdata=played_teams
        )
        average_line_trace = go.Scatter(
            x=player_df['season'],
            y=player_df['average'],
            mode='lines+markers',
            hovertemplate="Player: %{text}<br>Played Team: %{customdata}<br>Season: %{x}<br>Average: %{y}<extra></extra>",
            name=player,
            text=[player]*len(player_df),
            line=dict(shape='spline', width=3, color=player_last_played_team(ipl, player)),
            marker=dict(size=10, color=marker_colors, line=dict(width=2, color='white')),
            customdata=played_teams
        )
        fig2.add_trace(average_line_trace)
        fig.add_trace(strike_rate_line_trace)

    fig.update_layout(
        title=f'{player1} and {player2} Comparison by Strike Rate per season' if player2 else f'{player1} Strike Rate per season',
        hovermode='x unified', showlegend=False
    )
    fig2.update_layout(
        title=f'{player1} and {player2} Comparison by Average per season' if player2 else f'{player1} Average per season',
        hovermode='x unified', showlegend=False
    )
    add_tick_labels(fig)
    add_tick_labels(fig2)
    return update_layout(fig), update_layout(fig2)

def get_bowler_economy(ipl, player1, player2=None):
    filtered_ipl_df = ipl[ipl['bowler'].isin([player1, player2])] if player2 else ipl[ipl['bowler'] == player1]
    
    valid_dismissals = ['bowled', 'caught', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
    filtered_ipl_df = filtered_ipl_df[filtered_ipl_df['dismissal_kind'].isin(valid_dismissals) | filtered_ipl_df['dismissal_kind'].isnull()]
    legal_deliveries_df = filtered_ipl_df[~filtered_ipl_df['extra_runs'].isin(['wides', 'noballs'])]
    bowler_economy_df = legal_deliveries_df.groupby(['season','bowler']).agg(
        total_runs_conceded=('total_runs', 'sum'),
        total_wickets_taken=('is_wicket', 'sum'),
        total_balls_bowled=('ball', 'count')
    ).reset_index()

    bowler_economy_df['total_overs_bowled'] = bowler_economy_df['total_balls_bowled'] / 6
    bowler_economy_df['economy'] = bowler_economy_df['total_runs_conceded'] / bowler_economy_df['total_overs_bowled']
    
    fig = go.Figure()
    for player in bowler_economy_df['bowler'].unique():
        player_df = bowler_economy_df[bowler_economy_df['bowler'] == player]
        played_teams, marker_colors = player_played_team_each_season(filtered_ipl_df, player)
        economy_line_trace = go.Scatter(
            x=player_df['season'],
            y=player_df['economy'],
            mode='lines+markers',
            hovertemplate="Player: %{text}<br>Played Team: %{customdata}<br>Season: %{x}<br>Economy: %{y}<extra></extra>",
            name=player,
            text=[player]*len(player_df),
            line=dict(shape='spline', width=3, color=player_last_played_team(ipl, player)),
            marker=dict(size=10, color=marker_colors, line=dict(width=2, color='white')),
            customdata=played_teams
        )
        fig.add_trace(economy_line_trace)

    fig.update_layout(
        title=f'{player1} and {player2} Comparison by Economy per season' if player2 else f'{player1} Economy per season',
        hovermode='x unified', showlegend=False
    )
    add_tick_labels(fig)
    return update_layout(fig)


def get_bowler_wickets_against_other_teams(ipl, player1, player2, seasons=None):
    filtered_ipl_df = ipl[ipl['bowler'].isin([player1, player2])].copy() if player2 else ipl[ipl['bowler'] == player1].copy()
    valid_dismissals = ['bowled', 'caught', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
    filtered_ipl_df = filtered_ipl_df[filtered_ipl_df['dismissal_kind'].isin(valid_dismissals)]
    bowler_wickets_df = filtered_ipl_df.groupby(['bowler','batting_team'])['is_wicket'].sum().reset_index(name='total_wickets')
    
    fig = go.Figure()
    for player in [player1, player2]:
        player_df = bowler_wickets_df[bowler_wickets_df['bowler'] == player]
        if player_df.empty:
            continue
        bar_color = player_last_played_team(ipl, player)
        fig.add_trace(go.Bar(
            x=player_df['batting_team'],
            y=player_df['total_wickets'],
            marker_color=bar_color,
            name=player,
            hovertemplate="Batting Team: %{x}<br>Runs: %{y}<extra></extra>"
        ))
    fig.update_layout(title=f'{player1} wickets against other teams', showlegend=False)
    return update_layout(fig)

def get_bowler_wickets_at_each_venue(ipl, player1, player2, seasons=None):
    valid_dismissals = ['bowled', 'caught', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
    
    if player2:
        filtered_ipl_df = ipl[ipl['bowler'].isin([player1, player2])].copy()
        filtered_ipl_df = filtered_ipl_df[filtered_ipl_df['dismissal_kind'].isin(valid_dismissals)]
        venue_wickets = filtered_ipl_df.groupby('venue')['is_wicket'].sum().reset_index(name='total_wickets')
    else:
        filtered_ipl_df = ipl[ipl['bowler'] == player1].copy()
        filtered_ipl_df = filtered_ipl_df[filtered_ipl_df['dismissal_kind'].isin(valid_dismissals)]
        venue_wickets = filtered_ipl_df.groupby('venue')['is_wicket'].sum().reset_index(name='total_wickets')
    
    top_venues = venue_wickets.sort_values(by='total_wickets', ascending=False)['venue'].head(10).tolist()
    bowler_wickets_df = filtered_ipl_df[filtered_ipl_df['venue'].isin(top_venues)].groupby(['bowler','venue'])['is_wicket'].sum().reset_index(name='total_wickets')

    fig = go.Figure()
    for player in [player1, player2]:
        if not player:
            continue
        player_df = bowler_wickets_df[bowler_wickets_df['bowler'] == player]
        if player_df.empty:
            continue
        bar_color = player_last_played_team(ipl, player)
        short_names = player_df['venue'].apply(lambda v: VENUE_MAP.get(v, v.split(',')[0][:18] + ("..." if len(v.split(',')[0]) > 18 else "")))
        fig.add_trace(go.Bar(
            x=short_names,
            y=player_df['total_wickets'],
            marker_color=bar_color,
            name=player,
            hovertemplate=[f"Venue: {venue}<br>Wickets: {wickets}<extra></extra>" for venue, wickets in zip(player_df['venue'], player_df['total_wickets'])],
        ))
    fig.update_layout(
        title='Wickets by Player at Each Venue (Top 10)', showlegend=False
    )
    return update_layout(fig)