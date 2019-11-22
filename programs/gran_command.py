
"""Create a Dash app within a Flask app."""
import glob
from pathlib import Path
#from dash import Dash
#import dash_table
#import dash_html_components as html
import pandas as pd
import numpy as np

import plotly
import plotly.graph_objs as go
import numpy as np
import pandas as pd
import json


def world_indicator_data():
    '''
    Data gathered from
    https://datacatalog.worldbank.org/dataset/world-development-indicators
    '''

    S2 = pd.read_csv('data/WDIData.csv').dropna(how='all', axis=1)
    S2.columns = [ col.lower().replace(' ', '_') for col in S2.columns ]

    id_cols = [ col for col in S2.columns if col in ['country_name', 'country_code', 'indicator_name', 'indicator_code'] ]
    val_cols = [ col for col in S2.columns if col not in id_cols ]
    S2 = pd.melt(S2, id_vars = id_cols, value_vars = val_cols,
                 var_name = 'year', value_name = 'value')

    # remove rows with no data and standarize column names
    S2 = S2.dropna(subset=['value'])

    filtered_indicators = ['Access to electricity (% of population)', 'Adjusted net enrollment rate, primary (% of primary school age children)',
                           'Adjusted net national income per capita (current US$)', 'Adolescent fertility rate (births per 1,000 women ages 15-19)',
                           'Alternative and nuclear energy (% of total energy use)', 'Birth rate, crude (per 1,000 people)',
                           'Central government debt, total (% of GDP)', 'Children in employment, total (% of children ages 7-14)',
                           'CO2 emissions (kg per PPP $ of GDP)', 'Consumer price index (2010 = 100)',
                           'Cost of business start-up procedures (% of GNI per capita)', 'Current account balance (% of GDP)',
                           'Current education expenditure, total (% of total expenditure in public institutions)', 'Current health expenditure per capita, PPP (current international $)',
                           'Death rate, crude (per 1,000 people)']
    S2 = S2[S2['indicator_name'].isin(filtered_indicators)]

    # temp filters to test choropleth
    #S2 = S2[S2['indicator_name'] == 'Current health expenditure per capita, PPP (current international $)']
    #S2 = S2[S2['year'] == '2015']
    
    return S2

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +
        #body
        [html.Tr([html.Td(dataframe.iloc[i][col]) for col in dataframe.columns])
         for i in range(min(len(dataframe), max_rows))]
    )

def get_datasets():
    """Return previews of all CSVs saved in /data directory."""
    S2_wdi = world_indicator_data()
    html.H4(children='WDI'),
    generate_table(S2_wdi),
    return arr


def pivot_data(S2, index, axes):

    # filter columns for viewing and pivoting
    # clean index and levels
    necessary_cols = index + ['value']
    S2 = S2.filter(items=necessary_cols)
    S2 = S2[S2['indicator_name'].isin(axes)]
    S2 = S2.set_index(index).unstack(level=-1)
    S2.columns = S2.columns.droplevel()
    S2 = S2.reset_index()
    #print(S2.tail())
    #print(S2.columns)

    return S2

if __name__ == '__main__':

    #S2 = world_indicator_data()
    #S2.to_csv('filtered_wdi.csv', encoding='utf-8', index=False)
    S2 = pd.read_csv('filtered_wdi.csv')

    df = S2.copy()
    
    index_arr = ['country_name', 'year', 'indicator_name']
    x, y = 'Birth rate, crude (per 1,000 people)', 'Death rate, crude (per 1,000 people)'
    axes = [x, y]
    pivot_data(df, index_arr, axes)
