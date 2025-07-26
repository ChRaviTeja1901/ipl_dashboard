from dash import html, dcc, callback, Output, Input, dash_table
from utils.data_loader import load_data, BATSMANS, BOWLERS, ALL_ROUNDERS, get_batter_runs, get_batter_strike_rate_average, get_batter_runs_against_other_teams, get_batter_runs_at_each_venue,get_bowler_wickets, get_bowler_strike_rate_average, get_bowler_economy, get_bowler_wickets_against_other_teams, get_bowler_wickets_at_each_venue, get_player_stats
matches_df, deliveries_df, ipl_df = load_data()
seasons = matches_df['season'].unique()

layout = html.Div([
    html.Hr(),
    html.Div([
        # dcc.Dropdown(
        #     id='season-filter',
        #     options=[{'label': i, 'value': i} for i in seasons],
        #     value='',
        #     multi=True,
        #     className='season-filter',
        #     placeholder="Select Season"
        # ),
        dcc.Dropdown(
            id='player1-filter',
            options=[
                {'label': '--- Batsman ---', 'value': 'batsman-separator', 'disabled': True},
                *[{'label': i, 'value': i} for i in BATSMANS],
                {'label': '--- Bowlers ---', 'value': 'bowler-separator', 'disabled': True},
                *[{'label': i, 'value': i} for i in BOWLERS],
                {'label': '--- All-rounders ---', 'value': 'allrounder-separator', 'disabled': True},
                *[{'label': i, 'value': i} for i in ALL_ROUNDERS],
            ],
            value='',
            className='player1-filter',
            placeholder="Select Player 1"
        ),
        dcc.Dropdown(
            id='player2-filter',
            options=[],
            value='',
            className='player2-filter',
            placeholder="Select Player 2"
        ),
    ], className='filters'),
    html.Div(id='batter-key-metrics-row-container'),
    html.Div(id='batter-runs-row-container'),
    html.Div(id='batter-sr-row-container'),
    html.Div(id='batter-avg-row-container'),
    html.Div(id='batter-runs-agnst-oth-teams-row-container'),
    html.Div(id='batter-runs-at-each-venue'),
    
    html.Div(id='bowler-key-metrics-row-container'),
    html.Div(id='bowler-wickets-row-container'),
    html.Div(id='bowler-sr-row-container'),
    html.Div(id='bowler-avg-row-container'),
    html.Div(id='bowler-economy-row-container'),
    html.Div(id='bowler-wickets-agnst-oth-teams-row-container'),
    html.Div(id='bowler-wickets-at-each-venue')
])



# Callback to update player2-filter options based on player1 selection
@callback(
    Output('player2-filter', 'options'),
    Input('player1-filter', 'value')
)
def update_player2_options(selected_player1):
    # Helper to build options with separator
    def build_options(label, items, exclude=None):
        opts = [{'label': f'--- {label} ---', 'value': f'{label.lower()}-separator', 'disabled': True}]
        opts += [{'label': i, 'value': i} for i in items if i != exclude]
        return opts

    if not selected_player1:
        # Show all options with separators if nothing is selected
        return (
            build_options('Batsman', BATSMANS) +
            build_options('Bowlers', BOWLERS) +
            build_options('All-rounders', ALL_ROUNDERS)
        )
    if selected_player1 in BATSMANS:
        return build_options('Batsman', BATSMANS, exclude=selected_player1)
    elif selected_player1 in BOWLERS:
        return build_options('Bowlers', BOWLERS, exclude=selected_player1)
    elif selected_player1 in ALL_ROUNDERS:
        return build_options('All-rounders', ALL_ROUNDERS, exclude=selected_player1)
    else:
        return []

@callback(
    Output('batter-key-metrics-row-container', 'children'),
    Output('batter-runs-row-container', 'children'),
    Output('batter-sr-row-container', 'children'),
    Output('batter-avg-row-container', 'children'),
    Output('batter-runs-agnst-oth-teams-row-container', 'children'),
    Output('batter-runs-at-each-venue', 'children'),
    Output('bowler-key-metrics-row-container', 'children'),
    Output('bowler-wickets-row-container', 'children'),
    Output('bowler-sr-row-container', 'children'),
    Output('bowler-avg-row-container', 'children'),
    Output('bowler-economy-row-container', 'children'),
    Output('bowler-wickets-agnst-oth-teams-row-container', 'children'),
    Output('bowler-wickets-at-each-venue', 'children'),
    Input('player1-filter', 'value'),
    Input('player2-filter', 'value')
)
def update_player_content(player1, player2, seasons=None):
    if not player1:
        return html.Div("Select Player 1", className="compare-msg"), *[None]*12

    stats = get_player_stats(ipl_df, player1, seasons)

    # def format_best_figures(fig_str):
    #     if fig_str and '/' in fig_str:
    #         return fig_str.split('(')[-1].replace(')', '').strip() if '(' in fig_str else fig_str.strip()
    #     return fig_str

    # Shared: Build metric cards
    def build_metric_cards(metrics):
        return html.Div([
            html.Div([
                html.Div(str(val), className='kpi-value'),
                html.Div(label, className='kpi-label')
            ], className='kpi-card') for label, val in metrics
        ], className='kpi-row')

    # BATTER
    if player1 in BATSMANS:
        metrics = [
            ('Total Matches', stats['total_matches']),
            ('Total Innings', stats['total_innings']),
            ('Total Runs', stats['total_runs']),
            ('Average', round(stats['batting_average'], 2)),
            ('Strike Rate', round(stats['batting_strike_rate'], 2)),
            ('Fours', stats['total_fours']),
            ('Sixes', stats['total_sixes']),
            ('Fifties', stats['fifties']),
            ('Hundreds', stats['hundreds']),
            ('Best Score', stats['best_score']),
            ('Most Common Dismissal', stats['dismissal_type_often']),
            ('Player of the Match', stats['player_of_the_match'])
        ]
        batter_metrics_row = build_metric_cards(metrics)

        batter_runs = get_batter_runs(ipl_df, player1, player2)
        batter_strike_rate, batter_average = get_batter_strike_rate_average(ipl_df, player1, player2)
        batter_runs_agnst_teams = get_batter_runs_against_other_teams(ipl_df, player1, player2)
        batter_runs_venues = get_batter_runs_at_each_venue(ipl_df, player1, player2)

        return (
            batter_metrics_row,
            html.Div([dcc.Graph(figure=batter_runs, className='chart-style')], className='full-chart'),
            html.Div([dcc.Graph(figure=batter_strike_rate, className='chart-style')], className='full-chart'),
            html.Div([dcc.Graph(figure=batter_average, className='chart-style')], className='full-chart'),
            html.Div([dcc.Graph(figure=batter_runs_agnst_teams, className='chart-style')], className='full-chart'),
            html.Div([dcc.Graph(figure=batter_runs_venues, className='chart-style')], className='full-chart'),
            None, None, None, None, None, None, None
        )

    # BOWLER
    elif player1 in BOWLERS:
        metrics = [
            ('Total Matches', stats.get('total_matches', '-')),
            ('Total Innings', stats.get('total_innings', '-')),
            ('Total Wickets', stats['total_wickets']),
            ('Runs Conceded', stats['run_conceded']),
            ('Balls Bowled', stats['balls_bowled']),
            ('Overs', round(stats['total_overs'], 2)),
            ('Average', round(stats['bowling_average'], 2)),
            ('Economy', round(stats['economy_rate'], 2)),
            ('Strike Rate', round(stats['bowling_strike_rate'], 2)),
            ('Best Bowling', stats['best_bowling_figures']),
            ('4 Wicket Hauls', stats['four_wicket_hauls']),
            ('5 Wicket Hauls', stats['five_wicket_hauls']),
            ('Maidens', stats['maiden_overs'])
        ]
        bowler_metrics_row = build_metric_cards(metrics)

        bowler_wickets = get_bowler_wickets(ipl_df, player1, player2)
        bowler_sr, bowler_avg = get_bowler_strike_rate_average(ipl_df, player1, player2)
        bowler_economy = get_bowler_economy(ipl_df, player1, player2)
        bowler_wickets_teams = get_bowler_wickets_against_other_teams(ipl_df, player1, player2)
        bowler_wickets_venues = get_bowler_wickets_at_each_venue(ipl_df, player1, player2)

        return (
            None, None, None, None, None, None,
            bowler_metrics_row,
            html.Div([dcc.Graph(figure=bowler_wickets, className='chart-style')], className='full-chart'),
            html.Div([dcc.Graph(figure=bowler_sr, className='chart-style')], className='full-chart'),
            html.Div([dcc.Graph(figure=bowler_avg, className='chart-style')], className='full-chart'),
            html.Div([dcc.Graph(figure=bowler_economy, className='chart-style')], className='full-chart'),
            html.Div([dcc.Graph(figure=bowler_wickets_teams, className='chart-style')], className='full-chart'),
            html.Div([dcc.Graph(figure=bowler_wickets_venues, className='chart-style')], className='full-chart'),
        )

    # ALL-ROUNDER
    elif player1 in ALL_ROUNDERS:
        batting = stats['batting']
        bowling = stats['bowling']
        metrics = [
            ('Total Runs', batting['total_runs']),
            ('Batting Average', round(batting['batting_average'], 2)),
            ('Batting Strike Rate', round(batting['batting_strike_rate'], 2)),
            ('Fifties', batting['fifties']),
            ('Hundreds', batting['hundreds']),
            ('Best Score', batting['best_score']),
            ('Total Wickets', bowling['total_wickets']),
            ('Bowling Average', round(bowling['bowling_average'], 2)),
            ('Economy', round(bowling['economy_rate'], 2)),
            ('Bowling Strike Rate', round(bowling['bowling_strike_rate'], 2)),
            ('Best Bowling', bowling['best_bowling_figures']),
            ('4 Wicket Hauls', bowling['four_wicket_hauls']),
            ('5 Wicket Hauls', bowling['five_wicket_hauls'])
        ]
        allrounder_metrics_row = build_metric_cards(metrics)

        # Batting
        batter_runs = get_batter_runs(ipl_df, player1, player2)
        batter_sr, batter_avg = get_batter_strike_rate_average(ipl_df, player1, player2)
        batter_runs_teams = get_batter_runs_against_other_teams(ipl_df, player1, player2)
        batter_runs_venues = get_batter_runs_at_each_venue(ipl_df, player1, player2)

        # Bowling
        bowler_wickets = get_bowler_wickets(ipl_df, player1, player2)
        bowler_sr, bowler_avg = get_bowler_strike_rate_average(ipl_df, player1, player2)
        bowler_economy = get_bowler_economy(ipl_df, player1, player2)
        bowler_wickets_teams = get_bowler_wickets_against_other_teams(ipl_df, player1, player2)
        bowler_wickets_venues = get_bowler_wickets_at_each_venue(ipl_df, player1, player2)

        return (
            allrounder_metrics_row,
            html.Div([dcc.Graph(figure=batter_runs, className='chart-style')], className='full-chart'),
            html.Div([dcc.Graph(figure=batter_sr, className='chart-style')], className='full-chart'),
            html.Div([dcc.Graph(figure=batter_avg, className='chart-style')], className='full-chart'),
            html.Div([dcc.Graph(figure=batter_runs_teams, className='chart-style')], className='full-chart'),
            html.Div([dcc.Graph(figure=batter_runs_venues, className='chart-style')], className='full-chart'), None,
            html.Div([dcc.Graph(figure=bowler_wickets, className='chart-style')], className='full-chart'),
            html.Div([dcc.Graph(figure=bowler_sr, className='chart-style')], className='full-chart'),
            html.Div([dcc.Graph(figure=bowler_avg, className='chart-style')], className='full-chart'),
            html.Div([dcc.Graph(figure=bowler_economy, className='chart-style')], className='full-chart'),
            html.Div([dcc.Graph(figure=bowler_wickets_teams, className='chart-style')], className='full-chart'),
            html.Div([dcc.Graph(figure=bowler_wickets_venues, className='chart-style')], className='full-chart')
        )

    return html.Div("Unknown player type"), *[None]*12