import requests
import datetime
import pandas as pd
import numpy as np

GC.createXDataSeries("WEATHER", "TEMPERATURE", "celsius")
GC.createXDataSeries("WEATHER", "HUMIDITY", "%")
GC.createXDataSeries("WEATHER", "WINDSPEED", "kmh")
GC.createXDataSeries("WEATHER", "WINDDIRECTION", "degrees")
GC.createXDataSeries("WEATHER", "PRESSURE", "pascal")

GC.createXDataSeries("WEATHER", "STATION_LAT", "degrees")
GC.createXDataSeries("WEATHER", "STATION_LON", "degrees")
GC.createXDataSeries("WEATHER", "DISTANCE_TO_STATION", "gps_raw_dist")

# Gloabl definitions
PUBLIC_TOKEN="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
API_KEY="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
BASE_URL="https://api.synopticdata.com/v2/"
HIRSTORIC_DATA = "stations/timeseries"
UNITS="metric"

min_extra=30

# GC Data
act_date = GC.activityMetrics()["date"]
act_time = GC.activityMetrics()["time"]
start_datetime = datetime.datetime.combine(act_date, act_time)
act_duration = GC.activityMetrics()["Duration"]
end_datetime = start_datetime + datetime.timedelta(seconds=act_duration)
seconds = list(GC.series(GC.SERIES_SECS))
lat = GC.series(GC.SERIES_LAT)
lon = GC.series(GC.SERIES_LON)

def _datetime_to_api_datetime(datetime_obj):
    datetime_str = datetime_obj.strftime("%Y%m%d%H%M")
    return datetime_str

###### PULL ALL STATIONS DATA ######
url = BASE_URL + HIRSTORIC_DATA
params = {
    "token":PUBLIC_TOKEN # API_KEY
,"output":"json"
,"obtimezone":"local"
,"country":"us"
,"state":"CA"
# ,"county":"Los Angeles"
#,"STID":"KLAX"
,"status":"active"
,"end":_datetime_to_api_datetime(end_datetime + datetime.timedelta(minutes=min_extra))
,"start":_datetime_to_api_datetime(start_datetime - datetime.timedelta(minutes=min_extra))
,"showemptystations":1
,"units":"metric"}

## Make request and then create df of viable stations
full_response = requests.get(url=url,
params=params)
stations = full_response.json()['STATION']

st_locs = []
for i, station in enumerate(stations):
    if station['STATUS'] == 'ACTIVE' and 'OBSERVATIONS' in station.keys() and station['STID'][0]=='K' and (
            'date_time' in station['OBSERVATIONS'].keys()
            and 'wind_direction_set_1' in station['OBSERVATIONS'].keys()
            and 'pressure_set_1d' in station['OBSERVATIONS'].keys()
            and 'relative_humidity_set_1' in station['OBSERVATIONS'].keys()
            and 'wind_speed_set_1' in station['OBSERVATIONS'].keys()
            and 'air_temp_set_1' in station['OBSERVATIONS'].keys()):
        st_locs.append({"STID":station['STID']
                    ,"LONGITUDE":float(station['LONGITUDE'])
                    ,"LATITUDE":float(station['LATITUDE'])
                    ,"OBS_COUNT":len(station['OBSERVATIONS']['date_time'])
                    ,"resp_index":i})
st_df = pd.DataFrame(st_locs)
print(st_df.shape)

def _make_reference_points(start_datetime, seconds, lat, lon, incremnet_length=10*60):
    ref_points = []
    increment_datetime = start_datetime
    index_point = 0
    while index_point < len(seconds)-incremnet_length:
        ref_points.append({"datetime":increment_datetime
                           ,"lat":lat[index_point]
                           ,"lon":lon[index_point]})
        index_point += incremnet_length
        increment_datetime = start_datetime + datetime.timedelta(seconds=seconds[index_point])
    return ref_points

def station_determination(ref_datetime, ref_lat, ref_lon):
    st_df['lat_diff'] = st_df['LATITUDE'] - ref_lat
    st_df['ref_diff'] = st_df['LONGITUDE'] - ref_lon
    st_df['distance'] = st_df['ref_diff']**2 + st_df['lat_diff']**2
    
    closest_10_stations = st_df.sort_values('distance')[:10]
    closest_10_stations['obs_lower_limit'] = closest_10_stations['OBS_COUNT'].mean() - closest_10_stations['OBS_COUNT'].std()
    
    viable_stations = closest_10_stations[closest_10_stations['OBS_COUNT'] > closest_10_stations['obs_lower_limit']]
    station_choice_id, station_choice_index = viable_stations['STID'].tolist()[0], viable_stations['resp_index'].tolist()[0]
    station_lat = viable_stations['LATITUDE'].tolist()[0]
    station_lon = viable_stations['LONGITUDE'].tolist()[0]
    distance_to_station = viable_stations['distance'].tolist()[0]
    
    return station_choice_id, station_choice_index, station_lat, station_lon, distance_to_station

def extract_station_data(station_index, ref_datetime):
    station_in_use = stations[station_index]
    station_df = pd.DataFrame(station_in_use['OBSERVATIONS'])
    station_df['date_time'] = pd.to_datetime(station_df['date_time'])
    station_df['datetime_diff'] = abs(
        station_df['date_time'].apply(lambda x: (pd.Timestamp(x.to_datetime64()) - pd.Timestamp(ref_datetime)).seconds)
            )
    obs_in_use = station_df.sort_values('datetime_diff').iloc[0]
    ref_station_data = obs_in_use[['date_time',
                                    'wind_direction_set_1',
                                    'pressure_set_1d',
                                    'relative_humidity_set_1',
                                    'wind_speed_set_1',
                                    'air_temp_set_1']].to_dict()

    return ref_station_data

def _ref_point_stations(ref_datetimes):
    for i, point in enumerate(ref_datetimes):
        station_choice_id, station_choice_index, station_lat, station_lon, distance_to_station = station_determination(ref_datetime=point['datetime'], ref_lat=point['lat'], ref_lon=point['lon'])
        point['station_id'] = station_choice_id
        point['station_index'] = station_choice_index
        point['station_lat'] = station_lat
        point['station_lon'] = station_lon
        point['distance_to_station'] = distance_to_station

        ref_station_data = extract_station_data(station_index=station_choice_index
                                                 ,ref_datetime=point['datetime'])
        point.update(ref_station_data)
        ref_datetimes[i] = point
        print(station_lat,station_lon,distance_to_station)
    return ref_datetimes


# Clean up GPS Data and get reference markers for submission
lat = pd.Series([a for a in lat]).replace(0,np.nan).fillna(method='bfill').tolist()
lon = pd.Series([a for a in lon]).replace(0,np.nan).fillna(method='bfill').tolist()
ref_datetimes = _make_reference_points(start_datetime, seconds, lat, lon, incremnet_length=5*60)

ref_weather_records = _ref_point_stations(ref_datetimes)


for weather_record in ref_weather_records:
    GC.xdataSeries("WEATHER", "secs").append((pd.Timestamp(weather_record['date_time'].to_datetime64()) - pd.Timestamp(start_datetime)).seconds)
    index = len(GC.xdataSeries("WEATHER", "secs"))-1
    GC.xdataSeries("WEATHER", "TEMPERATURE")[index] = weather_record['air_temp_set_1']
    GC.xdataSeries("WEATHER", "HUMIDITY")[index] = weather_record['relative_humidity_set_1']
    GC.xdataSeries("WEATHER", "WINDSPEED")[index] = weather_record['wind_speed_set_1']
    GC.xdataSeries("WEATHER", "WINDDIRECTION")[index] = weather_record['wind_direction_set_1']
    GC.xdataSeries("WEATHER", "PRESSURE")[index] = weather_record['pressure_set_1d']

    #GC.xdataSeries("WEATHER", "STATION_ID")[index] = weather_record['station_id']
    GC.xdataSeries("WEATHER", "STATION_LAT")[index] = weather_record['station_lat']
    GC.xdataSeries("WEATHER", "STATION_LON")[index] = weather_record['station_lon']
    GC.xdataSeries("WEATHER", "DISTANCE_TO_STATION")[index] = weather_record['distance_to_station']