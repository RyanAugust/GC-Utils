import requests
import datetime
import pandas as pd
# import numpy as np
import json

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - [%(levelname)-8s] - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


# Get timezone offset based on lat lon
def timezone_finder(lat,lon):
    import datetime
    import pytz
    from tzwhere import tzwhere

    tzwhere = tzwhere.tzwhere()
    timezone_str = tzwhere.tzNameAt(lat, lon)

    timezone = pytz.timezone(timezone_str)
    dt = datetime.datetime.now()
    utcoffset = timezone.utcoffset(dt)
    return utcoffset

# GC Data

seconds = list(GC.series(GC.SERIES_SECS))
lat = GC.series(GC.SERIES_LAT)
lon = GC.series(GC.SERIES_LON)
utcoffset = timezone_finder(lat[len(lat)//2],lon[len(lat)//2])
act_date = GC.activityMetrics()["date"]
act_time = GC.activityMetrics()["time"]
start_datetime = datetime.datetime.combine(act_date, act_time) + utcoffset
act_duration = GC.activityMetrics()["Duration"]
end_datetime = start_datetime + datetime.timedelta(seconds=act_duration)
    


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
    
    def point_observation_data(self, lat, lon, ref_time, ref_time_bracket_minutes:int=20):
        stations = self._get_point_associated_stations(lat=lat, lon=lon)['features']
        station_attempt = 0
        station_found = False
        while station_found == False:
            station_id = stations[station_attempt]['properties']['stationIdentifier']
            time_bracket = datetime.timedelta(seconds=ref_time_bracket_minutes*60)
            start_limit, end_limit = ref_time - time_bracket, ref_time + time_bracket
            station_obs_data = self._get_observation_data(
                stationId=station_id,
                start_limit=start_limit,
                end_limit=end_limit,
                limit=10)
            station_found, station_data = self._extract_observation_data_dict(station_obs_data)
            station_attempt += 1
            logger.debug(f'Bumping station to number {station_attempt}')
        return station_data
    
    def _extract_observation_data_df(self, observation_response:dict) -> pd.DataFrame:
        obs_df = pd.json_normalize(observation_response['features'])
        return obs_df
    
    def _extract_observation_data_dict(self, observation_response:dict) -> dict:
        try:
            record = observation_response['features'][0]
        except IndexError:
            return False, {}
        data_dict = {
            'date_time': self._none_protection(record['properties']['timestamp']),
            'temp': self._none_protection(record['properties']['temperature']['value']),
            'humidity': self._none_protection(record['properties']['relativeHumidity']['value']),
            'wind_speed': self._none_protection(record['properties']['windSpeed']['value']),
            'wind_gust': self._none_protection(record['properties']['windGust']['value']),
            'wind_direction': self._none_protection(record['properties']['windDirection']['value']),
            'wind_chill': self._none_protection(record['properties']['windChill']['value']),
            'pressure': self._none_protection(record['properties']['barometricPressure']['value']),
            'heat_index': self._none_protection(record['properties']['heatIndex']['value']),
            'station_id': self._none_protection(record['properties']['station']),
            'station_lat': self._none_protection(record['geometry']['coordinates'][1]),
            'station_lon': self._none_protection(record['geometry']['coordinates'][0]),
            'description': self._none_protection(record['properties']['textDescription'])
        }
        return True, data_dict

    def _none_protection(self, val):
        if val is None:
            return 0
        else:
            return val


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
        print(weather_records)
        for index, weather_record in enumerate(weather_records):
            GC.xdataSeries("WEATHER", "secs").append((datetime.datetime.fromisoformat(weather_record['date_time']) - pd.Timestamp(start_datetime, tz='UTC')).seconds)
            # index = len(GC.xdataSeries("WEATHER", "secs")) - 1
            # GC.xdataSeries("WEATHER", "secs")[index] = (datetime.datetime.fromisoformat(weather_record['date_time']) - pd.Timestamp(start_datetime, tz='UTC')).seconds
            GC.xdataSeries("WEATHER", "TEMPERATURE")[index] = weather_record['temp']
            GC.xdataSeries("WEATHER", "HUMIDITY")[index] = weather_record['humidity']
            GC.xdataSeries("WEATHER", "WINDSPEED")[index] = weather_record['wind_speed']
            GC.xdataSeries("WEATHER", "WINDGUST")[index] = weather_record['wind_gust']
            GC.xdataSeries("WEATHER", "WINDDIRECTION")[index] = weather_record['wind_direction']
            GC.xdataSeries("WEATHER", "WINDCHILL")[index] = weather_record['wind_chill']
            GC.xdataSeries("WEATHER", "PRESSURE")[index] = weather_record['pressure']
            GC.xdataSeries("WEATHER", "HEATINDEX")[index] = weather_record['heat_index']
            # GC.xdataSeries("WEATHER", "DESCRTIPTION")[index] = weather_record['description']

            # GC.xdataSeries("WEATHER", "STATION_ID")[index] = weather_record['station_id']
            GC.xdataSeries("WEATHER", "STATION_LAT")[index] = weather_record['station_lat']
            GC.xdataSeries("WEATHER", "STATION_LON")[index] = weather_record['station_lon']

    def _make_reference_points(self, start_datetime, end_datetime, seconds, lat, lon, incremnet_length=10*60, **kwargs):
        logger.info(f'seconds are of length {len(seconds)}')
        ref_points = []
        increment_datetime = start_datetime
        index_point = 10
        while index_point < len(seconds)-incremnet_length:
            if lat[index_point] > 0:
                ref_points.append({"ref_time":increment_datetime
                                ,"lat":lat[index_point]
                                ,"lon":lon[index_point]})
                index_point += incremnet_length
                increment_datetime = start_datetime + datetime.timedelta(seconds=seconds[index_point])
            else:
                index_point += 10
                logger.warning(f'Bumping index point due to bad lat, lon. New index_point: {index_point}')
        return ref_points


def main():
    # Extract data from activity
    gci = GC_interaction()
    activity_data = gci.get_activity_data()
    activity_data
    # Make reference points based on activity data
    ref_points = gci._make_reference_points(**activity_data)

    # Call weather API for reference points
    weather_records = []
    wapi = weather_api_wrapper()
    for ref_point in ref_points:
        point_obs_data = wapi.point_observation_data(**ref_point)
        weather_records.append(point_obs_data)

    # Build & Fill Weather XDATA
    gci.init_gc_fields()
    gci.store_weather_data_to_activity(weather_records=weather_records)

main()