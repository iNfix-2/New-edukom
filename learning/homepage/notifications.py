"""Notification delivery status is recorded only after both emails are accepted."""
import logging
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .models import GuardianEmail
from tutors.models import TutorEmail

logger = logging.getLogger(__name__)


def send_application_emails(applicant, kind):
    model = GuardianEmail if kind == 'guardian' else TutorEmail
    lookup = {kind: applicant}
    if model.objects.filter(**lookup, sent=True).exists():
        return True
    applicant.full_name = f'{applicant.first_name} {applicant.last_name}'
    templates = ('gaurdian_sucess', 'guardiantoadmin') if kind == 'guardian' else ('tutorsucess', 'tutortoadmin')
    try:
        for template, recipients in zip(templates, ([applicant.email], settings.OFFICIAL_NOTIFICATION_EMAILS)):
            message = EmailMessage('Welcome to Edukom', render_to_string(f'emails/{template}.html', {kind: applicant}), settings.DEFAULT_FROM_EMAIL, recipients)
            message.content_subtype = 'html'
            if message.send(fail_silently=False) != 1:
                raise RuntimeError('Mail backend did not accept the notification')
        model.objects.update_or_create(**lookup, defaults={'sent': True})
        return True
    except Exception:
        logger.exception('Application notification failed for %s %s', kind, applicant.uid)
        return False
