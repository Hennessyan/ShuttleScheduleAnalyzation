import pandas as pd
import time
import datetime
import os
from math import radians, cos, sin, asin, sqrt, fabs

class ExtractMan:
    SHUTTLE_NUM = ["787", "788", "528", "526"]
    PHONE_ID = ["023d6dfce95b3997", "01ef64e4dec54025", "024a0c2d305eb3cc", "025391f6de955621"]
    NUM_OF_SHUTTLE = 4
    BuUnionLat = 42.086942806500474
    BuUnionLon = -75.96704414865724
    PATH = r'/Users/youngq/Documents/Pycharm27/LearnPycharm/BusAssignments/extractData'

    def __init__(self):
        print('Begin to get Driver information')

    @staticmethod
    def date_to_timestamp(date):  # convert Y/M/D H:M to x xxx xxx xxx . xxx
        time_array = time.strptime(date, "%Y/%m/%d %H:%M")
        timestamp = time.mktime(time_array)
        return timestamp

    @staticmethod
    def get_new_time_range(current_time, seconds):
        """
        :param current_time: 2017/7/5 15:0
        :param seconds:     -120s      or   120s
        :return:     2017/7/5 14:58    or   2017/7/5 15:2
        """
        dt = datetime.datetime.strptime(current_time, "%Y/%m/%d %H:%M")
        dt_s = dt + datetime.timedelta(seconds = seconds)
        return dt_s.strftime("%Y/%-m/%-d %-H:%-M")


    @staticmethod
    def hav(theta):
        s = sin(theta / 2)
        return s * s

    def get_distance_hav(self, lat0, lng0, lat1, lng1):
        r = 6371
        lat0 = radians(lat0)
        lat1 = radians(lat1)
        lng0 = radians(lng0)
        lng1 = radians(lng1)

        dlng = fabs(lng0 - lng1)
        dlat = fabs(lat0 - lat1)
        h = self.hav(dlat) + cos(lat0) * cos(lat1) * self.hav(dlng)
        distance = 2 * r * asin(sqrt(h)) * 1000
        return distance     # return meter

    def data_extract(self, filename, schedule, shuttle_num, date, file_type):
        """
        :param filename:    Gps.csv / Accelerometer.csv / Gyroscope.csv
        :param schedule:    list of list: [[start_time, end_time, route_name], ...]
        :param shuttle_num: index of shuttle: 0 -> 788
        :param date:        eg:2017/7/8
        :param file_type:   gps / acce /gyro    (used for name extracted data file)
        # :param driver:      instance of DriverSchedule: driver = ds.Driver()
        :return:            data with accurate scope
        """
        # create a shuttle info dictionary
        shuttle_dictionary = {}
        for i in range(len(ExtractMan.SHUTTLE_NUM)):  # len(ExtractMan.SHUTTLE_NUM) == NUM_OF_SHUTTLE
            shuttle_dictionary[ExtractMan.SHUTTLE_NUM[i]] = ExtractMan.PHONE_ID[i]

        # get data of corresponding shuttle according to shuttle_num
        my_matrix = pd.read_csv(filename, header=None)
        if shuttle_num in shuttle_dictionary.keys():
            phone_id = shuttle_dictionary[shuttle_num]
        else:
            print('No corresponding data of this shuttle, please check it again!')
            return -1
        data = my_matrix.loc[my_matrix.loc[:, 1] == phone_id, :]

        for temp_schedule in schedule:
            list_schedule = temp_schedule.split(',')
            start_time = date + ' ' + list_schedule[0]
            end_time = date + ' ' + list_schedule[1]
            count = 0       # record count of scope change, if bigger than 10 (20minutes), check this schedule, it must has
            while 1:        # something happen
                if count > 10:
                    print '!!!!!!!!!!!!!!!!'
                    print 'check route of this driver, some accidents may happens'
                    print temp_schedule
                    print '!!!!!!!!!!!!!!!!'
                    return -1
                start = self.date_to_timestamp(start_time)*1000
                end = self.date_to_timestamp(end_time)*1000
                result = data.loc[(start <= data.loc[:, 2]) & (data.loc[:, 2] < end), :]
                # result.to_csv(list_schedule[2] + '_' + file_type + '.csv')
                print start_time + ' ' + end_time
                start_lat = result.iloc[0,4]
                start_lon = result.iloc[0,3]
                end_lat = result.iloc[-1,4]
                end_lon = result.iloc[-1,3]
                print '*****'
                print start_lat
                print start_lon
                print end_lat
                print end_lon
                print '*****'
                distance1 = self.get_distance_hav(self.BuUnionLat, self.BuUnionLon, start_lat, start_lon)
                distance2 = self.get_distance_hav(self.BuUnionLat, self.BuUnionLon, end_lat, end_lon)
                print distance1
                print distance2
                if distance1 <= 150 and distance2 <= 150:
                    print 'In right scope'
                    break
                if distance1 > 150:
                    print 'last driver late'
                    start_time = self.get_new_time_range(start_time, 120)
                if distance2 > 150:
                    print 'not arrive'
                    end_time = self.get_new_time_range(end_time, 120)
            result.to_csv(os.path.join(self.PATH,list_schedule[2] + '_' + file_type + '.csv'))

Zh = ExtractMan()
# try_schedule = ['18:45,19:25,DCL_OUT_WS_IN','19:30,19:55,RRT','20:00,20:10,UP','20:15,20:55,WS_OUT_DCL_IN']
try_schedule = ['19:30,19:55,RRT']
Zh.data_extract('Gps.csv', try_schedule, Zh.SHUTTLE_NUM[1], '2017/8/23', 'gps')


