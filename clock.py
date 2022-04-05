from apscheduler.schedulers.blocking import BlockingScheduler

from checkNotification import getDataNotification

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=10)
def timed_job():
    getDataNotification()

sched.start()