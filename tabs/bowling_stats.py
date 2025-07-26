from dash import html, dcc, callback, Output, Input
from utils.data_loader import (
    load_data, get_top_bowlers, get_total_wickets, get_total_matches, get_best_bowling_figures,
    get_bowling_average_by_team, get_most_expensive_overs, get_dismissal_kind,
    get_most_number_of_hattricks, get_bowling_strike_rate_by_team, get_bowling_economy_by_team,
    get_best_team_average, get_best_team_economy, get_best_team_strike_rate
)

matches_df, deliveries_df, ipl_df = load_data()
seasons = matches_df['season'].unique()

# Precompute initial values for layout (no season filter) using dictionary comprehension for consistency
top_bowlers_wickets, top_bowlers_economy = get_top_bowlers(ipl_df, 10)
initial_values = {
    'total_wickets': get_total_wickets(ipl_df),
    'bowler_wickets': get_top_bowlers(ipl_df, 1),
    'top_wicket_takers': top_bowlers_wickets,
    'top_bowlers_by_economy': top_bowlers_economy,
    'total_matches': get_total_matches(matches_df),
    'most_expensive_overs': get_most_expensive_overs(ipl_df, 10),
    'dismissal_kind': get_dismissal_kind(ipl_df),
    'most_number_of_hattricks': get_most_number_of_hattricks(ipl_df),
    'best_bowling_figures': get_best_bowling_figures(ipl_df),
    'bowling_strike_rate_by_team': get_bowling_strike_rate_by_team(ipl_df),
    'bowling_average_by_team': get_bowling_average_by_team(ipl_df),
    'bowling_economy_by_team': get_bowling_economy_by_team(ipl_df),
    'best_team_average': get_best_team_average(ipl_df),
    'best_team_economy': get_best_team_economy(ipl_df),
    'best_team_strike_rate': get_best_team_strike_rate(ipl_df)
    
}

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
        )
    ]),
    # KPI Cards
    html.Div([
        html.Div([
            html.Div(initial_values['total_wickets'], className='kpi-value', id='total_wickets'),
            html.Div('Total Wickets', className='kpi-label')
        ], className='kpi-card'),
        html.Div([
            html.Div(initial_values['total_matches'], className='kpi-value', id='bowling_total_matches'),
            html.Div('Total Matches', className='kpi-label')
        ], className='kpi-card'),
        html.Div([
            html.Div(initial_values['bowler_wickets'], className='kpi-value', id='highest_wicket_taker'),
            html.Div('Highest Wicket Taker', className='kpi-label')
        ], className='kpi-card'),
        html.Div([
            html.Div(initial_values['best_bowling_figures'], className='kpi-value', id='best_bowling_figures'),
            html.Div('Best Bowling Figures', className='kpi-label')
        ], className='kpi-card'),
        html.Div([
            html.Div(initial_values['most_number_of_hattricks'], className='kpi-value', id='most_number_of_hattricks'),
            html.Div('Most No.of Hattricks', className='kpi-label')
        ], className='kpi-card'),
        html.Div([
            html.Div(initial_values['best_team_economy'], className='kpi-value', id='best_team_economy'),
            html.Div('Best Team Economy', className='kpi-label')
        ], className='kpi-card'),
        html.Div([
            html.Div(initial_values['best_team_strike_rate'], className='kpi-value', id='best_team_strike_rate'),
            html.Div('Best Team Strike Rate', className='kpi-label')
        ], className='kpi-card'),
        html.Div([
            html.Div(initial_values['best_team_average'], className='kpi-value', id='best_team_average'),
            html.Div('Best Team Bowling Avg', className='kpi-label')
        ], className='kpi-card'),
    ], className='kpi-row'),
    # Toss Scorers
    html.Div([
        html.Div([
            dcc.Graph(figure=initial_values['top_wicket_takers'], id='top_wicket_takers', className='chart-style')
        ], className="half-chart"),
        html.Div([
            dcc.Graph(figure=initial_values['most_expensive_overs'], id='most_expensive_overs', className='chart-style')
        ], className="half-chart"),
    ], className="chart-row"),
    html.Div([
        html.Div([
            dcc.Graph(figure=initial_values['top_bowlers_by_economy'], id='top_bowlers_by_economy', className='chart-style')
        ], className="half-chart"),
        html.Div([
            dcc.Graph(figure=initial_values['dismissal_kind'], id='dismissal_kind', className='chart-style')
        ], className="half-chart"),
    ], className="chart-row"),
    html.Div([
        dcc.Graph(figure=initial_values['bowling_economy_by_team'], className="chart-style", id="bowling_economy_by_team")
    ], className='full-chart'),
    html.Div([
        dcc.Graph(figure=initial_values['bowling_strike_rate_by_team'], className="chart-style", id="bowling_strike_rate_by_team")
    ], className='full-chart'),
    html.Div([
        dcc.Graph(figure=initial_values['bowling_average_by_team'], className="chart-style", id="bowling_average_by_team")
    ], className='full-chart'),
])

@callback(
    Output(component_id='total_wickets', component_property='children'),
    Output(component_id='bowling_total_matches', component_property='children'),
    Output(component_id='highest_wicket_taker', component_property='children'),
    Output(component_id='best_bowling_figures', component_property='children'),
    Output(component_id='most_number_of_hattricks', component_property='children'),
    Output(component_id='best_team_average', component_property='children'),
    Output(component_id='best_team_economy', component_property='children'),
    Output(component_id='best_team_strike_rate', component_property='children'),
    Output(component_id='top_wicket_takers', component_property='figure'),
    Output(component_id='most_expensive_overs', component_property='figure'),
    Output(component_id='dismissal_kind', component_property='figure'),
    Output(component_id='bowling_economy_by_team', component_property='figure'),
    Output(component_id='bowling_strike_rate_by_team', component_property='figure'),
    Output(component_id='bowling_average_by_team', component_property='figure'),
    Input(component_id='season-filter', component_property='value')
)
def update_page(selected_seasons):
    top_wicket_takers_fig, _ = get_top_bowlers(ipl_df, 10, selected_seasons)
    outputs = {
        'total_wickets': get_total_wickets(ipl_df, selected_seasons),
        'total_matches': get_total_matches(matches_df, selected_seasons),
        'highest_wicket_taker': get_top_bowlers(ipl_df, 1, selected_seasons),
        'best_bowling_figures': get_best_bowling_figures(ipl_df, selected_seasons),
        'most_number_of_hattricks': get_most_number_of_hattricks(ipl_df, selected_seasons),
        'top_wicket_takers': top_wicket_takers_fig,
        'most_expensive_overs': get_most_expensive_overs(ipl_df, 10, selected_seasons),
        'dismissal_kind': get_dismissal_kind(ipl_df, selected_seasons),
        'bowling_economy_by_team': get_bowling_economy_by_team(ipl_df, selected_seasons),
        'bowling_strike_rate_by_team': get_bowling_strike_rate_by_team(ipl_df, selected_seasons),
        'bowling_average_by_team': get_bowling_average_by_team(ipl_df, selected_seasons),
        'best_team_average': get_best_team_average(ipl_df, selected_seasons),
        'best_team_economy': get_best_team_economy(ipl_df, selected_seasons),
        'best_team_strike_rate': get_best_team_strike_rate(ipl_df, selected_seasons)
    }
    return (
        outputs['total_wickets'],
        outputs['total_matches'],
        outputs['highest_wicket_taker'],
        outputs['best_bowling_figures'],
        outputs['most_number_of_hattricks'],
        outputs['best_team_average'],
        outputs['best_team_economy'],
        outputs['best_team_strike_rate'],
        outputs['top_wicket_takers'],
        outputs['most_expensive_overs'],
        outputs['dismissal_kind'],
        outputs['bowling_economy_by_team'],
        outputs['bowling_strike_rate_by_team'],
        outputs['bowling_average_by_team']
    )
