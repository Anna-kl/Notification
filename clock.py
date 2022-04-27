from apscheduler.schedulers.blocking import BlockingScheduler

from Client import client
from checkNotification import get_data_notification

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=10)
def timed_job():
    print('Start clock')
    c = client.get_token()
    get_data_notification(c)

sched.start()