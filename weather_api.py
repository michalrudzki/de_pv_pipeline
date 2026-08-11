import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

import pickle
import datetime

now = datetime.datetime.now()
file_date = now.strftime("%Y-%m-%d")

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
# If You like to gether historical data You can use params "past_days": 7 - but not sure if API is returning forecast or actual weather then
url = "https://api.open-meteo.com/v1/forecast"
params_Warszawa = {
	"latitude": 52.13,
	"longitude": 21,
	"daily": ["sunrise", "sunset", "daylight_duration", "sunshine_duration", "weather_code", "uv_index_max", "uv_index_clear_sky_max", "rain_sum", "showers_sum", "snowfall_sum", "precipitation_sum", "precipitation_hours"],
	"hourly": ["cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "visibility", "temperature_2m", "relative_humidity_2m", "dew_point_2m", "rain", "showers", "snowfall", "weather_code"],
	"timezone": "Europe/Berlin",
    "forecast_days": 3,
}
params_Krakow = {
	"latitude": 50.06,
	"longitude": 19.56,
	"daily": ["sunrise", "sunset", "daylight_duration", "sunshine_duration", "weather_code", "uv_index_max", "uv_index_clear_sky_max", "rain_sum", "showers_sum", "snowfall_sum", "precipitation_sum", "precipitation_hours"],
	"hourly": ["cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "visibility", "temperature_2m", "relative_humidity_2m", "dew_point_2m", "rain", "showers", "snowfall", "weather_code"],
	"timezone": "Europe/Berlin",
    "forecast_days": 3,
}
params_Szczecin = {
	"latitude": 53.43,
	"longitude": 14.55,
	"daily": ["sunrise", "sunset", "daylight_duration", "sunshine_duration", "weather_code", "uv_index_max", "uv_index_clear_sky_max", "rain_sum", "showers_sum", "snowfall_sum", "precipitation_sum", "precipitation_hours"],
	"hourly": ["cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "visibility", "temperature_2m", "relative_humidity_2m", "dew_point_2m", "rain", "showers", "snowfall", "weather_code"],
	"timezone": "Europe/Berlin",
    "forecast_days": 3,
}

def get_meteo(params, city):
    responses = openmeteo.weather_api(url, params = params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation: {response.Elevation()} m asl")
    #print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
    #print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_cloud_cover = hourly.Variables(0).ValuesAsNumpy()
    hourly_cloud_cover_low = hourly.Variables(1).ValuesAsNumpy()
    hourly_cloud_cover_mid = hourly.Variables(2).ValuesAsNumpy()
    hourly_cloud_cover_high = hourly.Variables(3).ValuesAsNumpy()
    hourly_visibility = hourly.Variables(4).ValuesAsNumpy()
    hourly_temperature_2m = hourly.Variables(5).ValuesAsNumpy()
    hourly_relative_humidity_2m = hourly.Variables(6).ValuesAsNumpy()
    hourly_dew_point_2m = hourly.Variables(7).ValuesAsNumpy()
    hourly_rain = hourly.Variables(8).ValuesAsNumpy()
    hourly_showers = hourly.Variables(9).ValuesAsNumpy()
    hourly_snowfall = hourly.Variables(10).ValuesAsNumpy()
    hourly_weather_code = hourly.Variables(11).ValuesAsNumpy()

    hourly_data = {
        "date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        ).tz_convert(response.Timezone().decode())
    }

    hourly_data["cloud_cover"] = hourly_cloud_cover
    hourly_data["cloud_cover_low"] = hourly_cloud_cover_low
    hourly_data["cloud_cover_mid"] = hourly_cloud_cover_mid
    hourly_data["cloud_cover_high"] = hourly_cloud_cover_high
    hourly_data["visibility"] = hourly_visibility
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
    hourly_data["dew_point_2m"] = hourly_dew_point_2m
    hourly_data["rain"] = hourly_rain
    hourly_data["showers"] = hourly_showers
    hourly_data["snowfall"] = hourly_snowfall
    hourly_data["weather_code"] = hourly_weather_code

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    #print("\nHourly data\n", hourly_dataframe)

    with open(f"data/meteo_hourly_{city}_{file_date}.pkl", 'wb') as f:
        pickle.dump(hourly_dataframe, f)

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_sunrise = daily.Variables(0).ValuesInt64AsNumpy()
    daily_sunset = daily.Variables(1).ValuesInt64AsNumpy()
    daily_daylight_duration = daily.Variables(2).ValuesAsNumpy()
    daily_sunshine_duration = daily.Variables(3).ValuesAsNumpy()
    daily_weather_code = daily.Variables(4).ValuesAsNumpy()
    daily_uv_index_max = daily.Variables(5).ValuesAsNumpy()
    daily_uv_index_clear_sky_max = daily.Variables(6).ValuesAsNumpy()
    daily_rain_sum = daily.Variables(7).ValuesAsNumpy()
    daily_showers_sum = daily.Variables(8).ValuesAsNumpy()
    daily_snowfall_sum = daily.Variables(9).ValuesAsNumpy()
    daily_precipitation_sum = daily.Variables(10).ValuesAsNumpy()
    daily_precipitation_hours = daily.Variables(11).ValuesAsNumpy()

    daily_data = {
        "date": pd.date_range(
            start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
            end =  pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = daily.Interval()),
            inclusive = "left"
        ).tz_convert(response.Timezone().decode())
    }

    daily_data["sunrise"] = daily_sunrise
    daily_data["sunset"] = daily_sunset
    daily_data["daylight_duration"] = daily_daylight_duration
    daily_data["sunshine_duration"] = daily_sunshine_duration
    daily_data["weather_code"] = daily_weather_code
    daily_data["uv_index_max"] = daily_uv_index_max
    daily_data["uv_index_clear_sky_max"] = daily_uv_index_clear_sky_max
    daily_data["rain_sum"] = daily_rain_sum
    daily_data["showers_sum"] = daily_showers_sum
    daily_data["snowfall_sum"] = daily_snowfall_sum
    daily_data["precipitation_sum"] = daily_precipitation_sum
    daily_data["precipitation_hours"] = daily_precipitation_hours

    daily_dataframe = pd.DataFrame(data = daily_data)
    #print("\nDaily data\n", daily_dataframe)

    with open(f"data/meteo_daily_{city}_{file_date}.pkl", 'wb') as f:
        pickle.dump(daily_dataframe, f)

get_meteo(params_Warszawa, 'Warszawa')
get_meteo(params_Krakow, 'Krakow')
get_meteo(params_Szczecin, 'Szczecin')

