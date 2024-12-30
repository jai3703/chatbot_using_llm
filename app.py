from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd
import numpy as np
import datetime
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import candlestick_patterns_v2 as cp

# Load environment variables from .env file
load_dotenv()
# Access the database URL
db_url = os.getenv('DB_URL')

# Create connect sql database
def create_connection_database(db_url):
    # Database connection string
    db_url = db_url
    # Create an SQLAlchemy engine
    return create_engine(db_url)

# read data from the PostgreSQL table
try:
   with create_connection_database(db_url).connect() as connection:
    table_name = "nifty_top_500_stocks"
    query = f"SELECT * from {table_name};"
    df = pd.read_sql_query(query, con=create_connection_database(db_url))
    print("data pulled from sql table")
except Exception as e:
    print(f"Error: {e}")

# Volume confirmation
def volume_confirmation(days,df):
    """Check if current volume exceeds 10-day average volume."""
    df['Avg_Volume'] = df['VOLUME'].rolling(window=days).mean()
    df['Volume_Confirmed'] = df['VOLUME'] > 1.1 * df['Avg_Volume']
    return df

def process_dataframe(df):
    patterns = {
        "Doji": [],
        "Four Price Doji": [],
        "Long Legged Doji": [],
        "Gravestone Doji": [],
        "Dragonfly Doji": [],
        "Hammer": [],
        "Hanging Man": [],
        "Bullish Marubozu": [],
        "Bearish Marubozu": [],
    }

    for _, row in df.iterrows():
        candle = cp.SingleCandlePattern(row)
        patterns["Doji"].append(candle.is_doji())
        patterns["Four Price Doji"].append(candle.is_four_price_doji())
        patterns["Long Legged Doji"].append(candle.is_long_legged_doji())
        patterns["Gravestone Doji"].append(candle.is_gravestone_doji())
        patterns["Dragonfly Doji"].append(candle.is_dragonfly_doji())
        patterns["Hammer"].append(candle.is_hammer())
        patterns["Hanging Man"].append(candle.is_hanging_man())
        patterns["Bullish Marubozu"].append(candle.is_bullish_murubozu())
        patterns["Bearish Marubozu"].append(candle.is_bearish_murubozu())

    # Add results to the DataFrame
    for pattern, results in patterns.items():
        df[pattern] = results
    
    single_candle_patterns_columns = ["Doji",
        "Four Price Doji",
        "Long Legged Doji",
        "Gravestone Doji",
        "Dragonfly Doji",
        "Hammer",
        "Hanging Man",
        "Bullish Marubozu",
        "Bearish Marubozu"]
    df = df.sort_values(by=['SYMBOL','DATE'])
    df['Single_Candlestick_pattern'] = df[single_candle_patterns_columns].any(axis=1)
    df = volume_confirmation(10,df)
    return df

nifty_top_500 = pd.read_csv("ind_nifty500list.csv")
app = Dash()

app.layout = [
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dcc.DatePickerSingle(
        id='my-date-picker-single',
        min_date_allowed=df.DATE.min().date(),
        max_date_allowed=df.DATE.max().date(),
        initial_visible_month=df.DATE.min().date(),
        date=df.DATE.max().date()
    ),
    html.Br(),
    dash_table.DataTable(id='tbl'),
    dcc.Dropdown(nifty_top_500.Industry.unique(),value="All", id='dropdown-selection-sector'),
    dcc.Dropdown( id='dropdown-selection'),
    dcc.Graph(id='graph-content')
]


@callback(
    Output('tbl', 'data'),
    Output('tbl', 'columns'),
    Input('my-date-picker-single', 'date')
)
def update_table(value):
    
    processed_df = process_dataframe(df)
    dff = processed_df[processed_df.DATE==value]
    processed_df = dff[(dff['Single_Candlestick_pattern']==True) & (dff['Volume_Confirmed']==True)]
    return processed_df.to_dict('records'),[{"name": i, "id": i} for i in processed_df.columns]


@callback(
    Output('dropdown-selection', 'options'),
    Input('dropdown-selection-sector', 'value')
)
def update_graph(value):
    dff = nifty_top_500[nifty_top_500.Industry==value]
    return dff.Symbol.unique()


@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    dff = df[df.SYMBOL==value]

    fig = make_subplots
    fig = go.Figure(go.Candlestick(
        x=dff['DATE'],
        open=dff['OPEN'],
        high=dff['HIGH'],
        low=dff['LOW'],
        close=dff['CLOSE']
    ))
    return fig

if __name__ == '__main__':
    app.run(debug=True)
