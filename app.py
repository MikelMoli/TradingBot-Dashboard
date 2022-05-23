import streamlit as st
import pandas as pd
import plotly.express as px

class Dashboard:

    def __init__(self) -> None:
        self.transactions = pd.read_csv('./mock/mock_transactions.csv')
        self.data = pd.read_csv('./mock/BTCEUR_12h_INTERVAL.csv')

    def get_plotly_figures(self, transaction_df):
        return px.line(transaction_df, x="TIMESTAMP", y="ACCUMULATED_INVESTMENT", color="MODEL", title='Accumulated investment per Model')

    def run(self):
        transaction_df = self.transactions

        model_choices = ['All'] + transaction_df['MODEL'].unique().tolist()
        model_choice= st.sidebar.selectbox('Select your vehicle:', model_choices)

        if model_choice != 'All':
            transaction_df = transaction_df[transaction_df['MODEL']==model_choice]

        figure = self.get_plotly_figures(transaction_df)
        st.plotly_chart(figure, use_container_width=True)
        st.write(transaction_df)


if __name__=='__main__':
    app = Dashboard()
    app.run()