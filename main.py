# 1. Get data into shape
import argparse,datetime,os,sys,time

try:
    import plotly.graph_objects as go
except:
    go = None  

if go is None:
    print("plotly is not installed")

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from ipywidgets import widgets

from tools import load_groupfile, query_api, filterIQM, merge_dfs, chart, make_vio_plot, make_vio_plot_df

import ipywidgets as widgets
from ipywidgets import interact, interact_manual

filter_list= ['TR > 1.9', 'TR < 3'] #whatcha
 
# here = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
here = os.getcwd()

group_file = os.path.join(here, 'data', 'all_before_bold.tsv')

# scan type to query the API for [bold, T1w, T2w]
modality = 'bold'
#modality = 'T1w'


# IQM variables to visualize
#need to add separate IQMs for structural and functional
IQM_to_plot = ['fd_mean','fd_num','fd_perc']

userdf = load_groupfile(group_file)

T1apicsv = os.path.join(here, 'data', 'T1w_demo.csv')
T2apicsv = os.path.join(here, 'data', 'T2w_demo.csv')
boldapicsv = os.path.join(here, 'data', 'bold_demo.csv')

if modality == 'T1w':
    api_file = T1apicsv
elif modality == 'T2w':
    api_file = T1apicsv
elif modality == 'bold':
    api_file = boldapicsv

apidf = pd.read_csv(api_file)
if not filter_list == []:
    filtered_apidf = filterIQM(apidf,filter_list)
else:
    filtered_apidf = apidf

vis_ready_df = merge_dfs(userdf.copy(), filtered_apidf.copy())



#2. create dash app

import pandas as pd

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px


app = dash.Dash(__name__)


fig = chart(vis_ready_df, 'fd_mean', "Average Framewise Displacement")
thisdict = {'fd_num': "Number of timepoints above the threshold", 'fd_mean': "Average Framewise Displacement", 'fd_perc': "Percent of Framewise Displacement above the threshold"}

#---------------------------------------------------------------
app.layout = html.Div([
    html.Div([
        html.Label(['Image quality metrics for functional MRI']),
        dcc.Dropdown(
            id='my_dropdown',
            options=[
                     {'label': thisdict['fd_num'], 'value': 'fd_num'},
                     {'label': thisdict['fd_mean'], 'value': 'fd_mean'},
                     {'label': thisdict['fd_perc'], 'value': 'fd_perc'}
            ],
            value='fd_mean',
            multi=False,
            style={"width": "50%"}
        ),
    ]),

    html.Div([
        dcc.Graph(id='the_graph', figure=fig, config={'displayModeBar': False}, style={'width': '90vh', 'height': '90vh'}) 
    ]),

])

#---------------------------------------------------------------
@app.callback(
    Output(component_id='the_graph', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value')]
)



def update_graph(my_dropdown):

    fig = chart(vis_ready_df, my_dropdown, thisdict[my_dropdown])

    return (fig)

if __name__ == '__main__':
    app.run_server(port=8049)