from geopy.geocoders import Nominatim
import requests
import suncalc
import datetime
import pandas as pd

class moon_sun_db:

    def __init__(self, year=datetime.date.today().year):

        # Get current location coordinates based on your IP address
        loc = Nominatim(user_agent="GetLoc")
        # self.city = self.get_city()
        self.city = "Seattle"
        getLoc = loc.geocode(self.city)
        self.latitude = getLoc.latitude
        self.longitude = getLoc.longitude

        # Build this year's moon/sun DB
        self.db = {}

        self.year = year
        self.build_db(self.year)

    def get_city(self):
        ip_address = requests.get('https://api64.ipify.org?format=json').json()["ip"]
        response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
        return response.get("city")

    def build_db(self, year):

        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year + 1, 1, 1)

        def daterange(start_date, end_date):
            for n in range(int((end_date - start_date).days)):
                yield start_date + datetime.timedelta(n)

        for day in daterange(start_date, end_date):
            self.db[day] = suncalc.getTimes(day, self.latitude, self.longitude)
            self.db[day].update(suncalc.getMoonIllumination(day))
            self.db[day].update(suncalc.getMoonTimes(day, self.latitude, self.longitude))

            # Convert all string values to datetime values
            for data in self.db[day]:
                if isinstance(self.db[day][data], str):
                    self.db[day][data] = self.str_2_datetime(self.db[day][data])

    def str_2_datetime(self, datetime_str):
        date_format = '%Y-%m-%d %H:%M:%S'
        return datetime.datetime.strptime(datetime_str, date_format)

    def pandas_df(self):
        return pd.DataFrame.from_dict(self.db, orient='index')
