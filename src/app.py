import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from load_n_clean import load_data


# Load data
dbName = 'cryptos.db'
tbNames = ['BTC', 'ETH', 'SOL', 'ALGO', 'XRP', 'HBAR', 'BONK', 'LINK']
df = load_data(dbName, tbNames[0])['close']
for tb in tbNames[1:]:
    new_df = load_data(dbName, tb)['close']
    df = pd.concat([df, new_df], axis=1)
df.columns = tbNames

# compute returns
rets = df.pct_change().dropna()
cumrets = (1 + df.pct_change()).cumprod()
cumrets.iloc[0] = 1.



# Initialize the app
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Asset Analysis Dashboard"),

    html.H3("Select an asset"),

    ##  dropdown menu for a SINGLE asset/time series choice
    html.Div([
        dcc.Dropdown(
            id='single-asset-dropdown',
            options=[{'label': i, 'value': i} for i in df.columns],
            value=df.columns[0]
        )
    ], style={'width': '48%', 'display': 'inline-block'}),
    # placeholder for the plots
    dcc.Graph(id='price-graph'),
    dcc.Graph(id='periodic-returns'),

    ## dropdown for multi-asset selection
    html.H3("Select two or more assets"),
    html.Div([
        dcc.Dropdown(
            id='multi-asset-dropdown',
            options=[{'label': i, 'value': i} for i in df.columns],
            value=[df.columns[0]],
            multi=True
        )
    ], style={'width': '48%', 'display': 'inline-block'}),
    # placeholder for plots
    dcc.Graph(id='correlation-heatmap'),
    dcc.Graph(id='cumrets-comparison')
])

## single-asset dropdown
# price series
@app.callback(
    [
        Output('price-graph', 'figure'),
        Output('periodic-returns', 'figure')
    ],
    [Input('single-asset-dropdown', 'value')]
)
def update_single_asset_graphs(selected_asset):
    "Price series plot"
    fig_price = go.Figure()
    fig_price.add_trace(
        go.Scatter(x=df.index, y=df[selected_asset], mode='lines', name=selected_asset)
    )
    fig_price.update_layout(title=f'Hourly closing price of {selected_asset}', 
                      xaxis_title='', 
                      yaxis_title='[$]')

    "Return series plot"
    fig_ret = go.Figure()
    fig_ret.add_trace(
        go.Scatter(x=rets.index, y=rets[selected_asset], mode='lines', name=selected_asset)
    )
    fig_ret.update_layout(title=f'Hourly returns of {selected_asset}', xaxis_title='', yaxis_title='[%]')
    return fig_price, fig_ret


## multiasset dropdown
@app.callback(
    [
        Output('cumrets-comparison', 'figure'), 
        Output('correlation-heatmap', 'figure')
    ], 
    [Input('multi-asset-dropdown', 'value')]
)
def update_cumrets_compare_graph(selected_assets):
    # cum ret plot
    fig_cumret = px.line(cumrets[selected_assets])
    fig_cumret.update_layout(
        title='Cumulative returns of several assets', 
        xaxis_title='', yaxis_title='[$]', 
        legend=dict(title='Asset'))

    #  corr heatmap
    # if len(selected_assets) < 2:
    #     return {'data': [], 'layout': go.Layout(title='Select at least two assets')}

    corr = rets[selected_assets].corr()
    fig_heatmap = {
        'data': [go.Heatmap(
            z=corr.values,
            x=corr.index.values,
            y=corr.columns.values,
            colorscale='Blues'
        )],
        'layout': go.Layout(title='Correlation Heatmap of Asset Returns', xaxis={'side': 'bottom'})
    }
    return fig_cumret, fig_heatmap

# Debugging
# if __name__ == '__main__':
#     app.run_server(debug=True)

# click "http://127.0.0.1:8050" to view app on local machine
# Production
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=False)