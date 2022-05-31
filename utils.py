
import os
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go


### CONSTANTS ###
MODELS = ['All', 'LGBM', 'Linear']

### FUNCTIONS ###

def retrieve_data(mock):
    if mock:
        data = pd.read_csv('./mock/mock_transactions.csv')
    else:
        filenames = os.listdir('./data')
        filenames = [filename for filename in filenames if 'transactions' in filename]
        data = pd.DataFrame()
        for file in filenames:
            df = pd.read_csv(f'./data/{file}')
            model = file.split('_')[1].split('.')[0]
            df['MODEL'] = model
            data = pd.concat([data, df], axis=0, ignore_index=True)

    return data

def get_bounds_df(data):
    bounds_df = pd.DataFrame()
    for filename in os.listdir('./data'):
        if 'bounds' in filename:
            period = filename.split('_')[1]
            model = filename.split('_')[2]
            df = pd.read_csv(f'./data/{filename}')
            df['Model'] = model
            df['Period'] = period

            bounds_df = pd.concat([bounds_df, df], axis=0, ignore_index=True)

    bounds_df['ds'] = pd.to_datetime(bounds_df['ds'])
    data['Time'] = pd.to_datetime(data['Time'])

    data = data.merge(bounds_df, left_on='Time', right_on='ds', how='inner')

    data.drop(['ds'], axis=1, inplace=True)
    data.rename(columns={'yhat_lower': 'Lower_Bound', 'yhat_upper': 'Upper_Bound'}, inplace=True)
    
    return data.copy()


def get_bound_graph(dataframe):
    """    fig = go.Figure([
        go.Scatter(
            name='Measurement',
            x=dataframe['Time'],
            y=dataframe['10 Min Sampled Avg'],
            mode='lines',
            line=dict(color='rgb(31, 119, 180)'),
        ),
        go.Scatter(
            name='Upper Bound',
            x=dataframe['Time'],
            y=dataframe['10 Min Sampled Avg'],
            mode='lines',
            marker=dict(color="#444"),
            line=dict(width=0),
            showlegend=False
        ),
        go.Scatter(
            name='Lower Bound',
            x=dataframe['Time'],
            y=dataframe['10 Min Sampled Avg'],
            marker=dict(color="#444"),
            line=dict(width=0),
            mode='lines',
            fillcolor='rgba(68, 68, 68, 0.3)',
            fill='tonexty',
            showlegend=False
        )
    ])"""

    fig = go.Figure([

        go.Scatter(
            name='Close',
            x=dataframe['Time'],
            y=dataframe['Close'],
            mode='lines',
            line=dict(color='rgb(31, 119, 180)'),
            # fillcolor='rgba(68, 68, 68, 0.2)',
            # fill='toself'
            ),
        

        go.Scatter(
            name='Upper Bound',
            x=dataframe['Time'],
            y=dataframe['Upper_Bound'] ,
            mode='lines',
            marker=dict(color="#444"),
            line=dict(width=0.75, color="rgb(255, 188, 0)"),
            #fillcolor='rgba(68, 68, 68, 0.1)',
            # fill='tonexty'
            showlegend=False
            ),
        


        go.Scatter(
            name='Lower Bound',
            x=dataframe['Time'],
            y=dataframe['Lower_Bound'],
            marker=dict(color="#444"),
            line=dict(width=0.75, color="rgb(141, 196, 26)"),
            fillcolor='rgba(0, 191, 255, 0.25)',
            mode='lines',
            fill='tonexty',
            showlegend=False
            )
    ])


    # data = [lower_bound, upper_bound, trace1]



    # fig = go.Figure(data=data, layout=layout)
    fig.update_layout(autosize=False,
                      width=1500,
                      height=700,
                      title='Price',
                      hovermode='x',
                      plot_bgcolor='rgba(0,0,0,0.05)')
    return fig

def transform_bounds_data(data, model, from_date, to_date):
    if model != 'All':
        data = data.query('Model==@model')
    
    data['Time'] = pd.to_datetime(data['Time'])
    data = data.query("Time >= @from_date & Time <= @to_date")
    data['Time'] = data['Time'].dt.strftime('%Y-%m-%d %H:%M')

    return data
