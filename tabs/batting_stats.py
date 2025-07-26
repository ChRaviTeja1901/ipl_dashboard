from dash import html, dcc, callback, Output, Input
from utils.data_loader import (
    load_data, get_highest_run_chase, get_top_scorers, get_total_runs, get_total_matches,
    get_runs_distribution, get_runs_distribution_per_over, get_batting_runrate_by_team,
    get_batting_average_by_team, get_lowest_total, get_batting_strike_rate_by_team
)

matches_df, deliveries_df, ipl_df = load_data()
seasons = matches_df['season'].unique()

# Precompute initial values for layout (no season filter)
initial_values = {
    'total_runs': get_total_runs(ipl_df),
    'total_matches': get_total_matches(matches_df),
    'batsman_runs': get_top_scorers(ipl_df, 1),
    'top_scorers_fig': get_top_scorers(ipl_df, 10),
    'runs_distribution_fig': get_runs_distribution(ipl_df),
    'runs_distribution_per_over_fig': get_runs_distribution_per_over(ipl_df),
    'batting_runrate_by_team_fig': get_batting_runrate_by_team(ipl_df),
    'batting_average_by_team_fig': get_batting_average_by_team(ipl_df),
    'batting_strike_rate_by_team_fig': get_batting_strike_rate_by_team(ipl_df),
    'highest_run_chase': get_highest_run_chase(matches_df),
    'lowest_total': get_lowest_total(ipl_df)
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
            html.Div(initial_values['total_runs'], className='kpi-value', id='total_runs'),
            html.Div('Total Runs', className='kpi-label')
        ], className='kpi-card'),
        html.Div([
            html.Div(initial_values['total_matches'], className='kpi-value', id='batting_total_matches'),
            html.Div('Total Matches', className='kpi-label')
        ], className='kpi-card'),
        html.Div([
            html.Div(initial_values['batsman_runs'], className='kpi-value', id='top_scorer'),
            html.Div('Top Scorer', className='kpi-label')
        ], className='kpi-card'),
        html.Div([
            html.Div(initial_values['highest_run_chase'], className='kpi-value', id='highest_run_chase'),
            html.Div('Highest Run Chase', className='kpi-label')
        ], className='kpi-card'),
        html.Div([
            html.Div(initial_values['lowest_total'], className='kpi-value', id='lowest_total'),
            html.Div('Lowest Total', className='kpi-label')
        ], className='kpi-card'),
        html.Div([
            html.Div(initial_values['batting_runrate_by_team_fig'].data[0]['y'][0] if initial_values['batting_runrate_by_team_fig'].data else '-', className='kpi-value', id='batting_runrate'),
            html.Div('Best Team Run Rate', className='kpi-label')
        ], className='kpi-card'),
        html.Div([
            html.Div(round(initial_values['batting_strike_rate_by_team_fig'].data[0]['y'][0], 2) if initial_values['batting_strike_rate_by_team_fig'].data else '-', className='kpi-value', id='batting_strike_rate'),
            html.Div('Best Team Strike Rate', className='kpi-label')
        ], className='kpi-card'),
        html.Div([
            html.Div(initial_values['batting_average_by_team_fig'].data[0]['y'][0] if initial_values['batting_average_by_team_fig'].data else '-', className='kpi-value', id='batting_average'),
            html.Div('Best Team Batting Avg', className='kpi-label')
        ], className='kpi-card'),
    ], className='kpi-row'),
    # Toss Scorers
    html.Div([
        html.Div([
            dcc.Graph(figure=initial_values['top_scorers_fig'], id='top_scorers', className='chart-style')
        ], className="half-chart"),
        html.Div([
            dcc.Graph(figure=initial_values['runs_distribution_fig'], id='runs_distribution', className='chart-style')
        ], className="half-chart"),
    ], className="chart-row"),
    #runs per over
    html.Div([
        dcc.Graph(figure=initial_values['runs_distribution_per_over_fig'], className="chart-style", id="runs_distribution_per_over")
    ], className='full-chart'),
    html.Div([
        dcc.Graph(figure=initial_values['batting_runrate_by_team_fig'], className="chart-style", id="batting_runrate_by_team")
    ], className='full-chart'),
    html.Div([
        dcc.Graph(figure=initial_values['batting_strike_rate_by_team_fig'], className="chart-style", id="batting_strike_rate_by_team")
    ], className='full-chart'),
    html.Div([
        dcc.Graph(figure=initial_values['batting_average_by_team_fig'], className="chart-style", id="batting_average_by_team")
    ], className='full-chart'),
])

@callback(
    Output(component_id='total_runs', component_property='children'),
    Output(component_id='batting_total_matches', component_property='children'),
    Output(component_id='top_scorer', component_property='children'),
    Output(component_id='highest_run_chase', component_property='children'),
    Output(component_id='lowest_total', component_property='children'),
    Output(component_id='top_scorers', component_property='figure'),
    Output(component_id='runs_distribution', component_property='figure'),
    Output(component_id='runs_distribution_per_over', component_property='figure'),
    Output(component_id='batting_runrate_by_team', component_property='figure'),
    Output(component_id='batting_strike_rate_by_team', component_property='figure'),
    Output(component_id='batting_average_by_team', component_property='figure'),
    Input(component_id='season-filter', component_property='value')
)
def update_page(selected_seasons):
    # Use a dict to group all outputs for clarity
    outputs = {
        'total_runs': get_total_runs(ipl_df, selected_seasons),
        'total_matches': get_total_matches(matches_df, selected_seasons),
        'batsman_runs': get_top_scorers(ipl_df, 1, selected_seasons),
        'top_scorers_fig': get_top_scorers(ipl_df, 10, selected_seasons),
        'runs_distribution_fig': get_runs_distribution(ipl_df, selected_seasons),
        'runs_distribution_per_over_fig': get_runs_distribution_per_over(ipl_df, selected_seasons),
        'batting_runrate_by_team_fig': get_batting_runrate_by_team(ipl_df, selected_seasons),
        'batting_strike_rate_by_team_fig': get_batting_strike_rate_by_team(ipl_df, selected_seasons),
        'batting_average_by_team_fig': get_batting_average_by_team(ipl_df, selected_seasons),
        'highest_run_chase': get_highest_run_chase(matches_df, selected_seasons),
        'lowest_total': get_lowest_total(ipl_df, selected_seasons)
    }
    return (
        outputs['total_runs'],
        outputs['total_matches'],
        outputs['batsman_runs'],
        outputs['highest_run_chase'],
        outputs['lowest_total'],
        outputs['top_scorers_fig'],
        outputs['runs_distribution_fig'],
        outputs['runs_distribution_per_over_fig'],
        outputs['batting_runrate_by_team_fig'],
        outputs['batting_strike_rate_by_team_fig'],
        outputs['batting_average_by_team_fig']
    )
