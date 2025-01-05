import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd

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
def read_table(table_name,db_url=db_url):
    try:
        with create_connection_database(db_url).connect() as connection:
            #table_name = table_name #"nifty_top_500_stocks"
            query = f"SELECT * from {table_name};"
            df = pd.read_sql_query(query, con=create_connection_database(db_url))
            print("data pulled from sql table")
    except Exception as e:
            print(f"Error: {e}")
    
    return df