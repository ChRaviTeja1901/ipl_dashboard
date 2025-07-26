from dash import Dash, dcc, html
from tabs import overview, batting_stats, bowling_stats, teams_comparison, player_insights
from dash.dependencies import Input, Output

# Initialize app
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "IPL Dashboard"

# Layout
app.layout = html.Div([
    html.Div([
        html.H2("IPL Statistics Dashboard", className="main-title"),
        dcc.Tabs(id='tabs', value='overview', children=[
            dcc.Tab(label='Overview', value='overview'),
            dcc.Tab(label='Batting Stats', value='batting'),
            dcc.Tab(label='Bowling Stats', value='bowling'),
            dcc.Tab(label='Team Comparison', value='team'),
            dcc.Tab(label='Player Insights', value='player'),
        ], className="main-tabs"),
    ], className="header-tabs-row"),

    html.Div(id='tab-content')  # Tab output content
])

@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value')
)
def render_content(tab):
    if tab == 'overview':
        return overview.layout
    elif tab == 'batting':
        return batting_stats.layout
    elif tab == 'bowling':
        return bowling_stats.layout
    elif tab == 'team':
        return teams_comparison.layout
    elif tab == 'player':
        return player_insights.layout

if __name__ == '__main__':
    app.run(debug=True)
