from __future__ import unicode_literals

from django.conf.urls import url

from . import views

app_name = 'rest_framework_simplejwt'

urlpatterns = [
    url(r'^token/obtain/$', views.token_obtain, name='token_obtain'),
]
