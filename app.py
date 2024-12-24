from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")
import datetime
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

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


app = Dash()

app.layout = [
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dcc.Dropdown(df.Symbol.unique(), id='dropdown-selection'),
    dcc.Graph(id='graph-content')
]

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    dff = stocks_data[stocks_data.Symbol==value]
    return px.line(dff, x='Date', y='ClosePrice')

if __name__ == '__main__':
    app.run(debug=True)
