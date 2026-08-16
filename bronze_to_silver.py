import psycopg2
from datetime import datetime

# when Running from docker set host: "postgres18", and from local as "localhost"
conn_params: dict[str, str | int] = {
    "host": "localhost",
    "port": 5432,
    "dbname": "postgres",
    "user": "postgres",
    "password": "mysecret"
}

# check missing dates in silver that exists in bronze - our steering table will be pv_production data, We will align dates with it
def connect():
    connection= psycopg2.connect(**conn_params)
    return connection

def execute(sql,params={}):
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql,params)

def bronze_to_silver(eff_date):
    '''
        One connection, one query.
    '''
    eff_datetime = datetime.fromisoformat(f'{eff_date} 00:00:00.0')
    end_datetime = datetime.fromisoformat(f'{eff_date} 23:59:59.0')
    cleanup_sql = """
        delete from silver_pv_production
        where eff_date = %(eff_datetime)s
    """
    execute(cleanup_sql, locals())
    cleanup_sql = """
            delete from silver_meteo_forcast_hourly
            where eff_date = %(eff_datetime)s
        """
    execute(cleanup_sql, locals())
    cleanup_sql = """
            delete from silver_meteo_forcast_daily
            where eff_date = %(eff_datetime)s
        """
    execute(cleanup_sql, locals())

    sql='''
        INSERT INTO silver_pv_production (id_inst,current_power_W,daily_kWh,monthly_kWh,yearly_kWh,Total_MWh,eff_date)
            SELECT id_inst,current_power_W,daily_kWh,monthly_kWh,yearly_kWh,Total_MWh,eff_date
            from bronze_pv_production
            where eff_date = %(eff_datetime)s
    '''
    execute(sql,locals())

    sql='''
            INSERT INTO silver_meteo_forcast_hourly (eff_date, city, forecst_datetime, cloud_cover, cloud_cover_low, cloud_cover_mid, cloud_cover_high, visibility,
                temperature_2m, relative_humidity_2m, dew_point_2m, rain, showers, snowfall, weather_code)
                SELECT %(eff_datetime)s, city, forecst_datetime, cloud_cover, cloud_cover_low, cloud_cover_mid, cloud_cover_high, visibility,
                    temperature_2m, relative_humidity_2m, dew_point_2m, rain, showers, snowfall, weather_code
                from bronze_meteo_forcast_hourly
                where file_date + INTERVAL '1 DAY' = %(eff_datetime)s
                and forecst_datetime >= %(eff_datetime)s and forecst_datetime <= %(end_datetime)s
        '''
    execute(sql,locals())
   
    sql='''
            INSERT INTO silver_meteo_forcast_daily (eff_date, city, forecst_datetime, sunrise, sunset, daylight_duration, sunshine_duration, weather_code, uv_index_max, 
                    uv_index_clear_sky_max, rain_sum, showers_sum, snowfall_sum, precipitation_sum, precipitation_hours)
                SELECT %(eff_datetime)s, city, forecst_datetime, sunrise, sunset, daylight_duration, sunshine_duration, weather_code, uv_index_max, 
                    uv_index_clear_sky_max, rain_sum, showers_sum, snowfall_sum, precipitation_sum, precipitation_hours
                from bronze_meteo_forcast_daily
                where file_date + INTERVAL '1 DAY' = %(eff_datetime)s
                and forecst_datetime >= %(eff_datetime)s and forecst_datetime <= %(end_datetime)s
        '''
    execute(sql,locals())

bronze_to_silver('2026-08-15')
