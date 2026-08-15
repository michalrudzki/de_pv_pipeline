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

conn_params: dict[str, str | int] = {
    "host": "postgres18",
    "port": 5432,
    "dbname": "postgres",
    "user": "postgres",
    "password": "mysecret"
}

# check missing dates in silver that exists in bronze - our steering table will be pv_production data, We will align dates with it
