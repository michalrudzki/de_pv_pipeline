import pandas as pd
from numpy import array_split
import psycopg2
import csv
from psycopg2.extras import Json
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Delete
from sqlalchemy.engine.url import URL
from sqlalchemy import text 
from os import walk

file_date = '2026-08-11'
insert_date = datetime.fromisoformat(f'{file_date} 00:00:00.0')

config = dict(
    drivername='postgresql',
    username='postgres',
    password='mysecret',
    host='postgres18',
    port='5432',
    database='postgres'
)

url = URL.create(**config)
print(url)
engine = create_engine(url, echo=True)

def insert_meteo(table_type, meteo_city, file_date):
    insert_date = datetime.fromisoformat(f'{file_date} 00:00:00.0')
    meteo_data = pd.read_pickle(f"data/meteo/{table_type}/meteo_{table_type}_{meteo_city}_{file_date}.pkl")
    meteo_data['city'] = meteo_city
    meteo_data['file_date'] = pd.Timestamp(file_date)
    meteo_data.rename(columns={'date': 'forecst_datetime'}, inplace=True)
    table_name = f'bronze_meteo_forcast_{table_type}'

    delete_sql = """
        DELETE FROM bronze_meteo_forcast_{}
        WHERE file_date = :file_date and city = :meteo_city
    """.format(table_type)
 
    with engine.connect() as con:
        result = con.execute(
            text(delete_sql),
            {"file_date": insert_date, "meteo_city": meteo_city}
        )

        con.commit()

    meteo_data.to_sql(table_name, engine, if_exists="append", index=False)

# List dates to be loaded
meteo_type = 'daily'
meteo_city = 'Krakow'

filenames = next(walk(f'data/meteo/{meteo_type}'), (None, None, []))[2] 
dates_to_load = list(map(lambda x: x.split('.')[0][-10:],  filenames))

loaded_dates=[]
with open("data/loaded_meteo.csv", newline='') as myFile:
    csvReader = csv.reader(myFile)
    
    # Loop through each row in the CSV file
    for row in csvReader:
        loaded_dates.append(row[0]) 

dates_to_load = {x for x in dates_to_load if x not in loaded_dates and len(x) > 0}

for file_date in dates_to_load:
    insert_date = datetime.fromisoformat(f'{file_date} 00:00:00.0')

    insert_meteo('daily', 'Szczecin', file_date)
    insert_meteo('daily', 'Warszawa', file_date)
    insert_meteo('daily', 'Krakow', file_date)
    insert_meteo('hourly', 'Szczecin', file_date)
    insert_meteo('hourly', 'Warszawa', file_date)
    insert_meteo('hourly', 'Krakow', file_date)
  
    with open("data/loaded_meteo.csv", 'a') as csvfile:
        csvfile.write('\n')
        csvfile.write(file_date)

