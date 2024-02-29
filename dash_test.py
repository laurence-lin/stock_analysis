# These are the libaries to be used.
import dash
from dash import html, dcc, dash_table, callback_context, callback
import plotly.graph_objects as go
import dash_trich_components as dtc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc  # some default framework can be used created by bootstrap CSS modeuls
import plotly.express as px
import json
import pandas as pd
import numpy as np
import datetime
from scipy.stats import pearsonr
from datetime import date

# 1. Data Collection & Cleaning 
#stocks = pd.read_csv('export_data/export.csv')

from sqlalchemy import create_engine, text
engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost:5432/stock_analysis', echo=True)

with engine.connect() as conn:

    stocks = pd.read_sql("select * from stock_raw where time_stamp >= current_date - interval '30' day", conn)


# 'fig' exposes the candlestick chart with the prices of the stock since 2015.
fig = go.Figure()

# Observe that we are promtly filling the charts with AMBEV's data.
fig.add_trace(go.Candlestick(x=stocks['time_stamp'],
                             open=stocks['price_full'].apply(lambda x: x.split(',')[0]),
                             close=stocks['price_full'].apply(lambda x: x.split(',')[1]),
                             high=stocks['price_full'].apply(lambda x: x.split(',')[2]),
                             low=stocks['price_full'].apply(lambda x: x.split(',')[3]),
                             name='Stock Price'))
fig.update_layout(
    paper_bgcolor='black',
    font_color='grey',
    height=500,
    width=1000,
    margin=dict(l=10, r=10, b=5, t=5),
    autosize=False,
    showlegend=False
)
# Setting the graph to display the 2021 prices in a first moment. 
# Nonetheless,the user can also manually ajust the zoom size either by selecting a 
# section of the chart or using one of the time span buttons available.

# These two variables are going to be of use for the time span buttons.
min_date = '2024-02-01'
max_date = '2024-02-20'
fig.update_xaxes(range=[min_date, max_date])
fig.update_yaxes(tickprefix='R$')


# 2. Data Importing & Default Charts (Ending)

# Loading the dashboard's 'sector_stock' and 'carousel_prices'  json files.
#ector_stocks = json.load(open('sector_stocks.json', 'r'))
#carousel_prices = json.load(open('carousel_prices.json', 'r'))

# 3. Application's Layout
app = dash.Dash(__name__)

# Beginning the layout. The whole dashboard is contained inside a Div and a Bootstrap
# Row.

# Extract some fields to show in plot from stock raw data
stocks['ticker'] = stocks['stock_code'].apply(lambda x: x.split('_')[0]) # extract ticker from stock_code
stocks['price'] = stocks['price'].apply(lambda x: round(float(x), 2))


app.layout = html.Div(children = [ # children is always the first attribute which can be omitted
    html.Div([
        html.H1("The first stock analysis dash board"),
        html.Hr(), # add a separate line
        dbc.Row([
            dbc.Col(
            dcc.Dropdown(
                options = stocks['ticker'],
                value = '0050.TW',
                id = 'dropdown list of stock tickers'
                ),
            witdh = 'auto'
            ),
            dbc.Col(
            dcc.DatePickerRange(
                id = 'date_range for chart',
                min_date_allowed = date(2024, 1, 1),  # min allowed date to select in the date option
                max_date_allowed = date(2024, 2, 28),
                #initial_visible_month = date(2024, 1, 1)  # month first displayed in calendar
                start_date = date(2024, 1, 1),
                end_date = date(2024, 1, 31)
            ), witdh = 'auto'
            )
        
    ])
]),
    html.Br(),
    #dash_table.DataTable(data=df_sub.to_dict('records'), page_size=6),
    # Graph
    dcc.Graph(
        id = 'Line graph',
        figure = {}
    )
])


# Callback fundtions
@callback(
    Output(component_id = 'Line graph', component_property = 'figure'),
    Input(component_id = 'dropdown list of stock tickers', component_property = 'value'),
    Input('date_range for chart', 'start_date'),
    Input('date_range for chart', 'end_date')
)
def update_graph(stock_ticker, start_date, end_date):
    stocks_sub = stocks[(stocks['time_stamp'] >= start_date) & (stocks['time_stamp'] <= end_date) & (stocks['ticker'] == stock_ticker)]
    fig = px.line(stocks_sub, x = 'time_stamp', y = 'price')
    return fig

# Finally, running the Dash app.
if __name__ == '__main__':
    app.run_server(debug=True)