import requests
import datetime
import pandas as pd
# import numpy as np
import json

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - [%(levelname)-8s] - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# GC Data
act_date = GC.activityMetrics()["date"]
act_time = GC.activityMetrics()["time"]
start_datetime = datetime.datetime.combine(act_date, act_time)
act_duration = GC.activityMetrics()["Duration"]
end_datetime = start_datetime + datetime .timedelta(seconds=act_duration)
seconds = list(GC.series(GC.SERIES_SECS))
lat = GC.series(GC.SERIES_LAT)
lon = GC.series(GC.SERIES_LON)

class weather_api_wrapper:
    def __init__(self):
        self.base_url = "https://api.weather.gov"
        self.points_edge = "points"
        self.stations_edge = "stations"
        self.observations_endpoint = "stations/{stationId}/observations"
        self.datetime_format = "%Y-%m-%dT%H:%M:%SZ"

    def _points(self, lat, lon):
        url = f"{self.base_url}/{self.points_edge}/{lat:0.4f},{lon:0.4f}"
        logger.debug(f'_points url call || url:{url}')
        r = requests.get(url)
        return r

    def _get_point_associated_stations(self, lat:float, lon:float):
        point_return = self._points(lat, lon)
        point_json = point_return.json()
        stations_endpoint = point_json['properties']['observationStations']
        logger.debug(f'stations_endpoint url call | url:{stations_endpoint}')
        r = requests.get(url=stations_endpoint).json()
        return r

    def _get_observation_data(self, stationId, start_limit, end_limit, limit:int=25):
        formatted_obs_endpoint = self.observations_endpoint.format(
            stationId=stationId
            )
        url = f"{self.base_url}/{formatted_obs_endpoint}"
        params = {
            "start":start_limit.strftime(self.datetime_format,),
            "end":end_limit.strftime(self.datetime_format),
            "limit":limit
        }
        logger.debug(f'observation_data url call || url:{url} params:{params}')
        r = requests.get(url, params)
        # assert r.status_code == 200, "call unsuccessful :: returned status code of {r.status_code}"
        observation_data_json = r.json()
        return observation_data_json
    
    def point_observation_data(self, lat, lon, ref_time, ref_time_bracket_minutes:int=15):
        stations = self._get_point_associated_stations(lat=lat, lon=lon)['features']
        # for station in stations:
        station_id = stations[0]['properties']['stationIdentifier']
        time_bracket = datetime.timedelta(seconds=ref_time_bracket_minutes*60)
        start_limit, end_limit = ref_time - time_bracket, ref_time + time_bracket
        station_obs_data = self._get_observation_data(
            stationId=station_id,
            start_limit=start_limit,
            end_limit=end_limit,
            limit=10)
        station_data = self._extract_observation_data_dict(station_obs_data)
        return station_data
    
    def _extract_observation_data_df(self, observation_response:dict) -> pd.DataFrame:
        obs_df = pd.json_normalize(observation_response['features'])
        return obs_df
    
    def _extract_observation_data_dict(self, observation_response:dict) -> dict:
        record = observation_response['features'][0]
        data_dict = {
            'temp': record['properties']['temperature']['value'],
            'humidity': record['properties']['relativeHumidity']['value'],
            'wind_speed': record['properties']['windSpeed']['value'],
            'wind_gust': record['properties']['windGust']['value'],
            'wind_direction': record['properties']['windDirection']['value'],
            'wind_chill': record['properties']['windChill']['values'],
            'pressure': record['properties']['barometricPressure']['value'],
            'heat_index': record['properties']['heatIndex']['value'],
            'station_id': record['properties']['station'],
            'station_lat': record['geometry.coordinates'][1],
            'station_lon': record['geometry.coordinates'][0],
            'description': record['properties']['textDescription']['value']
        }
        return data_dict





# class helper_functions:
#     def _datetime_to_api_datetime(datetime_obj):
#         datetime_str = datetime_obj.strftime("%Y%m%d%H%M")
#         return datetime_str

class GC_interaction:
    def get_activity_data(self) -> dict:
        act_date = GC.activityMetrics()["date"]
        act_time = GC.activityMetrics()["time"]
        start_datetime = datetime.datetime.combine(act_date, act_time)
        act_duration = GC.activityMetrics()["Duration"]
        gc_data = {
            'act_date': act_date,
            'act_time': act_time,
            'start_datetime': start_datetime,
            'act_duration': act_duration,
            'end_datetime': start_datetime + datetime.timedelta(seconds=act_duration),
            'seconds': list(GC.series(GC.SERIES_SECS)),
            'lat': GC.series(GC.SERIES_LAT),
            'lon': GC.series(GC.SERIES_LON)
        }
        return gc_data

    def init_gc_fields(self) -> None:
        GC.createXDataSeries("WEATHER", "TEMPERATURE", "celsius")
        GC.createXDataSeries("WEATHER", "HUMIDITY", "%")
        GC.createXDataSeries("WEATHER", "WINDSPEED", "kmh")
        GC.createXDataSeries("WEATHER", "WINDGUST", "kmh")
        GC.createXDataSeries("WEATHER", "WINDDIRECTION", "degrees")
        GC.createXDataSeries("WEATHER", "WINDCHILL", "degrees")
        GC.createXDataSeries("WEATHER", "PRESSURE", "pascal")
        GC.createXDataSeries("WEATHER", "HEATINDEX", "celsius")
        GC.createXDataSeries("WEATHER", "DESCRTIPTION", "text")

        GC.createXDataSeries("WEATHER", "STATION_LAT", "degrees")
        GC.createXDataSeries("WEATHER", "STATION_LON", "degrees")
        GC.createXDataSeries("WEATHER", "STATION_ID", "text")

    def store_weather_data_to_activity(self, weather_records:list) -> None:
        """ TODO: Convert this to take just the GC fields as inputs so that 
        iteration is handled outside of this function
        """
        for weather_record in weather_records:
            GC.xdataSeries("WEATHER", "secs").append((pd.Timestamp(weather_record['date_time'].to_datetime64()) - pd.Timestamp(start_datetime)).seconds)
            index = len(GC.xdataSeries("WEATHER", "secs")) - 1
            GC.xdataSeries("WEATHER", "TEMPERATURE")[index] = weather_record['temp']
            GC.xdataSeries("WEATHER", "HUMIDITY")[index] = weather_record['humidity']
            GC.xdataSeries("WEATHER", "WINDSPEED")[index] = weather_record['wind_speed']
            GC.xdataSeries("WEATHER", "WINDGUST")[index] = weather_record['wind_gust']
            GC.xdataSeries("WEATHER", "WINDDIRECTION")[index] = weather_record['wind_direction']
            GC.xdataSeries("WEATHER", "WINDCHILL")[index] = weather_record['wind_chill']
            GC.xdataSeries("WEATHER", "PRESSURE")[index] = weather_record['pressure']
            GC.xdataSeries("WEATHER", "HEATINDEX")[index] = weather_record['heat_index']
            GC.xdataSeries("WEATHER", "DESCRTIPTION")[index] = weather_record['description']

            GC.xdataSeries("WEATHER", "STATION_ID")[index] = weather_record['station_id']
            GC.xdataSeries("WEATHER", "STATION_LAT")[index] = weather_record['station_lat']
            GC.xdataSeries("WEATHER", "STATION_LON")[index] = weather_record['station_lon']

    def _make_reference_points(self, start_datetime, end_datetime, seconds, lat, lon, incremnet_length=10*60, **kwargs):
        ref_points = []
        increment_datetime = start_datetime
        index_point = 0
        # while index_point < len(seconds)-incremnet_length:
        while increment_datetime < end_datetime:
            ref_points.append({"ref_time":increment_datetime
                            ,"lat":lat[index_point]
                            ,"lon":lon[index_point]})
            index_point += incremnet_length
            increment_datetime = start_datetime + datetime.timedelta(seconds=seconds[index_point])
        return ref_points


def main():
    # Extract data from activity
    activity_data = GC_interaction.get_activity_data()
    activity_data
    # Make reference points based on activity data
    ref_points = GC_interaction._make_reference_points(**activity_data)

    # Call weather API for reference points
    weather_records = []
    wapi = weather_api_wrapper()
    for ref_point in ref_points:
        point_obs_data = wapi.point_observation_data(**ref_point)
        weather_records.append(point_obs_data)

    # Build & Fill Weather XDATA
    GC_interaction.init_gc_fields()
    GC_interaction.store_weather_data_to_activity(weather_records=weather_records)

main()