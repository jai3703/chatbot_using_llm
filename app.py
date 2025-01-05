#import libraries
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
# import archive.candlestick_patterns_v2 as cp
import dash_ag_grid as dag
import database_connection as db_con
import dash_bootstrap_components as dbc
import technical_analysis as ta

# Step 1 : Select a timeframe
stocks_data = db_con.read_table("nifty_top_500_stocks")

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
date_element = (
    dcc.DatePickerSingle(
            id="my-date-picker-single",
            min_date_allowed=stocks_data.DATE.min().date(),
            max_date_allowed = stocks_data.DATE.max().date(),
            date=stocks_data.DATE.max().date(),  # or string in the format "YYYY-MM-DD"
        )
        )
app.layout = dbc.Container(dcc.Loading([
    dbc.Row(
        html.H1(children='Nifty 500 Technical Analysis', style={'textAlign':'center'})
    ),
    html.Br(),
    dbc.Row(
        [
            dbc.Col([
                html.Label("Select a date for technical analysis"),
                html.Br(),
                date_element
                ],width=3),
            dbc.Col(
                [
                   dag.AgGrid(id='tbl',
                              dashGridOptions={'pagination':True}),
                    html.Label(id="cell_value")
                ],width=9
            )
        ]
    ),
    dbc.Row(
        dcc.Graph(id="candlesticks")
        )
    # dcc.Dropdown(nifty_top_500.Industry.unique(),value="All", id='dropdown-selection-sector'),
    # dcc.Dropdown( id='dropdown-selection',searchable=True),

]))


@callback(
    Output('tbl', 'rowData'),
    Output('tbl', 'columnDefs'),
    Input('my-date-picker-single', 'date')
)
def update_table(value):
    ta_analysis = ta.CandlestickAnalyser(stocks_data)
    ta_analysis.detect_all_patterns()
    data = ta_analysis.get_results()
    data = data.sort_values(by=['SYMBOL','DATE'])
    data_volume = data.groupby("SYMBOL").apply(lambda x: ta.volume_confirmation(10,x))
    selected_date_data = data_volume[data_volume.DATE==value]
    pattern_columns = ['bearish_marubuzo', 'doji', 'hammer', 'hanging_man', 'shooting_star']
    data_filtered = selected_date_data[selected_date_data[pattern_columns].any(axis=1) == True]
    data_selected_columns = data_filtered[['SYMBOL','Volume_Confirmed']+pattern_columns]
    melted = data_selected_columns.melt(id_vars=["SYMBOL","Volume_Confirmed"], var_name="Pattern", value_name="Detected")
    # Filter rows where Detected is True
    filtered = melted[melted["Detected"]]
    grouped = filtered.groupby(["SYMBOL","Volume_Confirmed"])["Pattern"].apply(list).reset_index()
    grouped.rename(columns={"Pattern": "Detected_Patterns"}, inplace=True)
    return grouped.to_dict('records'),[{"field": i, 'filter':True} for i in grouped.columns]

@callback(
    Output('candlesticks', 'figure'),
    Input('tbl', 'cellClicked'),
    Input('my-date-picker-single', 'date')
)
def update_graph(value,date):
    fig = go.Figure()
    try:
        stock_data_filtered = stocks_data[stocks_data.SYMBOL==value['value']]
        stock_data_filtered = stock_data_filtered.sort_values(by=['SYMBOL','DATE'])
        stock_data_filtered = ta.moving_average_crossover(stock_data_filtered, 'CLOSE', 25, 50)
        fig.add_trace(go.Candlestick(
            x=stock_data_filtered['DATE'],
            open=stock_data_filtered['OPEN'],
            high=stock_data_filtered['HIGH'],
            low=stock_data_filtered['LOW'],
            close=stock_data_filtered['CLOSE']
            ))

        # Add first line chart
        fig.add_trace(go.Scatter(
            x=stock_data_filtered['DATE'],
            y=stock_data_filtered['EMA_25'],
            mode='lines',
            name='EMA_25',
            line=dict(color='blue')
            ))

        # Add second line chart
        fig.add_trace(go.Scatter(
            x=stock_data_filtered['DATE'],
            y=stock_data_filtered['EMA_50'],
            mode='lines',
            name='EMA_50',
            line=dict(color='red')
        ))

        fig.add_vline(x=date, line_width=3, line_dash="dash", line_color="green")
        # Update layout for better visualization
        fig.update_layout(
            title=f'Candlestick Chart with Two Lines for {value['value']}',
            xaxis_title='Date',
            yaxis_title='Price',
            xaxis_rangeslider_visible=False  # Optionally disable range slider
        )
        return fig
    except:
        return fig
 



# def process_dataframe(df):
#     patterns = {
#         "Doji": [],
#         "Four Price Doji": [],
#         "Long Legged Doji": [],
#         "Gravestone Doji": [],
#         "Dragonfly Doji": [],
#         "Hammer": [],
#         "Hanging Man": [],
#         "Bullish Marubozu": [],
#         "Bearish Marubozu": [],
#     }

#     for _, row in df.iterrows():
#         candle = cp.SingleCandlePattern(row)
#         patterns["Doji"].append(candle.is_doji())
#         patterns["Four Price Doji"].append(candle.is_four_price_doji())
#         patterns["Long Legged Doji"].append(candle.is_long_legged_doji())
#         patterns["Gravestone Doji"].append(candle.is_gravestone_doji())
#         patterns["Dragonfly Doji"].append(candle.is_dragonfly_doji())
#         patterns["Hammer"].append(candle.is_hammer())
#         patterns["Hanging Man"].append(candle.is_hanging_man())
#         patterns["Bullish Marubozu"].append(candle.is_bullish_murubozu())
#         patterns["Bearish Marubozu"].append(candle.is_bearish_murubozu())

#     # Add results to the DataFrame
#     for pattern, results in patterns.items():
#         df[pattern] = results
    
#     single_candle_patterns_columns = ["Doji",
#         "Four Price Doji",
#         "Long Legged Doji",
#         "Gravestone Doji",
#         "Dragonfly Doji",
#         "Hammer",
#         "Hanging Man",
#         "Bullish Marubozu",
#         "Bearish Marubozu"]
#     df = df.sort_values(by=['SYMBOL','DATE'])
#     df['Single_Candlestick_pattern'] = df[single_candle_patterns_columns].any(axis=1)
#     df = volume_confirmation(10,df)
#     return df



# nifty_top_500 = pd.read_csv("ind_nifty500list.csv")






# @callback(
#     Output('dropdown-selection', 'options'),
#     Input('dropdown-selection-sector', 'value')
# )
# def update_graph(value):
#     dff = nifty_top_500[nifty_top_500.Industry==value]
#     return dff.Symbol.unique()




if __name__ == '__main__':
    app.run(debug=True)
