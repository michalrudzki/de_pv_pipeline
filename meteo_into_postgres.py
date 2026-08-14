import pandas as pd
from numpy import array_split
import psycopg2
import csv
from psycopg2.extras import Json
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Delete
from sqlalchemy.engine.url import URL
from sqlalchemy import text 

file_date = '2026-08-11'
insert_date = datetime.fromisoformat(f'{file_date} 00:00:00.0')

config = dict(
    drivername='postgresql',
    username='postgres',
    password='mysecret',
    host='localhost',
    port='5432',
    database='postgres'
)

url = URL.create(**config)
print(url)
engine = create_engine(url, echo=True)

def insert_meteo(table_type, meteo_city, file_date):
    insert_date = datetime.fromisoformat(f'{file_date} 00:00:00.0')
    meteo_data = pd.read_pickle(f"data/meteo/meteo_{table_type}_{meteo_city}_{file_date}.pkl")
    meteo_data['city'] = meteo_city
    meteo_data['file_date'] = pd.Timestamp(file_date)
    meteo_data.rename(columns={'date': 'forecst_datetime'}, inplace=True)
    table_name = f'meteo_forcast_{table_type}'

    delete_sql = """
        DELETE FROM meteo_forcast_{}
        WHERE file_date = :file_date and city = :meteo_city
    """.format(table_type)
 
    with engine.connect() as con:
        result = con.execute(
            text(delete_sql),
            {"file_date": insert_date, "meteo_city": meteo_city}
        )

        con.commit()

    meteo_data.to_sql(table_name, engine, if_exists="append", index=False)

insert_meteo('daily', 'Szczecin', file_date)
insert_meteo('daily', 'Warszawa', file_date)
insert_meteo('daily', 'Krakow', file_date)
insert_meteo('hourly', 'Szczecin', file_date)
insert_meteo('hourly', 'Warszawa', file_date)
insert_meteo('hourly', 'Krakow', file_date)
