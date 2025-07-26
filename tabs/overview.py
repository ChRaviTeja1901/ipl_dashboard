from dash import html, dcc
from utils.data_loader import (
    load_data, get_summary_stats, get_matches_won, get_toss_decision, get_team_wins,
    get_top_scorers, get_top_bowlers, get_total_matches_per_season
)

matches_df, deliveries_df, ipl_df = load_data()
# Precompute initial values for layout (no filter)
initial_values = {}
initial_values['summary_stats'] = get_summary_stats(matches_df)
initial_values['matches_won'] = get_matches_won(matches_df)
initial_values['toss_decision'] = get_toss_decision(matches_df)
initial_values['team_wins'] = get_team_wins(matches_df)
initial_values['top_scorers'] = get_top_scorers(ipl_df, 5)
top_bowlers = get_top_bowlers(ipl_df, 5)
initial_values['top_bowlers_by_wickets'] = top_bowlers[0]
initial_values['top_bowlers_by_economy'] = top_bowlers[1]
initial_values['total_matches_per_season'] = get_total_matches_per_season(matches_df)

layout = html.Div([
    html.Hr(),
    # KPI Cards
    html.Div([
        html.Div([
            html.Div(initial_values['summary_stats']['total_matches'], className='kpi-value'),
            html.Div('Total Matches', className='kpi-label')
        ], className='kpi-card'),
        html.Div([
            html.Div(initial_values['summary_stats']['total_seasons'], className='kpi-value'),
            html.Div('Total Seasons', className='kpi-label')
        ], className='kpi-card'),
        html.Div([
            html.Div(initial_values['summary_stats']['total_teams'], className='kpi-value'),
            html.Div('Total Teams', className='kpi-label')
        ], className='kpi-card'),
        html.Div([
            html.Div(initial_values['summary_stats']['total_venues'], className='kpi-value'),
            html.Div('Total Venues', className='kpi-label')
        ], className='kpi-card'),
        html.Div([
            html.Div(f"{initial_values['summary_stats']['most_successful_team']} ({initial_values['summary_stats']['most_successful_team_wins']} wins)", className='kpi-value'),
            html.Div('Most Successful Team', className='kpi-label')
        ], className='kpi-card'),
        html.Div([
            html.Div(initial_values['summary_stats']['highest_match_aggregate'], className='kpi-value'),
            html.Div('Highest Match Agg', className='kpi-label')
        ], className='kpi-card'),
        html.Div([
            html.Div(f"{initial_values['summary_stats']['most_common_venue']} ({initial_values['summary_stats']['most_common_venue_count']} matches)", className='kpi-value'),
            html.Div('Most Common Venue', className='kpi-label')
        ], className='kpi-card'),
    ], className='kpi-row'),
    # Toss Decision & Team Wins
    html.Div([
        html.Div([
            dcc.Graph(figure=initial_values['toss_decision'], id='toss_decision', className='chart-style')
        ], className="half-chart"),
        html.Div([
            dcc.Graph(figure=initial_values['team_wins'], id='team_wins', className='chart-style')
        ], className="half-chart"),
    ], className="chart-row"),
    html.Div([
        dcc.Graph(figure=initial_values['total_matches_per_season'], className="chart-style")
    ], className='full-chart'),
    # Top Scorers, Bowlers (2 rows)
    html.Div([
        html.Div([
            dcc.Graph(figure=initial_values['top_scorers'], id='top_scorers', className='chart-style')
        ], className="third-chart"),
        html.Div([
            dcc.Graph(figure=initial_values['top_bowlers_by_wickets'], id='top_bowlers_by_wickets', className='chart-style')
        ], className="third-chart"),
        html.Div([
            dcc.Graph(figure=initial_values['top_bowlers_by_economy'], id='top_bowlers_by_economy', className='chart-style')
        ], className="third-chart"),
    ], className="chart-row"),
])
