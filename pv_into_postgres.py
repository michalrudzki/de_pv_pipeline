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
    with open(f'data/pv/pv_production{file_date}.csv', mode='r') as infile:
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



filenames = next(walk('data/pv/'), (None, None, []))[2] 
print(filenames)
a = list(map(lambda x: x.split('pv_production')[1].split('.')[0],  filenames))

for a in a:
    print(a)

#data_l= get_pv_data_from_csv(file_date)
#fastInsert_PV(data_l, file_date)

