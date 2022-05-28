import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from plotly.subplots import make_subplots

class Dashboard:

    def __init__(self) -> None:
        self.transactions = pd.read_csv('./mock/mock_transactions.csv')
        self.transactions['TIMESTAMP'] = pd.to_datetime(self.transactions['TIMESTAMP'])
        self.data = pd.read_csv('./mock/BTCEUR_12h_INTERVAL.csv')
        self.data['Time'] = pd.to_datetime(self.data['Time'])
        st.set_page_config(layout="wide")

    def get_plotly_figures(self, transaction_df):
        return px.line(transaction_df, x="TIMESTAMP", y="ACCUMULATED_INVESTMENT", color="MODEL", title='Accumulated investment per Model')

    def get_plotly_figures_double(self, transaction_df):
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig.add_trace(
            go.Scatter(x=self.data['Time'].values.tolist(), y=self.data['Close'].values.tolist(), name="BTC/EUR"),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=transaction_df['TIMESTAMP'].values.tolist(), y=transaction_df.query('ORDER_TYPE=="SELL"')['ACCUMULATED_INVESTMENT'].values.tolist(), name="Acc. Investment"),
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

    def run(self):
        transaction_df = self.transactions
        
        model_choices = ['All'] + transaction_df['MODEL'].unique().tolist()
        #model_choice= st.sidebar.selectbox('Select your vehicle:', model_choices)

        data_min_date = self.data['Time'].min()
        data_max_date = self.data['Time'].max()

        
        with st.sidebar:
            model_choice= st.sidebar.selectbox('Select your vehicle:', model_choices)
            from_date = st.date_input(label="Start Date", value=data_min_date, min_value=data_min_date, max_value=data_max_date)
            to_date = st.date_input(label="End Date", value=data_max_date, min_value=data_min_date, max_value=data_max_date)

        if model_choice != 'All':
            transaction_df = transaction_df[transaction_df['MODEL']==model_choice]

        transaction_df = transaction_df.query("TIMESTAMP >= @from_date & TIMESTAMP <= @to_date")
        self.data = self.data.query("Time >= @from_date & Time <= @to_date")

        self.data['Time'] = self.data['Time'].dt.strftime('%Y-%m-%d %H:%M')
        transaction_df['TIMESTAMP'] = transaction_df['TIMESTAMP'].dt.strftime('%Y-%m-%d %H:%M')
        print(transaction_df.shape)

        figure = self.get_plotly_figures_double(transaction_df)
        st.plotly_chart(figure, use_container_width=False)
            
        st.dataframe(transaction_df)


if __name__=='__main__':
    app = Dashboard()
    app.run()