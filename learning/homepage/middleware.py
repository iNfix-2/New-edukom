from django.utils import timezone
from django.db.models import F
from .models import SiteTraffic

class SiteTrafficMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method == 'GET' and response.status_code == 200 and response.get('Content-Type', '').startswith('text/html') and not request.path_info.startswith(('/admin/', '/account/', '/guardian', '/dashboard/', '/Assets/', '/media/')):
            obj, _ = SiteTraffic.objects.get_or_create(date=timezone.localdate())
            SiteTraffic.objects.filter(pk=obj.pk).update(views=F('views') + 1)
        return response
