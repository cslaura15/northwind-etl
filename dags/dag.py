from airflow.decorators import dag, task
from datetime import datetime
import sqlite3
import pandas as pd
from sqlalchemy import create_engine
import os

@dag(schedule=None, start_date=datetime(2024, 1, 1), catchup=False, tags=["etl"])
def northwind_etl():

    @task
    def extract():
        conn = sqlite3.connect(os.environ["SQLITE_SRC_PATH"])
        df = pd.read_sql("SELECT * FROM customers", conn)
        conn.close()
        return df.to_json()

    @task
    def transform(data_json):
        df = pd.read_json(data_json)
        # transformation logic here
        return df.to_json()

    @task
    def load(data_json):
        df = pd.read_json(data_json)
        engine = create_engine(os.environ["POSTGRES_DEST_CONN"])
        df.to_sql("customers", engine, if_exists="replace", index=False)

    load(transform(extract()))

northwind_etl()