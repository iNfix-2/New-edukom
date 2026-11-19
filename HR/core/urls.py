from django.urls import path
from . import views

urlpatterns = [
    path('', views.gateway_home, name='gateway_home'),
    path('hr/', views.hr_home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('send-email.php', views.contact, name='legacy_contact'),
    path('learning/', views.learning_redirect, name='learning_redirect'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),

    # Redirect learning routes (from email links or legacy bookmarks) directly to learning platform
    path('account/', views.learning_path_redirect, {'prefix': 'account'}, name='account_redirect_root'),
    path('account/<path:subpath>', views.learning_path_redirect, {'prefix': 'account'}, name='account_redirect'),
    path('Tutor/', views.learning_path_redirect, {'prefix': 'Tutor'}, name='tutor_redirect_root'),
    path('Tutor/<path:subpath>', views.learning_path_redirect, {'prefix': 'Tutor'}, name='tutor_redirect'),
    path('guardians/', views.learning_path_redirect, {'prefix': 'guardians'}, name='guardians_redirect'),
    path('guardian/<path:subpath>', views.learning_path_redirect, {'prefix': 'guardian'}, name='guardian_redirect'),
]
