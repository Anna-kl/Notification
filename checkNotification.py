import json
from datetime import datetime, time, timedelta
from functools import reduce
import requests

from Client import client
from Models.SettingsDateTime import SettingsDateTime
from report import sendEmail

Week = [{'name': 'Понедельник', 'id': 1},
        {'name': 'Вторник', 'id': 2},
        {'name': 'Среда', 'id': 3},
        {'name': 'Четверг', 'id': 4},
        {'name': 'Пятница', 'id': 5},
        {'name': 'Суббота', 'id': 6},
        {'name': 'Воскресенье', 'id': 7}]
url = 'https://test.pmc.gpn.supply/api/contexts/1/notifications/'
#url = 'https://localhost:44321/api/contexts/1/notifications/'
c = client.get_token()

from sqlalchemy import create_engine, desc

engine = create_engine(
    'postgresql://dufuauvnmhhnbi:e04834417d5b33baf80de46ff78c145979019532d52e0019de70b1e83dbf36b6@ec2-34-254-69-72.eu-west-1.compute.amazonaws.com:5432/ddq1javfo02shs')
from sqlalchemy.orm import sessionmaker

session = sessionmaker()
session.configure(bind=engine)


def check_date_time(settings, last_state):
    if last_state is not None:
        if last_state.state:
            return False
        if last_state.createdatetime + timedelta(minutes=settings['interval']) > datetime.utcnow():
            return False

    day_of_week = settings['daysOfWeek']
    week_id = datetime.utcnow().isoweekday()

    for day in day_of_week:

        if len(list(filter(lambda item: item['name'] == day and item['id'] == week_id, Week))) != 0:
            start = get_time_from_str(settings['startPeriod'])

            end = get_time_from_str(settings['endPeriod'])

            if start <= datetime.utcnow() <= end:
                return True

    return False


def check_zero(settings, data):
    value = list(map(lambda x: x['count'], data))
    value = reduce(lambda x, key: x + key, value)
    end_period = get_time_from_str(settings['endPeriod'])

    if value == 0 and datetime.utcnow() < end_period:
        return False
    else:
        return True


def get_count_in_dict(last, current, key):
    for item1 in last:
        if item1['mtrType'] == key:
            find = next(filter(lambda x: x['mtrType'] == key, current))
            if find['count'] == item1['count']:
                return True
            else:
                return False


def get_days_check(settingsTime):
    day_of_week = settingsTime['daysOfWeek']
    week_id = datetime.utcnow().isoweekday()

    for day in day_of_week:
        if (len(list(filter(lambda item: item['name'] == day and item['id'] == week_id, Week))) != 0):
            return True
    return False


def check_send_email(setting_time):
    if get_days_check(setting_time) and setting_time['timeSendEmail']:
        end_check = get_time_from_str(setting_time['timeSendEmail'])
        if datetime.utcnow() >= end_check:
            return True

    return False


def send_email(settings_time, email, last_state):
    if last_state is not None:
        sendEmail(email,
                  json.loads(last_state.currentstate),
                  settings_time['startPeriod'],
                  settings_time['endPeriod'])
        last_state.state = True
    else:
        sendEmail(email,
                  None,
                  settings_time['startPeriod'],
                  settings_time['endPeriod'])


def get_time_from_str(date):
    if date:
        start_period = datetime.strptime(date.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        start_period = datetime.utcnow().replace(hour=start_period.hour,
                                              minute=start_period.minute)
        return start_period
    else:
        return date


def get_data_notification():
    print('start proccess')
    headers = {'Authorization':
                   'Bearer {}'.format(c['access_token']),
               'Content-type': 'application/json'}
    r = requests.get('{0}any-user/'.format(url), headers=headers, verify=False)
    print(r.status_code, r.content)
    notifications = json.loads(r.content)

    main_session = session()

    for notification in notifications:
        settings_time = json.loads(notification['settingsDateTime'])
        last_state = main_session.query(SettingsDateTime) \
            .filter(SettingsDateTime.notificationid == notification['id']) \
            .order_by(desc(SettingsDateTime.createdatetime)) \
            .first()

        if last_state is not None:
            if last_state.createdatetime.date() != datetime.today().date():
                last_state = None
        if last_state is not None:
            if check_send_email(settings_time) and last_state.state is False:
                send_email(settings_time, notification['settingsSend'], last_state)
                main_session.add(last_state)
                main_session.commit()
                continue

        if check_date_time(settings_time, last_state):
            start_period = get_time_from_str(settings_time['startPeriod'])


            send = {
                'startPeriod': start_period.strftime('%Y-%m-%dT%H:%M:%S'),
                'notificationId': notification['id'],
                'mtrItemsTypes': json.loads(notification['mtrTypes'])
            }
            r = requests.post('{0}check-state/'.format(url), data=json.dumps(send), headers=headers, verify=False)

            data_mtr_items_current = json.loads(r.content.decode('utf8'))

            indicators = json.loads(notification['mtrTypes'])
            checked_state = 0
            if last_state is None:
                current_state = SettingsDateTime(notificationid=notification['id'],
                                                 currentstate=json.dumps(data_mtr_items_current),
                                                 state=False, createdatetime=datetime.utcnow())

            else:
                if not check_zero(settings_time, data_mtr_items_current):
                    continue


                for mtrType in indicators:
                    data_mtr_items_last = json.loads(last_state.currentstate)
                    if get_count_in_dict(data_mtr_items_last, data_mtr_items_current, mtrType):
                        checked_state += 1
                if checked_state == len(indicators):
                    current_state = SettingsDateTime(notificationid=notification['id'],
                                                     currentstate=json.dumps(data_mtr_items_current),
                                                     state=False, createdatetime=datetime.utcnow())
                    if settings_time['timeSendEmail'] is None \
                            or get_time_from_str(settings_time['startPeriod']) > datetime.utcnow():
                        send_email(settings_time,
                                   notification['settingsSend'],
                                   current_state)
                        print('Письмо отправлено')

                else:
                    current_state = SettingsDateTime(notificationid=notification['id'],
                                                     currentstate=json.dumps(data_mtr_items_current, ensure_ascii=True),
                                                     state=False, createdatetime=datetime.utcnow())
            main_session.add(current_state)
            main_session.commit()
            print('Проверка завершена')


def datetime_to_local_timezone(dt):
    epoch = dt.timestamp()  # Get POSIX timestamp of the specified datetime.
    st_time = time.localtime(
        epoch)  # Get struct_time for the timestamp. This will be created using the system's locale and it's time zone information.
    tz = datetime.timezone(datetime.timedelta(
        seconds=st_time.tm_gmtoff))  # Create a timezone object with the computed offset in the struct_time.

    return dt.astimezone(tz)  # Move the datetime instance to the new time zone.


# sendEmail('akklimova@gmail.com')
get_data_notification()
