# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 02:32:35 2024

@author: P282980
"""



import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd


urlFreq = "https://laimabaldina.com/nounplots/public/freqnouns.csv"
urlProp = "https://laimabaldina.com/nounplots/public/propnouns.csv"
urlRank = "https://laimabaldina.com/nounplots/public/ranknouns.csv"

freqnouns = pd.read_csv(open_url(urlFreq), header=[0,1,2], index_col=0)
propnouns = pd.read_csv(open_url(urlProp), header=[0,1,2], index_col=0)
ranknouns = pd.read_csv(open_url(urlRank), header=[0,1,2], index_col=0)

app = dash.Dash(__name__)

server = app.server

# Extracting subreddit and month options for dropdown menus
subreddit_options = [{'label': subr, 'value': subr} for subr in ['Conservative', 'Liberal', 'Republican', 'democrats', 'politics']]

app.layout = html.Div([
    dcc.Dropdown(
        id='subreddit-dropdown',
        options=subreddit_options,
        value='Conservative',  # Default value
        multi=True
    ),
    dcc.RadioItems(
        id='frequency-proportion-rank-toggle',
        options=[
            {'label': 'Frequency', 'value': 'freq'},
            {'label': 'Proportion', 'value': 'prop'},
            {'label': 'Rank', 'value': 'rank' }
        ],
        value='freq'  # Default value
    ),
    dcc.Input(
        id='word-input',
        type='text',
        placeholder='enter words to track',
        value=''  # Default value
    ),
    dcc.Graph(id='noun-visualization')
])

@app.callback(
    Output('noun-visualization', 'figure'),
    [Input('subreddit-dropdown', 'value'),
     Input('frequency-proportion-rank-toggle', 'value'),
     Input('word-input', 'value')]
)
def update_graph(selected_subreddits, data_type, input_words):
    # Split the input words by commas and strip whitespace
    words = [word.strip() for word in input_words.split(',') if word.strip()]
    
    if not isinstance(selected_subreddits, list):
        selected_subreddits = [selected_subreddits]
    
    # Choose the correct DataFrame based on the data_type
    if data_type == 'freq':
        df = freqnouns
    elif data_type == 'prop':
        df = propnouns
    else:  # This handles the 'rank' option
        df = ranknouns
        
    figure = go.Figure()

    # Generate a sorted list of all unique year-month combinations present in the DataFrame
    year_month_list = sorted(list(set([(year, month) for year, month, subreddit in df.columns])), key=lambda x: (x[0], x[1]))
    # Convert year-month tuples to a string format for display, e.g., '2020-01'
    x_axis_labels = [f'{year}-{str(month).zfill(2)}' for year, month in year_month_list]

    for word in words:
        if word in df.index:
            for subreddit in selected_subreddits:
                y_data = []
                for year, month in year_month_list:
                    if (year, month, subreddit) in df.columns:
                        y_data.append(df.loc[word, (year, month, subreddit)])
                    else:
                        y_data.append(0)  # Append 0 for missing data points
                
                # Adding word to the trace name for clarity
                trace_name = f'{word} in {subreddit}'
                figure.add_trace(go.Scatter(x=x_axis_labels, y=y_data, mode='lines+markers', name=trace_name))
        else:
            figure.add_annotation(text=f'{word} not found', xref="paper", yref="paper",
                                  x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="red"))

    
    figure.update_layout(
        title='Words Across Subreddits Over Time (use lowercase and separate with commas while searching)',
        xaxis={
        'title': 'Time (Year-Month)',
        'type': 'category',
        'categoryorder': 'array',
        'categoryarray': x_axis_labels
        },
        yaxis={
            'title': 'Rank' if data_type == 'rank' else ('Frequency' if data_type == 'freq' else 'Proportion'),
            'autorange': 'reversed' if data_type == 'rank' else True  # Reverse Y-axis for 'rank'
        },
        legend_title='Word in Subreddit',
        xaxis_tickangle=-45  # Improve label readability
    )
    
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)