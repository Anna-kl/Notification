from apscheduler.schedulers.blocking import BlockingScheduler

from checkNotification import get_data_notification

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=10)
def timed_job():
    print('Start clock')
    get_data_notification()

sched.start()