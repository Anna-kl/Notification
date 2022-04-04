import json
from datetime import datetime, time, timedelta
from functools import reduce
import smtplib, ssl
import requests

from Client import client
from Models.SettingsDateTime import SettingsDateTime
from report import sendEmail

Week = [{ 'name':'Понедельник', 'id': 1},
     {'name':'Вторник', 'id':2},
     {'name':'Среда', 'id': 3},
     {'name':'Четверг', 'id': 4},
        {'name': 'Пятница', 'id': 5 },
        {'name': 'Суббота', 'id': 6},
        {'name':'Воскресенье', 'id': 7}]
url = 'https://localhost:44321/api/contexts/1/notification/'
c=client.get_token()

from sqlalchemy import create_engine, desc

engine=create_engine('postgresql+psycopg2://postgres:2537300@localhost:5432/dashboards')
from  sqlalchemy.orm import sessionmaker
session=sessionmaker()
session.configure(bind=engine)




def checkDateTime(settings):
    day_of_week = settings['daysOfWeek']
    week_id =  datetime.now().isoweekday()

    for day in day_of_week:

        if (len(list(filter(lambda item: item['name'] == day and item['id'] == week_id, Week))) != 0):
            start = datetime.strptime(settings['startPeriod'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
            end = datetime.strptime(settings['endPeriod'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
            start = datetime.now().replace(hour=(start.hour+3)%24, minute=start.minute)
            end = datetime.now().replace(hour=(end.hour+3)%24, minute=end.minute)
            if datetime.now() >= start and datetime.now() <= end:
                return True



    return False

def checkCount(settings, data):
    value = list(map(lambda x: x['count'], data))
    value = reduce(lambda x, key: x+key, value)
    endPeriod = datetime.strptime(settings['endPeriod'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
    endPeriod = datetime.now().replace(hour=(endPeriod.hour+3)%24, minute=endPeriod.minute)
    if value == 0 and datetime.now() < endPeriod:
        return False
    else:
        return True


def getCountInDict(last, current, key):
    for item1 in last:
       if item1['mtrType'] == key:
           find = next(filter(lambda x: x['mtrType'] == key, current))
           if find['count'] == item1['count']:
               return True
           else:
               return False



def getDataNotification():
    headers = {'Authorization':
                   'Bearer {}'.format(c['access_token']),
               'Content-type': 'application/json'}
    r = requests.get('{0}getAll/'.format(url), headers=headers, verify=False)
    notifications = json.loads(r.content.decode('utf8'))

    mainSession = session()


    for notification in notifications:
        settingTime = json.loads(notification['settingsDateTime'])
        if checkDateTime(settingTime):
            lastState = mainSession.query(SettingsDateTime)\
                .filter(SettingsDateTime.notificationid == notification['id'])\
                .order_by(desc(SettingsDateTime.createdatetime))\
                .first()

            if lastState is not None:
                if lastState.createdatetime.date() != datetime.today().date():
                    lastState = None

            if lastState is not None:
                if lastState.state:
                    continue
                if lastState.createdatetime + timedelta(minutes=settingTime['interval'])>datetime.now():
                    continue
            startPeriod = datetime.strptime(settingTime['startPeriod'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
            startPeriod  = datetime.now().replace(hour=(startPeriod.hour + 3) % 24,
                                                      minute=startPeriod.minute)

            endPeriod = datetime.strptime(settingTime['endPeriod'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
            endPeriod = datetime.now().replace(hour=(endPeriod.hour + 3) % 24,
                                                 minute=endPeriod.minute)

            send = {
                'startPeriod': startPeriod.strftime('%Y-%m-%dT%H:%M:%S'),
                'notificationId': notification['id'],
                'mtrItemsTypes': json.loads(notification['indicators'])
            }
            r = requests.post('{0}checkState/'.format(url), data=json.dumps(send), headers=headers, verify=False)

            dataMtrItemsCurrent = json.loads(r.content.decode('utf8'))

            indicators = json.loads(notification['indicators'])
            checkedState = 0
            if lastState is None:
                currentState = SettingsDateTime(notificationid=notification['id'],
                                                currentstate=r.content.decode('utf8'),
                                                state=False, createdatetime=datetime.now())

            else:
                dataMtrItemLast = json.loads(lastState.currentstate)
                if checkCount(settingTime, dataMtrItemsCurrent) == False:
                    continue

                for mtrType in indicators:
                    if getCountInDict(dataMtrItemLast, dataMtrItemsCurrent, mtrType):
                        checkedState += 1
                if checkedState == len(indicators):
                    currentState = SettingsDateTime(notificationid=notification['id'],
                                                    currentstate=r.content.decode('utf8'),
                                                    state=True, createdatetime=datetime.now())
                    sendEmail(notification['settingsSend'],
                              dataMtrItemLast,
                              startPeriod,
                              endPeriod)


                else:
                    currentState = SettingsDateTime(notificationid=notification['id'], currentstate=r.content.decode('utf8'),
                                                state=False, createdatetime=datetime.now())
            mainSession.add(currentState)
            mainSession.commit()

def datetime_to_local_timezone(dt):
    epoch = dt.timestamp() # Get POSIX timestamp of the specified datetime.
    st_time = time.localtime(epoch) #  Get struct_time for the timestamp. This will be created using the system's locale and it's time zone information.
    tz = datetime.timezone(datetime.timedelta(seconds = st_time.tm_gmtoff)) # Create a timezone object with the computed offset in the struct_time.

    return dt.astimezone(tz) # Move the datetime instance to the new time zone.

#sendEmail('akklimova@gmail.com')
getDataNotification()