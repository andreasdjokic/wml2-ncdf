from netCDF4 import Dataset, date2num, stringtochar, stringtoarr
import numpy as np 
from datetime import timedelta, datetime
""" Hard-coding the timeseries in Python """
# Helper method to see whether or not something is a valid int
def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

# Returns a list of 22 strings, each string representing the name of a gage
def gageList(timeseries):
	f = open(timeseries, "r")
	f.seek(0,0)
	sentence = f.readline()
	sentence = sentence.split()
	s1 = []
	for i in range(len(sentence)):
		isValid = RepresentsInt(sentence[i])
		if(isValid):
			s1.append(sentence[i])
		else:
			continue
	return s1

# Returns a list(x) of lists(y), where each y is a value at a different year/month
# And each x is a different gage
def timeSeriesList(timeseries):
	f = open(timeseries, "r")
	f.seek(0,0)
	sentence = []
	s1 = []
	for line in f:
		sentence = line.split()
		for i in range(len(sentence)):
			isValid = RepresentsInt(sentence[i])
			isValidString = isinstance(sentence[i], basestring)
			if(isValid):
				None
			else:
				s1.append(sentence[i])
	s1.remove("YEAR")
	s1.remove("MONTH")
	counter = 0
	month = 0
	s2 = []
	for value in s1:
		if(counter < 22):
			s2.append([value])
			counter = counter + 1
		else:
			month = counter % 22
			s2[month].append(value)
			counter = counter + 1
	return s2

# Want to return a list of pairs, with the first value being the gage name, and the second being
# the list of values for each gage
def bigList(gage_list, gage_values):
	s1 = []
	for i in range(len(gage_list)):
		s1.append((gage_list[i], gage_values[i]))
	return s1

# Want to return a list, where each value of the list is a date,
# moving in increasing order. i.e., 1980-01-1 --> 2009-12-01
def makeDate(timeseries):
	f = open(timeseries, "r")
	f.seek(0,0)
	years = []
	# Create a list of years
	for line in f:
		sentence = line.split()
		if(sentence and sentence[0] == "YEAR"):
			continue
		elif(sentence):
			years.append(sentence[0])
		else:
			break
	months = []
	counter = 0
	# Create a list of months
	for i in range(len(years)):
		months.append(str((i%12)+1).zfill(2))
	days = []
	# Create a list of days
	for i in range(len(years)):
		days.append(str(1).zfill(2))
	# Combine years-months-days
	final_date = []
	for i in range(len(years)):
		final = ""
		year = years[i]
		month = months[i]
		day = days[i]
		final = year + "-" + month + "-" + day
		final_date.append(final)
	return final_date

# Returns the number of characters in a string. Used to determine what to
# pass into stringtoarr as the NUMCHARS value
def charCounter(word):
	counter = 0
	for i in word:
		counter = counter + 1
	return counter

# Takes a list of the names of the stations (station_names) and returns a
# character array length NUMCHARS
def stringToArrList(list):
	numchars = charCounter(list[0])
	newList = []
	for i in range(len(list)):
		newList.append(stringtoarr(list[i], numchars))
	return newList

""" Create the list of data, create the list of dates """
timeseries = "./practiceGages" #location of practiceGages (change after download)
gage_list = gageList(timeseries)
gage_values = timeSeriesList(timeseries)
big_list = bigList(gage_list, gage_values)
final_date = makeDate(timeseries)
print final_date


""" NetCDF Code """
nc_title = "testing_title"
nc_summary = "testing_summary"
nc_date_create = "2013-05-03"
nc_creator_name = "David Blodgett"
nc_creator_email= "dblodgett@usgs.gov"
nc_project = "testing_project"
nc_proc_level = "testing_process_level"
nc_data_var_name = "data"
nc_data_var_units = "cfs"
nc_data_longName = "Modeled Stream Flow"
nc_data_prec = "single"
nc_stations = gage_list
nc_station_dim_name = "gage"
nc_station_longname = "NWIS Site ID"
nc_time_coords = final_date
nc_num_times = len(nc_time_coords)
nc_filename = "test.nc"


#Create the file
nc_file = Dataset(nc_filename, 'w', format='NETCDF4')

#Create the dimensions
try:
	nc_station_dim = nc_file.createDimension('procedure', len(gage_list))
	nc_station_name_dim = nc_file.createDimension('station_nm', None)
	nc_time_dim = nc_file.createDimension('time', None)
	
	# time variable attributes
	nc_time = nc_file.createVariable('time', 'f8', ('time',))
	nc_time.units = 'days since 1970-01-01 00:00:00'
	nc_time.calendar = 'gregorian'
	nc_time.standard_name = 'time'
	
	# values variable attributes
	nc_values_var = nc_file.createVariable('values', 'f4', ('station_nm', 'time',))
	nc_values_var.units = 'cfs'
	nc_values_var.missing_value = '-999'
	nc_values_var.long_name = 'Modeled Stream Flow'
	nc_values_var.coordinates = 'time lat lon'
	
	# station_nm variable attributes 
	nc_station_names = nc_file.createVariable('stations', 'c', ('station_nm', 'time',)) 
	nc_station_names.units = ''
	#nc_station_names.long_names = nc_station_longname
	nc_station_names.standard_name = 'station_id'
	nc_station_names.cf_role = 'timeseries_id'
	
	# lat variable attributes
	nc_lat_var = nc_file.createVariable('lat', 'f4', ('station_nm',))
	nc_lat_var.units = 'degree_north'
	nc_lat_var.long_name = 'Latitude'
	#nc_lat_var.standard_name = 'latitude'
	
	# lon variable attributes
	nc_lon_var = nc_file.createVariable('lon', 'f4',('station_nm',))
	nc_lon_var.units = 'degree_east'
	nc_lon_var.long_name = 'Longitude'
	#nc_lon_var.standard_name = 'longitude'
	
	# Create ncdf attributes
	nc_file.WML_Conventions = 'CF-1.6'
	nc_file.WML_featureType = 'timeSeries'
	nc_file.WML_cdm_data_type = 'Station'
	nc_file.WML_standard_name_vocabulary = 'CF-1.6'
	nc_file.title = nc_title
	nc_file.summary = nc_summary
	nc_file.id = 'testing_id'
	nc_file.naming_authory = 'testing_authority'
	nc_file.WML_date_created = nc_date_create
	nc_file.WML_creator_name = nc_creator_name
	nc_file.creator_email = nc_creator_email
	nc_file.project = nc_project
	nc_file.processing_level = nc_proc_level
	nc_file.WML_profile = 'single variable'
	
	# data
	dates = [datetime(2001,3,1)+n*timedelta(hours=12) for n in range(12)]
	nc_time[:] = date2num(dates,units=nc_time.units,calendar=nc_time.calendar)
	#nc_station_names[:] = [stringtoarr("aaaa",4),stringtoarr("bbbb",4)]
	dummy = [stringtoarr("aaaa",4),stringtoarr("bbbb",4)]
	nc_station_names[:] = dummy
	nc_lat_var[:] = [35.0, 70.0]
	nc_lon_var[:] = [-120.0, 120.0]
	#for i in range(len(nc_station_names)):
		#data[i,:] = np.random.uniform(len(nc_time))
	
except:
	print "Try again."
nc_file.close()


