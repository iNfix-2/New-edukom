from django.shortcuts import render, redirect
from . import forms
from . import models
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from homepage.notifications import send_application_emails


def community(request):
    return render(request, 'community.html')


def succes_form(request, uid):
    # A success receipt belongs to the browser that submitted the application.
    if str(uid) not in request.session.get('tutor_receipts', []):
        from django.http import Http404
        raise Http404
    tutor = get_object_or_404(models.Tutor, uid=uid)
    tutor.full_name = f"{tutor.first_name} {tutor.last_name}"
    return render(request, 'Forms/tutor_success.html', {'tutor': tutor})


def become_a_tutor(request):
    if request.method == "POST":
        Guform = forms.TutorForm(request.POST)
        Abform = forms.AboutTutorForm(request.POST)
        Loform = forms.LocationForm(request.POST)
        Leform = forms.LessonForm(request.POST)
        if Guform.is_valid() & Abform.is_valid() & Loform.is_valid() & Leform.is_valid():
            with transaction.atomic():
                applicant = Guform.save()
                for form in (Abform, Loform, Leform):
                    record = form.save(commit=False)
                    record.tutor = applicant
                    record.save()
            receipts = request.session.get('tutor_receipts', [])
            request.session['tutor_receipts'] = (receipts + [str(applicant.uid)])[-20:]
            send_application_emails(applicant, 'tutor')
            return redirect('tutor_succes_form', uid=applicant.uid)
    else:
        Guform = forms.TutorForm()
        Abform = forms.AboutTutorForm()
        Loform = forms.LocationForm()
        Leform = forms.LessonForm()

    form_context = {
        'Guform':Guform,
        'Abform':Abform,
        'Loform':Loform,
        'Leform':Leform,
    }
    return render(request, 'Forms/becomeatutor.html', form_context)
