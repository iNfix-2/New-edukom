from django.test import TestCase, override_settings
from django.core import mail
from django.contrib.staticfiles import finders
from django.contrib.auth import get_user_model
from blog.models import Post
from unittest.mock import patch


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class SiteTests(TestCase):
    def test_public_routes_and_static_asset(self):
        for path in ('/', '/hr/', '/blog/', '/accounts/login/'):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)
        self.assertTrue(finders.find('site.css'))

    def test_contact_validates_data_before_sending(self):
        response = self.client.post('/contact/', {'name': 'Example', 'email': 'invalid', 'message': 'Hello'}, follow=True)
        self.assertContains(response, 'Please provide a valid')
        self.assertEqual(len(mail.outbox), 0)

    def test_contact_escapes_email_html(self):
        response = self.client.post('/contact/', {'name': '<b>Example</b>', 'email': 'example@example.com', 'message': '<script>alert(1)</script>'}, follow=True)
        self.assertContains(response, 'Your message has been sent')
        self.assertEqual(len(mail.outbox), 1)
        self.assertNotIn('<script>', mail.outbox[0].alternatives[0][0])
        self.assertIn('&lt;script&gt;', mail.outbox[0].alternatives[0][0])

    def test_contact_failure_is_visible(self):
        with patch('core.views.send_mail', side_effect=RuntimeError('test failure')):
            response = self.client.post('/contact/', {'name': 'Example', 'email': 'example@example.com', 'message': 'Hello'}, follow=True)
        self.assertContains(response, 'We could not send your message')

    def test_staff_navigation_and_draft_save(self):
        user = get_user_model().objects.create_user('editor', is_staff=True)
        self.client.force_login(user)
        self.assertEqual(self.client.get('/').status_code, 200)
        response = self.client.post('/blog/new/', {'title': 'Draft example', 'content': 'Draft body'})
        self.assertRedirects(response, '/blog/manage/')
        self.assertFalse(Post.objects.get().published)

    def test_blog_content_sanitization(self):
        post = Post.objects.create(title='Example', content='<p>Text</p><script>alert(1)</script><a href="javascript:alert(1)">Link</a>')
        response = self.client.get(post.get_absolute_url())
        self.assertContains(response, '<p>Text</p>')
        self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertNotContains(response, 'href="javascript:')

    def test_ordinary_user_cannot_publish(self):
        self.client.force_login(get_user_model().objects.create_user('reader'))
        self.assertEqual(self.client.get('/blog/new/').status_code, 302)

    def test_management_lists_posts_and_pagination_has_no_duplicates(self):
        for i in range(15):
            Post.objects.create(title=f'Article {i}', content='Body')
        first = self.client.get('/blog/')
        second = self.client.get('/blog/?page=2')
        ids1 = {p.pk for p in first.context['posts']}
        ids2 = {p.pk for p in second.context['posts']}
        self.assertFalse(ids1 & ids2)
        self.client.force_login(get_user_model().objects.create_user('manager', is_staff=True))
        response = self.client.get('/blog/manage/')
        self.assertContains(response, 'Article 0')
        self.assertContains(response, 'Edit')

    def test_template_static_references_resolve(self):
        import re
        from pathlib import Path
        from django.conf import settings
        from django.contrib.staticfiles import finders
        for template in (settings.BASE_DIR / 'templates').rglob('*.html'):
            for asset in re.findall(r"{%\s*static\s+['\"]([^'\"]+)['\"]\s*%}", template.read_text()):
                with self.subTest(template=template, asset=asset):
                    self.assertTrue(finders.find(asset), asset)
