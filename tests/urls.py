from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^api/', include('rest_framework_simplejwt.urls')),

    url(r'^test-view/$', views.test_view, name='test_view'),
]
