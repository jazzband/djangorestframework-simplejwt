from django.conf.urls import url
from rest_framework_simplejwt import views as jwt_views

from . import views

urlpatterns = [
    url(r'^token/obtain/$', jwt_views.token_obtain_sliding, name='token_obtain_sliding'),
    url(r'^token/refresh/$', jwt_views.token_refresh_sliding, name='token_refresh_sliding'),

    url(r'^test-view/$', views.test_view, name='test_view'),
]
