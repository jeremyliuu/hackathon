from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import admin
admin.autodiscover()

import views


urlpatterns = [
    url(r'^setup/$', views.SetupView.as_view(), name='setup'),
    url(r'^welcome/$', views.doctor_welcome, name='setup'),
    url(r'^check_in/$', views.check_in_patients, name='check_in'),
    url(r'^update/$', views.update_status, name='update'),
    url(r'^select/$', views.select_appointments, name='select'),
    url(r'^info/$', views.demographic_info, name='info'),
    url(r'^success/$', views.successfully_check_in, name='success'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
]