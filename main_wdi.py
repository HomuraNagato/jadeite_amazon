#!/usr/bin/env python3

from flask import Flask, render_template,request
import plotly
import plotly.graph_objs as go
import plotly.express as px

import pandas as pd
import numpy as np
import json

from programs.gran_command import *

server = Flask(__name__)

def create_bar(df, x_axis, y_axis, filter_axis, filter_value):

    
    #print("indicators", df['indicator_name'].unique())
    df = df[df[filter_axis] == filter_value]
    df = df[df['year'] == 2015]
    
    data = [
        go.Bar(
            x=df[x_axis], 
            y=df[y_axis]
        )
    ]
    
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def create_scatter(df, x_axis, y_axis, text_axis, color_axis):

    fig = go.Figure()

    df = df[df[color_axis] == 2015]
    
    data = [
        go.Scatter(
            x=df[x_axis], 
            y=df[y_axis],
            mode='markers',
            name='markers',
            text=df[text_axis]
        )
    ]

    layout = go.Layout(
        title = 'Scatter Relationship',
        yaxis = {'title': y_axis},
        xaxis = {'title': x_axis}
    )

    fig = dict(data=data, layout=layout)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def create_table(df, x_axis, y_axis, text_axis, color_axis):

    fig = go.Figure()

    data = [
        go.Table(
            header=dict(values= [text_axis, color_axis, x_axis, y_axis],
                    fill_color= 'paleturquoise',
                    align= 'left'),
            cells=dict(values= [df[text_axis], df[color_axis], df[x_axis], df[y_axis]],
                    fill_color= 'lavender',
                    align= 'left'),
            )
        ]

    layout = go.Layout(
        title = 'table'
    )
    
    fig = dict(data=data, layout=layout)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

@server.route('/')
def index():

    # load data
    #df = world_indicator_data()
    S2 = pd.read_csv('data/filtered_wdi.csv')

    # create bar chart
    x, y = 'country_name', 'value' 
    filter_axis, filter_value = 'indicator_name', 'Current health expenditure per capita, PPP (current international $)'
    bar = create_bar(S2, x, y, filter_axis, filter_value)

    # create scatter plot
    text_axis, color_axis = 'country_name', 'year'
    x_axis, y_axis = 'Birth rate, crude (per 1,000 people)', 'Death rate, crude (per 1,000 people)'
    index = ['country_name', 'year', 'indicator_name']
    axes = [x_axis, y_axis]
    S2_scatter = pivot_data(S2, index, axes)
    scatter = create_scatter(S2_scatter, x_axis, y_axis, text_axis, color_axis)

    # create table
    table = create_table(S2_scatter, x_axis, y_axis, text_axis, color_axis)
    
    return render_template('index.html', bar=bar, scatter=scatter, table=table)


@server.route('/bar', methods=['GET', 'POST'])
def change_features():

    S2 = pd.read_csv('data/filtered_wdi.csv')
    text_axis, color_axis = 'country_name', 'year'
    #x_axis, y_axis = 'Birth rate, crude (per 1,000 people)', 'Death rate, crude (per 1,000 people)'
    index = ['country_name', 'year', 'indicator_name']
    x_axis = request.args['selected-x']
    y_axis = request.args['selected-y']
    axes = [x_axis, y_axis]
    S2_scatter = pivot_data(S2, index, axes)
    graphJSON= create_scatter(S2_scatter, x_axis, y_axis, text_axis, color_axis)

    return graphJSON



if __name__ == '__main__':
    server.run(debug=True)
