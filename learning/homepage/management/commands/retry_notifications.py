from django.core.management.base import BaseCommand
from django.db.models import Q
from homepage.models import Guardian
from tutors.models import Tutor
from homepage.notifications import send_application_emails


class Command(BaseCommand):
    help = 'Retry application notifications that have no successful delivery record.'

    def handle(self, *args, **options):
        failed = 0
        for model, relation, kind in ((Guardian, 'GuardianEmail', 'guardian'), (Tutor, 'TutorEmail', 'tutor')):
            for applicant in model.objects.filter(Q(**{relation + '__isnull': True}) | Q(**{relation + '__sent': False})).iterator():
                if not send_application_emails(applicant, kind):
                    failed += 1
        self.stdout.write(f'Notification retries complete; {failed} failed. See server logs for details.')
