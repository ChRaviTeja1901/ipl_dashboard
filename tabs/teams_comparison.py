from dash import html, dcc, callback, Output, Input, dash_table
from utils.data_loader import load_data, get_team_stats, get_teams_stats_figs, get_team_wins_fig, get_head_to_head_win_stats, get_powerplay_death_batting_stats, get_powerplay_death_bowling_stats, get_top_scorer_top_bowler_stats, get_boundary_count, get_dismissal_type_distribution, get_batting_strike_rate, get_bowling_economy

matches_df, deliveries_df, ipl_df = load_data()
seasons = matches_df['season'].unique()
teams = ['Royal Challengers Bengaluru', 'Punjab Kings', 'Delhi Capitals', 'Mumbai Indians', 'Kolkata Knight Riders', 'Rajasthan Royals', 'Sunrisers Hyderabad', 'Chennai Super Kings', 'Gujarat Titans', 'Lucknow Super Giants']

layout = html.Div([
    html.Hr(),
    html.Div([
        dcc.Dropdown(
            id='season-filter',
            options=[{'label': i, 'value': i} for i in seasons],
            value='',
            multi=True,
            className='season-filter',
            placeholder="Select Season"
        ),
        dcc.Dropdown(
            id='team1-filter',
            options=[{'label': i, 'value': i} for i in teams],
            value='',
            className='team1-filter',
            placeholder="Select Team 1"
        ),
        dcc.Dropdown(
            id='team2-filter',
            options=[{'label': i, 'value': i} for i in teams],
            value='',
            className='team2-filter',
            placeholder="Select Team 2"
        ),
    ], className='filters'),
    html.Div(id='comparison-content'),
    html.Div(id='stats-row-container'),
    html.Div(id='other-stats-row-container'),
    html.Div(id='wickets-stats-row-container'),
    html.Div(id='wins-row-container'),
    html.Div(id='batting-stats-row-container'),
    html.Div(id='bowling-stats-row-container'),
    html.Div(id='strike-rate-row-container'),
    html.Div(id='bowling-economy-row-container')
])


@callback(
    Output('team2-filter', 'options'),
    Input('team1-filter', 'value')
)
def update_team2_options(selected_team1):
    return [{'label': i, 'value': i} for i in teams if i != selected_team1] if selected_team1 else [{'label': i, 'value': i} for i in teams]


@callback(
    Output('team1-filter', 'options'),
    Input('team2-filter', 'value')
)
def update_team1_options(selected_team2):
    return [{'label': i, 'value': i} for i in teams if i != selected_team2] if selected_team2 else [{'label': i, 'value': i} for i in teams]


@callback(
    Output('comparison-content', 'children'),
    Output('stats-row-container', 'children'),
    Output('other-stats-row-container', 'children'),
    Output('wickets-stats-row-container', 'children'),
    Output('wins-row-container', 'children'),
    Output('batting-stats-row-container', 'children'),
    Output('bowling-stats-row-container', 'children'),
    Output('strike-rate-row-container', 'children'),
    Output('bowling-economy-row-container', 'children'),
    Input('team1-filter', 'value'),
    Input('team2-filter', 'value'),
    Input('season-filter', 'value')
)
def update_comparison_content(team1, team2, seasons):
    if not team1 or not team2:
        # Only show the warning message if one of the teams is not selected
        return html.Div("Select both teams to compare.", className="compare-msg"), None, None, None, None, None, None, None, None

    # Compute all figures and tables in a dictionary for maintainability
    outputs = {}
    outputs['team1_df'] = get_team_stats(ipl_df, team1, seasons)
    outputs['team2_df'] = get_team_stats(ipl_df, team2, seasons)
    outputs['basic_stats'], outputs['batting_stats'], outputs['bowling_stats'] = get_teams_stats_figs(ipl_df, team1, team2, seasons)
    outputs['team_wins'] = get_team_wins_fig(matches_df, team1, team2)
    outputs['head_to_head'] = get_head_to_head_win_stats(matches_df, team1, team2, seasons)
    outputs['powerplay_overs_batting_stats'], outputs['death_overs_batting_stats'] = get_powerplay_death_batting_stats(ipl_df, team1, team2)
    outputs['powerplay_overs_bowling_stats'], outputs['death_overs_bowling_stats'] = get_powerplay_death_bowling_stats(ipl_df, team1, team2)
    outputs['top_scorer_top_bowler_stats'] = get_top_scorer_top_bowler_stats(ipl_df, team1, team2, seasons)
    outputs['boundary_count'] = get_boundary_count(ipl_df, team1, team2, seasons)
    outputs['wicket_taken_stats'], outputs['wicket_lost_stats'] = get_dismissal_type_distribution(ipl_df, team1, team2, seasons)
    outputs['strike_rate_stats'] = get_batting_strike_rate(ipl_df, team1, team2)
    outputs['bowling_economy_stats'] = get_bowling_economy(ipl_df, team1, team2)

    # Tables
    comparison_tables = html.Div([
        html.Div([
            dash_table.DataTable(
                data=outputs['team1_df'].to_dict('records'),
                columns=[{'name': i, 'id': i} for i in outputs['team1_df'].columns],
            )
        ], className=f'team-table team-bg-{team1.replace(" ", "-")}'),

        html.Div([
            dash_table.DataTable(
                data=outputs['team2_df'].to_dict('records'),
                columns=[{'name': i, 'id': i} for i in outputs['team2_df'].columns],
            )
        ], className=f"team-table team-bg-{team2.replace(' ', '-')}")
    ], className='comparison-tables')

    # Charts
    stats_row = html.Div([
        html.Div([dcc.Graph(figure=outputs['basic_stats'], className='chart-style')], className="third-chart"),
        html.Div([dcc.Graph(figure=outputs['batting_stats'], className='chart-style')], className="third-chart"),
        html.Div([dcc.Graph(figure=outputs['bowling_stats'], className='chart-style')], className="third-chart"),
    ], className="chart-row")

    wins_row = html.Div([
        html.Div([dcc.Graph(figure=outputs['team_wins'], className='chart-style')], className='full-chart')
    ])

    other_stats = html.Div([
        html.Div([dcc.Graph(figure=outputs['head_to_head'], className='chart-style')], className="third-chart"),
        html.Div([dcc.Graph(figure=outputs['top_scorer_top_bowler_stats'], className='chart-style')], className="third-chart"),
        html.Div([dcc.Graph(figure=outputs['boundary_count'], className='chart-style')], className="third-chart"),
    ], className="chart-row")

    batting_stats_row = html.Div([
        html.Div([dcc.Graph(figure=outputs['powerplay_overs_batting_stats'], className='chart-style')], className="half-chart"),
        html.Div([dcc.Graph(figure=outputs['death_overs_batting_stats'], className='chart-style')], className="half-chart"),
    ], className="chart-row")

    bowling_stats_row = html.Div([
        html.Div([dcc.Graph(figure=outputs['powerplay_overs_bowling_stats'], className='chart-style')], className="half-chart"),
        html.Div([dcc.Graph(figure=outputs['death_overs_bowling_stats'], className='chart-style')], className="half-chart"),
    ], className="chart-row")

    wickets_stats_row = html.Div([
        html.Div([dcc.Graph(figure=outputs['wicket_taken_stats'], className='chart-style')], className="half-chart"),
        html.Div([dcc.Graph(figure=outputs['wicket_lost_stats'], className='chart-style')], className="half-chart"),
    ], className="chart-row")

    strike_rate_stats_row = html.Div([
        html.Div([dcc.Graph(figure=outputs['strike_rate_stats'], className='chart-style')], className='full-chart')
    ])

    bowling_economy_stats_row = html.Div([
        html.Div([dcc.Graph(figure=outputs['bowling_economy_stats'], className='chart-style')], className='full-chart')
    ])

    return comparison_tables, stats_row, other_stats, wickets_stats_row, wins_row, batting_stats_row, bowling_stats_row, strike_rate_stats_row, bowling_economy_stats_row