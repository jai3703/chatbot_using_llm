import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")
import datetime
from jugaad_data.nse import stock_df
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


def pull_stock_data(stock_symbol:str,start_date:datetime) -> pd.DataFrame:
    today = datetime.date.today()
    print(start_date,today)
    data = stock_df(symbol=stock_symbol, from_date=start_date,
            to_date=today, series="EQ")
    return data

# check last updated date for each stock and add data till current date
master_data = pd.DataFrame()
for symbol in df.SYMBOL.unique():
    start_date = df[df.SYMBOL == symbol].DATE.max().date()
    try:
        data = pull_stock_data(stock_symbol=symbol,start_date=start_date+datetime.timedelta(days=1))
        master_data = pd.concat([master_data,data],axis=0)
    except:
        pass

print("latest stocks data pulled")

# add new data in database
try:
   with create_connection_database(db_url).connect() as connection:
    table_name = "nifty_top_500_stocks"
    master_data.to_sql(table_name,create_connection_database(db_url),index=False,if_exists='append')
    print(f"{len(master_data)} rows successfully added in {table_name}")
except Exception as e:
    print(f"Error: {e}")