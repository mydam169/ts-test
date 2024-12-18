#  data importing and cleaning
import sqlite3
import pandas as pd 
from datetime import timedelta

def load_data(dbName, tbName, ParisTime=True, hourly=True):
    conn = sqlite3.connect(dbName)
    select_query = f'SELECT * FROM {tbName}'
    df = pd.read_sql_query(select_query, conn, index_col='datetime')
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    conn.close()
    if ParisTime:
        df.index = df.index + timedelta(hours=1)
    if hourly:
        "Remove incorrect 30-min mark data values"
        correct_time_idx = df.index.minute == 0
        df = df[correct_time_idx]
    return df 
