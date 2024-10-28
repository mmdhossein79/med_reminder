from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_email(subject, to, context,template_name):
    html_message = render_to_string(f'account_module/{template_name}', context)
    plain_message = strip_tags(html_message)
    from_email = 'medicalznu.co@gmail.com' # Ensure this is set in settings.py
    send_mail(subject, plain_message, from_email, [to], html_message=html_message)
