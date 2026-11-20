from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from homepage import models
from tutors import models as tmodels

@staff_member_required(login_url="login")
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


@staff_member_required(login_url="login")
def GuardianDetailView(request, uid):
    guardian = get_object_or_404(models.Guardian, uid=uid)
    context = {
        'guardian':guardian
    }
    return render(request, 'Request/details.html', context)



@staff_member_required(login_url="login")
def TutorDetailView(request, uid):
    tutor = get_object_or_404(tmodels.Tutor, uid=uid)
    context = {
        'tutor':tutor
    }
    return render(request, 'Request/tutordetail.html', context)
