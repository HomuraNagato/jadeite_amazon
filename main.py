#!/usr/bin/env python3

from flask import Flask, render_template,request
import plotly
import plotly.graph_objs as go
import plotly.express as px

import pandas as pd
import numpy as np
import json

from programs.gran_command import *
from programs.jadeite_sellers import *

server = Flask(__name__)

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

def create_table(df, columns):

    fig = go.Figure()

    data = [
        go.Table(
            header=dict(values= columns,
                    fill_color= 'paleturquoise',
                    align= 'left'),
            cells=dict(values= [ df[x] for x in columns ],
                    fill_color= 'lavender',
                    align= 'left'),
            )
        ]

    layout = go.Layout(
        title = 'Amazon Sellers List',
        width = 900,
        #margin = { 'l': 20, 'r': 20, 't': 20, 'b': 20, 'pad': 10 },
        autosize = True
    )
    
    fig = dict(data=data, layout=layout)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

@server.route('/')
def index():

    # create scatter plot
    artifact = Amazon(action="clear")
    S2 = artifact.view_database()
    columns = S2.columns
    
    # create table
    table = create_table(S2, columns)
    
    return render_template('index.html', table=table)



@server.route('/table', methods=['GET', 'POST'])
def filter_table():

    # get environmental variables
    asin = request.args['asin']
    action = request.args['action']
    print("entered filter table in main")
    artifact = Amazon(asin=asin, action=action)
    
    if action == "add":
        try:
            asin_request(artifact)
            print("asin", asin, "added to database")
        except:
            print("Unable to collect asin", asin, "from Amazon")

    elif action == "delete":
        try:
            artifact.delete_sql()
        except:
            print("Unable to delete asin", asin, "from postgres database")
    
    S2 = artifact.view_database()
    columns = S2.columns
    
    if action == "filter":
        S2 = S2[S2['asin'] == asin]

    graphJSON = create_table(S2, columns)

    return graphJSON



if __name__ == '__main__':
    server.run(debug=True)
