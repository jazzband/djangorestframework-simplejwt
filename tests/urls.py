from django.conf.urls import url
from rest_framework_simplejwt import views as jwt_views

from . import views

urlpatterns = [
    url(r'^token/pair/$', jwt_views.token_obtain_pair, name='token_obtain_pair'),
    url(r'^token/refresh/$', jwt_views.token_refresh, name='token_refresh'),

    url(r'^token/sliding/$', jwt_views.token_obtain_sliding, name='token_obtain_sliding'),
    url(r'^token/sliding/refresh/$', jwt_views.token_refresh_sliding, name='token_refresh_sliding'),

    url(r'^token/verify/$', jwt_views.token_verify, name='token_verify'),

    url(r'^test-view/$', views.test_view, name='test_view'),
]
