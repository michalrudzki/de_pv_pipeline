import pandas
from numpy import array_split
import psycopg2
from psycopg2.extras import Json
import time
import contextlib

@contextlib.contextmanager
def timer(name="duration"):
    'Utility function for timing execution'
    start=time.time()
    yield
    duration=time.time()-start
    print("{0}: {1} second(s)".format(name,duration))

# Parametry połączenia

conn_params: dict[str, str | int] = {
    "host": "localhost",
    "port": 5432,
    "dbname": "postgres",
    "user": "postgres",
    "password": "mysecret"
}

'''
try:
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"Połączono z PostgreSQL:\n{version[0]}")
except psycopg2.OperationalError as e:
    print(f"Błąd połączenia: {e}")
finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()
'''
# I will create database objects by DBeaver application connected to postgres18 container
# DDL will be placed in assets folder

# 'insert into table values ({})'.format(', '.join('%s' for s in range(22)))

#,properties hstore not null default ''::hstore

SETUP_SQL="""
    DROP TABLE IF EXISTS upload_time_test;

    CREATE TABLE upload_time_test(
        uuid BIGSERIAL PRIMARY KEY,
        created timestamp with time zone not null default now(),
        text text not null,
        properties VARCHAR(50)
    );

    GRANT ALL ON upload_time_test TO postgres;
"""

SINGLE_INSERT="""
    INSERT INTO upload_time_test(text,properties)
         VALUES (%(text)s, %(properties)s)
"""

def connect():
    connection= psycopg2.connect(**conn_params)
    #psycopg2.extras.register_hstore(connection)
    return connection

def execute(sql,params={}):
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql,params)

class Tester():
    def __init__(self,count):
        execute(SETUP_SQL)
        self.count=count
        #print(self.count)

        self.data=[
            {
                'text':'Some text',
                'properties': "value",
            }
            for i in range(count)
        ]
        
    def slowInsert(self):
        '''
            Creates a new connection for each insertion
        '''
        for row in self.data:
            text=row['text']
            properties=row['properties']
            execute(SINGLE_INSERT,locals())
            
    def insert(self):
        '''
            One connection.
            Multiple queries.
        '''
        with connect() as connection:
            with connection.cursor() as cursor:
                for row in self.data:
                    text=row['text']
                    properties=row['properties']
                    cursor.execute(SINGLE_INSERT,locals())

    def fastInsert(self):
        '''
            One connection, one query.
        '''
        sql='''
            INSERT INTO upload_time_test(text,properties)
              SELECT unnest( %(texts)s ) ,
                     unnest( %(properties)s)

        '''

        texts=[r['text'] for r in self.data]
        properties=[r['properties'] for r in self.data]
        execute(sql,locals())

def runTests(iterations):
    tester = Tester(iterations)
    with timer('slow'):
        tester.slowInsert()
    with timer('normal'):
        tester.insert()
    with timer('fast'):
        tester.fastInsert()

#runTests(1000)