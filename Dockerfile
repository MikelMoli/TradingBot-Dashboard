FROM python:3.9

WORKDIR /app

#VOLUME . /home/pi/Desktop/TradingBot-Dashboard

#COPY requirements.txt ./requirements.txt

#RUN pip install -r requirements.txt

EXPOSE 8501

COPY . ./app

# ENTRYPOINT ["streamlit", "run"]

CMD [". venv/bin/activate && cd app && streamlit run app.py"]
