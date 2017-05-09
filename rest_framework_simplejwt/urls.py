from __future__ import unicode_literals

from django.conf.urls import url

from . import views

app_name = 'rest_framework_simplejwt'

urlpatterns = [
    url(r'^token/obtain/$', views.token_obtain, name='token_obtain'),
    url(r'^token/refresh/$', views.token_refresh, name='token_refresh'),
]
