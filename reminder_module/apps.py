from django.apps import AppConfig


class ReminderModuleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reminder_module'

    def ready(self):

        from reminder_module.task import start_scheduler
        start_scheduler()

        from reminder_module.task import start_scheduler_reserve
        start_scheduler_reserve()
# your_app/apps.py
