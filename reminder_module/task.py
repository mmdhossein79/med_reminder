from apscheduler.schedulers.background import BackgroundScheduler
from reminder_module.schedular import send_medication_reminders, send_reservation_reminders


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_medication_reminders, 'interval', minutes=1)  # Check every hour

    scheduler.start()

# You may want to call this function from your Django app’s ready method.
def start_scheduler_reserve():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_reservation_reminders, 'interval', minutes=1)  # Check every hour

    scheduler.start()
