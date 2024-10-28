from random import randint
import re
from datetime import datetime
import jdatetime
from datetime import datetime


def convert_gregorian_to_jalali(gregorian_date):
    jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
    day = jalali_date.day
    month = jalali_date.month
    year = jalali_date.year

    return f"{year}/{month}/{day}"


def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def check_valid_birth_date(date):
    date_pattern = r'^\d{4}/\d{2}/\d{2}$'
    return re.match(date_pattern, date) is not None


def get_random_number():
    return randint(10000, 99999)


def calculate_age(birth_date):
    if isinstance(birth_date, str):
        print(birth_date)
        birth_date = datetime.strptime(birth_date, '%Y-%m-%d')

    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    return f'{age} سال'


def send_sms_param(param, username, app="removebg"):
    url = "https://gateway.ghasedak.me/rest/api/v1/WebService/SendOtpSMS"
    data = {"template": app, "receptor": username, "param1": param, "type": 1}
    # requests.request("POST", url, headers=headers, data=data)
    # requests.post(URL, data=data, auth=HTTPBasicAuth("", ""))
    return True


DAYS_TRANSLATION = {
    'SA': 'شنبه',
    'SU': 'یکشنبه',
    'MO': 'دوشنبه',
    'TU': 'سه‌شنبه',
    'WE': 'چهارشنبه',
    'TH': 'پنج‌شنبه',
}
