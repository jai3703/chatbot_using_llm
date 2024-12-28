from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import numpy as np
import datetime
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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


nifty_top_500 = pd.read_csv("ind_nifty500list.csv")
app = Dash()

app.layout = [
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dcc.Dropdown(nifty_top_500.Industry.unique(),value="All", id='dropdown-selection-sector'),
    dcc.Dropdown( id='dropdown-selection'),
    dcc.Graph(id='graph-content')
]


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
