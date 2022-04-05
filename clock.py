from apscheduler.schedulers.blocking import BlockingScheduler

from checkNotification import getDataNotification

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=1)
def timed_job():
    print('Start clock')
    getDataNotification()

sched.start()