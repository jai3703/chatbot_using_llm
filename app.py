from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

stocks_data = pd.read_excel("master_data_ta.xlsx")

app = Dash()

app.layout = [
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dcc.Dropdown(stocks_data.Symbol.unique(), id='dropdown-selection'),
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
