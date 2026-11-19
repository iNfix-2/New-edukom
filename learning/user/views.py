from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from homepage import models
from tutors import models as tmodels

@login_required
def GuardianListView(request):
    order = request.GET.get('order', 'desc')
    if order == 'asc':
        guardian = models.Guardian.objects.all().order_by('date_joined')
        tutor = tmodels.Tutor.objects.all().order_by('date_joined')
    else:
        guardian = models.Guardian.objects.all().order_by('-date_joined')
        tutor = tmodels.Tutor.objects.all().order_by('-date_joined')
        
    context = {
        'guardian': guardian,
        'tutor': tutor,
        'current_order': order
    }
    return render(request, 'Request/list.html', context)


@login_required
def GuardianDetailView(request, uid):
    guardian = models.Guardian.objects.get(uid=uid)
    context = {
        'guardian':guardian
    }
    return render(request, 'Request/details.html', context)



@login_required
def TutorDetailView(request, uid):
    tutor = tmodels.Tutor.objects.get(uid=uid)
    context = {
        'tutor':tutor
    }
    return render(request, 'Request/tutordetail.html', context)