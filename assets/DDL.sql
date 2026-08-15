--drop table public.user;

CREATE TABLE public.USER (
  id_inst INT,
  city VARCHAR(50),
  inverter VARCHAR(100),
  power INT,
  from_date TIMESTAMP,
  to_date TIMESTAMP
);

create table public.bronze_pv_production (
id_inst INT,
current_power_W DECIMAL(12,2),
daily_kWh DECIMAL(12,2),
monthly_kWh DECIMAL(12,2),
yearly_kWh DECIMAL(12,2),
Total_MWh DECIMAL(12,2),
eff_date TIMESTAMP
);

create table public.bronze_meteo_forcast_hourly (
file_date TIMESTAMP,
city VARCHAR(50),
forecst_datetime TIMESTAMP,
cloud_cover DECIMAL(10,2),
cloud_cover_low DECIMAL(10,2), 
cloud_cover_mid DECIMAL(10,2), 
cloud_cover_high DECIMAL(10,2), 
visibility DECIMAL(12,2), 
temperature_2m DECIMAL(10,2), 
relative_humidity_2m DECIMAL(10,2), 
dew_point_2m DECIMAL(16,8), 
rain DECIMAL(10,2), 
showers DECIMAL(10,2),  
snowfall DECIMAL(10,2), 
weather_code DECIMAL(10,2)
);

create table public.bronze_meteo_forcast_daily (
file_date TIMESTAMP,
city VARCHAR(50),
forecst_datetime TIMESTAMP,
sunrise INT,
sunset INT,
daylight_duration DECIMAL(16,8),
sunshine_duration DECIMAL(16,8), 
weather_code DECIMAL(10,2), 
uv_index_max DECIMAL(10,2), 
uv_index_clear_sky_max DECIMAL(10,2), 
rain_sum DECIMAL(10,2), 
showers_sum DECIMAL(10,2), 
snowfall_sum DECIMAL(10,2), 
precipitation_sum DECIMAL(10,2), 
precipitation_hours DECIMAL(10,2)
);


SELECT *
  FROM information_schema.tables
-- WHERE table_schema='public'
--   AND table_type='BASE TABLE'
;

select 5::NUMERIC/2::NUMERIC;

/*Silver - handles dates so We can combine easly forecast from day-1 file to "day" date, co it can match pv_production date*/
/*no other data cleanup is required with our datasets */
/* pv goes 1:1 to silver */
/* meteo - dates modification is required */
 
create table public.silver_pv_production (
id_inst INT,
current_power_W DECIMAL(12,2),
daily_kWh DECIMAL(12,2),
monthly_kWh DECIMAL(12,2),
yearly_kWh DECIMAL(12,2),
Total_MWh DECIMAL(12,2),
eff_date TIMESTAMP
);

create table public.silver_meteo_forcast_hourly (
forecast_date TIMESTAMP,
city VARCHAR(50),
forecst_datetime TIMESTAMP,
cloud_cover DECIMAL(10,2),
cloud_cover_low DECIMAL(10,2), 
cloud_cover_mid DECIMAL(10,2), 
cloud_cover_high DECIMAL(10,2), 
visibility DECIMAL(12,2), 
temperature_2m DECIMAL(10,2), 
relative_humidity_2m DECIMAL(10,2), 
dew_point_2m DECIMAL(16,8), 
rain DECIMAL(10,2), 
showers DECIMAL(10,2),  
snowfall DECIMAL(10,2), 
weather_code DECIMAL(10,2)
);

create table public.silver_meteo_forcast_daily (
forecast_date TIMESTAMP,
city VARCHAR(50),
forecst_datetime TIMESTAMP,
sunrise INT,
sunset INT,
daylight_duration DECIMAL(16,8),
sunshine_duration DECIMAL(16,8), 
weather_code DECIMAL(10,2), 
uv_index_max DECIMAL(10,2), 
uv_index_clear_sky_max DECIMAL(10,2), 
rain_sum DECIMAL(10,2), 
showers_sum DECIMAL(10,2), 
snowfall_sum DECIMAL(10,2), 
precipitation_sum DECIMAL(10,2), 
precipitation_hours DECIMAL(10,2)
);
