# import libraries
import pandas as pd
import numpy as np

equity_list_nse = pd.read_csv("EQUITY_L.csv")
symbol_list = equity_list_nse['SYMBOL'].head(50).to_list()
symbol_list