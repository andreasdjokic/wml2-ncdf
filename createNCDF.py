""" The idea of this file is to create a ncdf file from arbitrary/generic values for multiple points. 
    We assume we have a list of station names, latitude, longitude, and data values.
    We then create the global variables that we deem necessary, as well as the time
    and station name dimensions. Next, we create the main variables that will store the
    data, as variables that use the dimensions we created. We fill the variables with 
    the lists of data that we are provided (and ideally have extracted from a WaterML2 
    file)

    Note: Works under assumption that station_names are uniform length. If not, create
          a method to take in the list of names, and add buffers to the shorter names
          to create a new, uniformed list. 
"""
from netCDF4 import Dataset, date2num, stringtochar, stringtoarr
import numpy as np 
from datetime import timedelta, datetime

root_grp = Dataset('test3.nc', 'w', format='NETCDF4')
root_grp.description = 'Example temperature data'

""" Returns the number of characters in a string. Used to determine what to
    pass into stringtoarr as the NUMCHARS value """
def charCounter(word):
	counter = 0
	for i in word:
		counter = counter + 1
	return counter

""" Takes a list of the names of the stations (station_names) and returns a
    character array length NUMCHARS """
def stringToArrList(list):
	newList = []
	for i in range(len(list)):
		numchars = charCounter(list[i])
		newList.append(stringtoarr(list[i], numchars))
	return newList

station_list = ["S001", "S002", "S003", "S004", "S005", "S006", "S007", "S008","S009", "S010", "S011", "S012"]
lat_list = [-150.0, -120.0, -90.0, -60.0, -30.0, 0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0]
lon_list = [-150.0, -120.0, -90.0, -60.0, -30.0, 0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0]
data_values = [17.0, 26.0, 58.0, 37.0, 45.0, 66.0, 27.0, -2.0, 7.0, 9.0, 23.0, 14.0]

# Main
try: 
    # global
    root_grp.description = "Test"
    root_grp.cdm_datatype = "Station"
    root_grp.stationDimension = "station_nm";
    root_grp.featureType = "TimeSeries";
    root_grp.conventions= "CF-1.6";
    # dimensions
    root_grp.createDimension('time', None)
    root_grp.createDimension('station_nm', None) # stations unlimited = http://cf-pcmdi.llnl.gov/documents/cf-conventions/1.6/cf-conventions.html#idp8314368
    # variables
    times = root_grp.createVariable('time', 'f8', ('time',))
    times.units = 'hours since 0001-01-01 00:00:00.0'
    times.calendar = 'gregorian'
    times.standard_name= 'time'
    data = root_grp.createVariable('data', 'f4', ('station_nm','time',))
    data.coordinates='time lat lon'
    stations = root_grp.createVariable('stations', 'c', ('station_nm','time',))
    stations.units=""
    stations.standard_name= 'station_id'
    stations.cf_role = 'timeseries_id'
    lat = root_grp.createVariable('lat', 'f4', ('station_nm',))
    lat.units = 'degree_north'
    lat.long_name='Latitude'
    
    lon = root_grp.createVariable('lon', 'f4', ('station_nm',))
    lon.units = 'degree_east'
    lon.long_name="Longitude"
    
    # Fill in the individual data for each point (lat, lon, station name
    dates = [datetime(2001,3,1)+n*timedelta(hours=12) for n in range(12)]
    times[:]= date2num(dates,units=times.units,calendar=times.calendar)
    
    # Run under assumption all station names are equal in length; otherwise will get error: "ValueError: cannot set an array element with a sequence"
    # Might have to add functionality that finds the longest name, and pads the shorter names to be equal to the longest
    # Set the station names
    placeholder = stringToArrList(station_list)
    stations[:] = placeholder

    #set the latitude values
    lat[:] = lat_list 

    #set the longitude values
    lon[:] = lon_list 

    # Fill with data given
    for i in range(len(stations)):
       data[i,:] = data_values[i]
    
    # group
    # my_grp = root_grp.createGroup('my_group')
finally:   
    root_grp.close()
