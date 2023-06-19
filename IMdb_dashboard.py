"""Importing the required libraries"""

from bs4 import BeautifulSoup
import requests
import numpy as np
import pandas as pd

# import plotly.offline as pyo
import plotly.graph_objs as go

import dash
from dash import dcc, html
from dash.dependencies import Input, Output


def replace_nan(data):
    """
    This function replaces empty or N/A values with np.nan so that it can be easier to manipulate the data later on.
    """
    for col in data.columns:
        data[col].replace(["N/A", "", " "], np.nan, inplace=True)

def data_cleaner(data):
    replace_nan(data)
    data.year = data.year.apply(lambda x: x.split("(")[1] if "(" in x else x)
    data.year = data.year.apply(lambda x : int(x))
    return data
"""Building the plotting functions"""
def year_agg(data, col, keyword):
    L = []
    if keyword == "Average":
        for x in range(20, 91, 10):
            L.append(data[(data.year >= 1900+x) & (data.year < 1910+x)][col].mean())
        L.append(data[(data.year >= 2000) & (data.year < 2010)][col].mean())
        L.append(data[data.year >= 2010][col].mean())
    elif keyword == "Minimum":
        for x in range(20, 91, 10):
            L.append(data[(data.year >= 1900+x) & (data.year < 1910+x)][col].min())
        L.append(data[(data.year >= 2000) & (data.year < 2010)][col].min())
        L.append(data[data.year >= 2010][col].min())
    elif keyword == "Maximum":
        for x in range(20, 91, 10):
            L.append(data[(data.year >= 1900+x) & (data.year < 1910+x)][col].max())
        L.append(data[(data.year >= 2000) & (data.year < 2010)][col].max())
        L.append(data[data.year >= 2010][col].max())
    return L

# ---------------------------------------------------------------------------

def plot_movies_score(data, keyword="Average"):
    labels = [str(x) + "s" for x in range(20, 91, 10)]
    labels.extend(["2000-2010", "2010+"])
    cols = ["rating", "m_score"]
    plot_data = []
    for col in cols:
        plot_data.append(go.Bar(x=labels, y=year_agg(data, col, keyword), name=col))
    layout = go.Layout(title=f"Movies {keyword} Scores by decades",
                       xaxis=dict(title="Decades"),
                       yaxis=dict(title="Scores"))
    fig = go.Figure(data=plot_data, layout=layout)
    return fig

def plot_topK_movies(data, k, sortedby="m_score", ascending = False):
    new = data.sort_values(by=sortedby, ascending = ascending)[:k]
    plot_data = []

    plot_data.append(go.Bar(x=new.name, y=new[sortedby], name=sortedby))

    layout = go.Layout(title=f"top {k} movies score by {sortedby}",
                       xaxis=dict(title="Movies"),
                       yaxis=dict(title=f"{sortedby}"))
    fig = go.Figure(data=plot_data, layout=layout)
    return fig

def plot_worstK_movies(data, k, sortedby="m_score"):
    return plot_topK_movies(data, k, sortedby=sortedby, ascending = True)


def init_figure():
    "This function initiate all the needed figure to start the app."
    return plot_movies_score(data), plot_topK_movies(data, 10), plot_worstK_movies(data, 10)



"""Initiale Figures"""
# ---------------------------------------------------------------------------
import os

here = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(here, "films.csv")
data = pd.read_csv(filename)
data = data_cleaner(data)


init_score_fig, init_topK_movies_plot, init_worstK_movies_plot = init_figure()




# Initializing the app
app = dash.Dash(__name__)
server = app.server

# Building the app layout
app.layout = html.Div([
    html.H1("150 top meta score movies DashBoard", style={"text-align": "center"}),
    html.Br(),
    html.Div([
        html.Br(),
        html.H2("Movies imdb scores by decade", style={"text-align": "center"}),
        html.Br(),
        dcc.Dropdown(id="select_keyword",
                     options=[
                         dict(label="Average score", value="Average"),
                         dict(label="Maximum score", value="Maximum"),
                         dict(label = "Minimum score", value="Minimum")],
                     multi=False,
                     value="Average",
                     style={"width": "40%"}
                     ),

        dcc.Graph(id="Movie_score", figure=init_score_fig)
    ]),

    html.Div([
        html.Br(),
        html.H2("Top k movies by score.", style={"text-align": "center"}),
        html.Br(),
        dcc.Dropdown(id="select_attribute",
                     options=[
                         dict(label="Meta score", value='m_score'),
                         dict(label="User rating", value='rating')],
                     multi=False,
                     value="m_score",
                     style={"width": "60%", 'display': 'inline-block'}
                     ),
        dcc.Dropdown(id="select_k_movies",
                     options=[
                         dict(label="Top 5", value=5),
                         dict(label="Top 10", value=10),
                         dict(label="Top 20", value=20),
                         dict(label="Top 30", value=30),
                     ],
                     multi=False,
                     value=10,
                     style={"width": "30%", 'display': 'inline-block'}
                     ),

        dcc.Graph(id="k_movies_sorted", figure=init_topK_movies_plot)
    ]),


    html.Div([
        html.Br(),
        html.H2("Worst k movies by score.", style={"text-align": "center"}),
        html.Br(),
                dcc.Dropdown(id="select_attribute_asc",
                     options=[
                         dict(label="Meta score", value='m_score'),
                         dict(label="User rating", value='rating')],
                     multi=False,
                     value="m_score",
                     style={"width": "60%", 'display': 'inline-block'}
                     ),
        dcc.Dropdown(id="select_k_movies_asc",
                     options=[
                         dict(label="Worst 5", value=5),
                         dict(label="Worst 10", value=10),
                         dict(label="Worst 20", value=20),
                         dict(label="Worst 30", value=30),
                     ],
                     multi=False,
                     value=10,
                     style={"width": "30%", 'display': 'inline-block'}
                     ),

        dcc.Graph(id="k_movies_asc_sorted", figure=init_worstK_movies_plot)
    ]),
])


# Defining the application callbacks

@app.callback(
    Output("Movie_score", "figure"),
    Input("select_keyword", "value")
)
def update_movies_bar(value):
    return plot_movies_score(data, keyword=value)


@app.callback(
    Output("k_movies_sorted", "figure"),
    Input("select_attribute", "value"),
    Input("select_k_movies", "value")
)
def update_k_movies_sorted(attribute, n_movies):
    return plot_topK_movies(data, n_movies, sortedby=attribute)

@app.callback(
    Output("k_movies_asc_sorted", "figure"),
    Input("select_attribute_asc", "value"),
    Input("select_k_movies_asc", "value")
)
def update_k_movies_asc_sorted(attribute, n_movies):
    return plot_worstK_movies(data, n_movies, sortedby=attribute)
if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(here, "films.csv")
    data = pd.read_csv(filename)
    data = data_cleaner(data)
    app.run_server()
