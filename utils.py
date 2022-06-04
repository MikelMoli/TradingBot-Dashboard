
from datetime import timedelta
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
            print(model,':', df.shape)
            df['MODEL'] = model
            data = pd.concat([data, df], axis=0, ignore_index=True)
    
    print('RETRIEVE-DATA:', data.shape)
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


def get_bound_graph(dataframe, transaction_df):

    df_buys = transaction_df.query('ORDER_TYPE=="Buy"')
    df_sells = transaction_df.query('ORDER_TYPE=="Sell"')

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
            ),

        # AÑADIR UN SCATTER DE BUY Y OTRO DE SELLS
        go.Scatter(
            mode='markers',
            x=df_buys['TIMESTAMP'],
            y=df_buys['BUY_PRICE'],
            marker=dict(
                color='chartreuse',
                size=10,
                line=dict(
                    color='MediumPurple',
                    width=1
                ),
                symbol='arrow-bar-right'
            ),
            name = 'Buy',
            showlegend=False
        ),
        go.Scatter(
            mode='markers',
            x=df_sells['TIMESTAMP'],
            y=df_sells['SELL_PRICE'],
            marker=dict(
                color='crimson',
                size=10,
                line=dict(
                    color='MediumPurple',
                    width=1
                ),
                symbol='arrow-bar-left'
            ),
            name = 'Sell',
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

def transform_app2_data(data, transaction_df, model, from_date, to_date):

    if model != 'All':
        data = data.query('Model==@model')
        transaction_df = transaction_df.query('MODEL==@model')
    
    data['Time'] = pd.to_datetime(data['Time'])
    transaction_df['TIMESTAMP'] = pd.to_datetime(transaction_df['TIMESTAMP'])
    transaction_df['TIMESTAMP'] = transaction_df['TIMESTAMP'].apply(lambda x: x - timedelta(hours=2))

    transaction_df = transaction_df.query("TIMESTAMP >= @from_date & TIMESTAMP <= @to_date")
    data = data.query("Time >= @from_date & Time <= @to_date")
    
    data['Time'] = data['Time'].dt.strftime('%Y-%m-%d %H:%M')
    transaction_df['TIMESTAMP'] = transaction_df['TIMESTAMP'].dt.strftime('%Y-%m-%d %H:%M')

    return data, transaction_df
