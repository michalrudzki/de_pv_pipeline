import pandas as pd
from numpy import array_split
import psycopg2
import csv
from psycopg2.extras import Json
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Delete
from sqlalchemy.engine.url import URL
from sqlalchemy import text 

file_date = '2026-08-10'
insert_date = datetime.fromisoformat(f'{file_date} 00:00:00.0')

conn_params: dict[str, str | int] = {
    "host": "localhost",
    "port": 5432,
    "dbname": "postgres",
    "user": "postgres",
    "password": "mysecret"
}

def connect():
    connection= psycopg2.connect(**conn_params)
    return connection

def execute(sql,params={}):
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql,params)

def fastInsert_PV(data_l, file_date):
    '''
        One connection, one query.
    '''
    insert_date = datetime.fromisoformat(f'{file_date} 00:00:00.0')
    cleanup_sql = """
        delete from pv_production
        where eff_date = %(insert_date)s
    """

    execute(cleanup_sql, locals())

    sql='''
        INSERT INTO pv_production(id_inst,current_power_W,daily_kWh,monthly_kWh,yearly_kWh,Total_MWh,eff_date)
            SELECT unnest( %(id_inst)s ) ,
                    unnest( %(current_power_W)s),
                    unnest( %(daily_kWh)s),
                    unnest( %(monthly_kWh)s),
                    unnest( %(yearly_kWh)s),
                    unnest( %(Total_MWh)s),
                    unnest( %(eff_date)s)

    '''

    id_inst=[int(r['idinst']) for r in data_l]
    current_power_W=[float(r['Moc bieżąca W']) for r in data_l]
    daily_kWh=[float(r['Dzień kWh']) for r in data_l]
    monthly_kWh=[float(r['Dzień kWh']) for r in data_l]
    yearly_kWh=[float(r['Dzień kWh']) for r in data_l]
    Total_MWh=[float(r['Dzień kWh']) for r in data_l]
    eff_date=[datetime.fromisoformat(f'{file_date} 00:00:00.0') for r in data_l]
    execute(sql,locals())

# Load PV data
def get_pv_data_from_csv(file_date):
    pv_data_l=list()
    with open(f'data/pv_production{file_date}.csv', mode='r') as infile:
        reader = csv.reader(infile)
        keys=[]
        
        for i,row in enumerate(reader):
            if i==0:
                keys=row
                continue
            row_dict={}
            for j, value in enumerate(row):
                row_dict[keys[j]] = value
            pv_data_l.append(row_dict)
    return pv_data_l

data_l= get_pv_data_from_csv(file_date)

fastInsert_PV(data_l, file_date)

# Load Meteo
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
    meteo_data = pd.read_pickle(f"data/meteo_{table_type}_{meteo_city}_{file_date}.pkl")
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
