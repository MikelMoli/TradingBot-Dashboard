from datetime import timedelta
from pyexpat import model
import streamlit as st
import pandas as pd
import hydralit as hy

import plotly.express as px
import plotly.graph_objects as go

from plotly.subplots import make_subplots
import utils

MOCK = False

pd.set_option('mode.chained_assignment', None)

def read_data():
    transactions = utils.retrieve_data(MOCK)
    transactions['TIMESTAMP'] = pd.to_datetime(transactions['TIMESTAMP'])
    data = pd.read_csv(f'./data/BTCEUR_12h_INTERVAL.csv')
    data['Time'] = pd.to_datetime(data['Time'])
    data.rename(columns={ data.columns[1]: "Close" }, inplace = True)
    return data, transactions

def get_plotly_figures(transaction_df):
    return px.line(transaction_df, x="TIMESTAMP", y="ACCUMULATED_INVESTMENT", color="MODEL", title='Accumulated investment per Model')

def get_plotly_figures_double(data, transaction_df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=data['Time'].values.tolist(), y=data['Close'].values.tolist(), name="BTC/EUR"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=transaction_df['TIMESTAMP'].values.tolist(), y=transaction_df.query('ORDER_TYPE=="Sell"')['ACCUMULATED_INVESTMENT'].values.tolist(), name="Acc. Investment"),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(
        title_text="Accumulated Investment vs. Price"
    )

    # Set x-axis title
    fig.update_xaxes(title_text="Date")

    # Set y-axes titles
    fig.update_yaxes(title_text="<b>BTC/EUR price</b>", secondary_y=False)
    fig.update_yaxes(title_text="<b>Acc. investment</b>", secondary_y=True)

    fig.update_layout(
        autosize=False,
        width=1200,
        height=600,)

    return fig

    
def transform_data(model_choice, from_date, to_date, data, transaction_df):
    if model_choice != 'All':
        transaction_df = transaction_df[transaction_df['MODEL']==model_choice]

    transaction_df = transaction_df.query("TIMESTAMP >= @from_date & TIMESTAMP <= @to_date")
    data = data.query("Time >= @from_date & Time <= @to_date")
    data['Time'] = data['Time'].dt.strftime('%Y-%m-%d %H:%M')
    transaction_df['TIMESTAMP'] = transaction_df['TIMESTAMP'].dt.strftime('%Y-%m-%d %H:%M')
    return data, transaction_df

if __name__=='__main__':
    app = hy.HydraApp(title='Trading Bot')

    @app.addapp(is_home=True, title='General')
    def my_home():
        c1 = hy.container()
        col1, col2, col3 = hy.columns(3)
        
        c2 = hy.container()
        col4, col5, col6, col7, col8 = hy.columns(5)
        

        data, transaction_df = read_data()

        data_min_date = data['Time'].min()
        data_max_date = data['Time'].max()

        filter_min_date = data_max_date - timedelta(days=30)
        filter_max_date = data_max_date + timedelta(days=1)
        #with hy.sidebar:
        # model_choice= hy.selectbox('Select your vehicle:', model_choices)

        with c1:
            model_choice = col1.selectbox('Model:', utils.MODELS)
            from_date = col2.date_input(label="Start Date", value=filter_min_date, min_value=data_min_date, max_value=filter_max_date)
            to_date = col3.date_input(label="End Date", value=filter_max_date, min_value=data_min_date, max_value=filter_max_date)




        #from_date = hy.date_input(label="Start Date", value=data_min_date, min_value=data_min_date, max_value=data_max_date)
        #to_date = hy.date_input(label="End Date", value=data_max_date, min_value=data_min_date, max_value=data_max_date)

        data, transaction_df = transform_data(model_choice, from_date, to_date, data, transaction_df)

        buy_transactions_made = transaction_df.query('ORDER_TYPE == "Buy"').shape[0]
        sell_transactions_made = transaction_df.query('ORDER_TYPE == "Sell"').shape[0]
        won_transactions = transaction_df.query('ORDER_TYPE == "Sell" and BUY_PRICE < SELL_PRICE').shape[0]
        loss_transactions = transaction_df.query('ORDER_TYPE == "Sell" and BUY_PRICE > SELL_PRICE').shape[0]
        #accumulated_investment = transaction_df.query('ORDER_TYPE == "Sell"').loc[-1, "ACCUMULATED_INVESTMENT"]


        with c2:
            col4.metric("Buy Transactions", buy_transactions_made)
            col5.metric("Sell Transactions", sell_transactions_made)
            col6.metric("Won Transactions", won_transactions)
            col7.metric("Loss Transactions", loss_transactions)
            #col8.metric("Accumulated Investment", accumulated_investment)

        figure = get_plotly_figures_double(data, transaction_df)

        hy.plotly_chart(figure, use_container_width=True)

        hy.dataframe(transaction_df)
        

    @app.addapp(title='Intervals & Company')
    def app2():
        c1 = hy.container()
        col1, col2, col3 = hy.columns(3)

        data, transaction_df = read_data()

        data_min_date = data['Time'].min()
        data_max_date = data['Time'].max()

        filter_min_date = data_max_date - timedelta(days=30)
        filter_max_date = data_max_date + timedelta(days=1)

        model_list = utils.MODELS.copy()
        model_list.remove('All')

        with c1:
            model_choice = col1.selectbox('Model:', model_list)
            from_date = col2.date_input(label="Start Date", value=filter_min_date, min_value=data_min_date, max_value=filter_max_date)
            to_date = col3.date_input(label="End Date", value=filter_max_date, min_value=data_min_date, max_value=filter_max_date)



        bounds_df = utils.get_bounds_df(data)
        bounds_df, transaction_df = utils.transform_app2_data(bounds_df, transaction_df, model_choice, from_date, to_date)
        # data, _ = transform_data(model_choice, from_date, to_date, data, transaction_df.copy())

        
        #figure = get_plotly_figures_double(data, transaction_df)
        fig_bounds = utils.get_bound_graph(bounds_df, transaction_df)
        hy.plotly_chart(fig_bounds, use_container_width=False)

        hy.dataframe(bounds_df)


    @app.addapp(title='The Best', icon="🥰")
    def app3():
        col1, col2, col3 = hy.columns(3)
        with col2:
            hy.image('./images/munger_buffet.jpg')
        hy.info('Estos dos viejos nos pueden comer los huevos, pero de momento somos nosotros los consumidores de su té de escroto.')

    #Run the whole lot, we get navbar, state management and app isolation, all with this tiny amount of work.
    app.run()
    
