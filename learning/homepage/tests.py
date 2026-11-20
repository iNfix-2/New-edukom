from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.db import IntegrityError
from unittest.mock import patch
from uuid import uuid4
from .models import Guardian, AboutChild, Location, Lesson, GuardianEmail, Blog
from tutors.models import Tutor, TutorEmail
from .notifications import send_application_emails


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', OFFICIAL_NOTIFICATION_EMAILS=['team@example.com'])
class WorkflowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('reader')
        self.staff = get_user_model().objects.create_user('staff', is_staff=True)
        self.admin = get_user_model().objects.create_user('admin', is_staff=True, is_superuser=True)
        self.guardian = Guardian.objects.create(first_name='Example', last_name='Parent', email='parent@example.com')

    def guardian_data(self):
        return dict(first_name='Test', last_name='Parent', email='test@example.com', phone='+2348012345678', hear='Recommendation', lesson_type='Online lessons', curriculum=['British'], child_class='year 1', goal='Home schooling', subject=['Math'], about='Learning support', state='Abuja', street_address='Example street', days=['Monday'], start='2027-01-10', weeks=4, hour_per_day=1, start_time='12:00')

    def test_public_routes(self):
        for path in ('/', '/about/', '/courses/', '/Tutor/', '/Tutor/Join', '/Get_a_tutor/', '/contact/', '/blog/', '/account/Login/'):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

    def test_personal_records_require_staff(self):
        paths = ['/account/list', f'/account/detail/{self.guardian.uid}', '/guardians/', f'/guardian/{self.guardian.uid}']
        for user in (None, self.user, self.staff):
            self.client.logout()
            if user:
                self.client.force_login(user)
            for path in paths:
                with self.subTest(user=user, path=path):
                    self.assertEqual(self.client.get(path).status_code, 200 if user == self.staff else 302)
        tutor = Tutor.objects.create(first_name='Test', last_name='Tutor')
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(f'/account/tutor/detail/{tutor.uid}').status_code, 302)

    def test_missing_record_returns_404(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(f'/guardian/{uuid4()}').status_code, 404)
        self.assertEqual(self.client.get(f'/account/detail/{uuid4()}').status_code, 404)

    def test_blog_deletion_requires_post_and_csrf(self):
        post = Blog.objects.create(title='Example', slug='example')
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get('/blog/example/delete/').status_code, 405)
        self.assertTrue(Blog.objects.filter(pk=post.pk).exists())
        protected = Client(enforce_csrf_checks=True)
        protected.force_login(self.admin)
        self.assertEqual(protected.post('/blog/example/delete/').status_code, 403)
        self.client.force_login(self.user)
        self.assertEqual(self.client.post('/blog/example/delete/').status_code, 302)
        self.assertTrue(Blog.objects.filter(pk=post.pk).exists())
        self.client.force_login(self.admin)
        self.assertEqual(self.client.post('/blog/example/delete/').status_code, 302)
        self.assertFalse(Blog.objects.filter(pk=post.pk).exists())

    def test_guardian_application_and_receipt_do_not_resend(self):
        response = self.client.post('/Get_a_tutor/', self.guardian_data())
        self.assertEqual(response.status_code, 302)
        applicant = Guardian.objects.get(email='test@example.com')
        self.assertTrue(AboutChild.objects.filter(guardian=applicant).exists())
        self.assertTrue(Location.objects.filter(guardian=applicant).exists())
        self.assertTrue(Lesson.objects.filter(guardian=applicant).exists())
        self.assertTrue(GuardianEmail.objects.get(guardian=applicant).sent)
        self.assertEqual(len(mail.outbox), 2)
        for _ in range(2):
            self.assertEqual(self.client.get(response.url).status_code, 200)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(Client().get(response.url).status_code, 404)

    def test_tutor_application_and_receipt(self):
        data = self.guardian_data()
        data['teacher_class'] = data.pop('child_class')
        response = self.client.post('/Tutor/Join', data)
        self.assertEqual(response.status_code, 302)
        applicant = Tutor.objects.get(email='test@example.com')
        self.assertTrue(TutorEmail.objects.get(tutor=applicant).sent)
        self.assertContains(self.client.get(response.url), 'Test Parent')
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(Client().get(response.url).status_code, 404)

    def test_failed_application_rolls_back_related_records(self):
        before = Guardian.objects.count()
        with patch('homepage.models.Location.save', side_effect=IntegrityError('test rollback')):
            with self.assertRaises(IntegrityError):
                self.client.post('/Get_a_tutor/', self.guardian_data())
        self.assertEqual(Guardian.objects.count(), before)
        self.assertEqual(AboutChild.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_invalid_schedule_is_rejected(self):
        data = self.guardian_data()
        data.update(weeks=-1, hour_per_day=100)
        self.assertEqual(self.client.post('/Get_a_tutor/', data).status_code, 200)
        self.assertFalse(Guardian.objects.filter(email='test@example.com').exists())

    def test_notification_failure_is_retryable(self):
        with patch('homepage.notifications.EmailMessage.send', return_value=0):
            self.assertFalse(send_application_emails(self.guardian, 'guardian'))
        self.assertFalse(GuardianEmail.objects.filter(guardian=self.guardian, sent=True).exists())
        self.assertTrue(send_application_emails(self.guardian, 'guardian'))
        self.assertTrue(GuardianEmail.objects.get(guardian=self.guardian).sent)
        self.assertTrue(send_application_emails(self.guardian, 'guardian'))
        self.assertEqual(len(mail.outbox), 2)

    def test_dashboard_safely_serializes_post_titles(self):
        Blog.objects.create(title='</script><script>alert(1)</script>', slug='example')
        self.client.force_login(self.admin)
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '</script><script>alert(1)</script>')
        self.assertContains(response, 'application/json')

    def test_logout_requires_post(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get('/account/Logout/').status_code, 405)
        self.assertEqual(self.client.post('/account/Logout/').status_code, 302)

    def test_admin_pages_render_with_current_framework(self):
        self.client.force_login(self.admin)
        for path in ('/admin/', '/admin/homepage/guardian/', '/admin/tutors/tutor/'):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

    def test_template_static_references_resolve(self):
        import re
        from pathlib import Path
        from django.conf import settings
        from django.contrib.staticfiles import finders
        for template in (settings.BASE_DIR / 'temp').rglob('*.html'):
            for asset in re.findall(r"{%\s*static\s+['\"]([^'\"]+)['\"]\s*%}", template.read_text()):
                with self.subTest(template=template, asset=asset):
                    self.assertTrue(finders.find(asset), asset)

    def test_contact_is_preserved_when_notification_fails(self):
        from .models import Contact
        with patch('homepage.views.EmailMessage.send', return_value=0):
            response = self.client.post('/contact/', dict(name='Example', phone_number='+2348012345678', email='example@example.com', message='Support request'), follow=True)
        self.assertEqual(Contact.objects.count(), 1)
        self.assertContains(response, 'Your message has been saved for our team')

    def test_retry_command_skips_completed_notifications(self):
        from django.core.management import call_command
        from io import StringIO
        output = StringIO()
        call_command('retry_notifications', stdout=output)
        self.assertIn('0 failed', output.getvalue())
        self.assertEqual(len(mail.outbox), 2)
        call_command('retry_notifications', stdout=output)
        self.assertEqual(len(mail.outbox), 2)
