from urllib.parse import urlencode
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.html import format_html
from django.contrib import messages
from .forms import ContactForm
import logging
logger = logging.getLogger(__name__)

# Configurable Learning platform URL
LEARNING_PLATFORM_URL = getattr(settings, 'LEARNING_PLATFORM_URL', 'https://learning.edukom.ng/')


@ensure_csrf_cookie
def gateway_home(request: HttpRequest) -> HttpResponse:
    """Landing page for edukom.ng connecting Edukom HR and Edukom Learning."""
    context = {
        'learning_url': LEARNING_PLATFORM_URL,
    }
    return render(request, 'core/gateway.html', context)


@ensure_csrf_cookie
def hr_home(request: HttpRequest) -> HttpResponse:
    """Main Edukom HR landing page with all 01-04 sections and content on one page."""
    context = {
        'learning_url': LEARNING_PLATFORM_URL,
    }
    return render(request, 'core/index.html', context)


def learning_redirect(request: HttpRequest) -> HttpResponse:
    """Direct navigation route to Edukom Learning Platform."""
    return redirect(LEARNING_PLATFORM_URL)


def learning_path_redirect(request: HttpRequest, prefix: str = '', subpath: str = '') -> HttpResponse:
    """Redirect learning paths (such as account/, Tutor/, guardians/) from edukom.ng to learning platform."""
    base = LEARNING_PLATFORM_URL.rstrip('/')
    target = f"{base}{request.get_full_path()}"
    return HttpResponseRedirect(target)


def contact(request: HttpRequest) -> HttpResponse:
    if request.method != 'POST':
        return redirect('home')

    form = ContactForm(request.POST)
    if request.POST.get('website'):
        return HttpResponseRedirect(f"{reverse('home')}?sent=1#contact")
    if not form.is_valid():
        messages.error(request, 'Please provide a valid name, email address and message (up to 5,000 characters).')
        return HttpResponseRedirect(f"{reverse('home')}?sent=0#contact")
    name = form.cleaned_data['name']
    email = form.cleaned_data['email']
    subject = form.cleaned_data['subject'] or 'New Contact Form Submission'
    message = form.cleaned_data['message']
    body_html = format_html('<p><strong>Name:</strong> {}</p><p><strong>Email:</strong> {}</p><p><strong>Message:</strong></p><p>{}</p>', name, email, message)
    body_text = f"Name: {name}\nEmail: {email}\nMessage:\n{message}"

    try:
        send_mail(
            subject,
            body_text,
            settings.DEFAULT_FROM_EMAIL,
            [getattr(settings, 'CONTACT_TO_EMAIL', settings.DEFAULT_FROM_EMAIL)],
            html_message=body_html,
            fail_silently=False,
        )
        messages.success(request, 'Your message has been sent. Our team will be in touch.')
        query = urlencode({'sent': 1})
    except Exception:
        logger.exception('Contact email failed')
        messages.error(request, 'We could not send your message. Please try again or contact us by phone.')
        query = urlencode({'sent': 0})

    return HttpResponseRedirect(f"{reverse('home')}?{query}#contact")


def robots_txt(request: HttpRequest) -> HttpResponse:
    lines = [
        "User-agent: *",
        "Allow: /",
        "Sitemap: https://edukom.ng/sitemap.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request: HttpRequest) -> HttpResponse:
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://edukom.ng/</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://edukom.ng/hr/</loc>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
</urlset>"""
    return HttpResponse(content, content_type="application/xml")
