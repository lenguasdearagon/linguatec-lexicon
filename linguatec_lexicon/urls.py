from django.conf.urls import include, url
from django.urls import path
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register(r'words', views.WordViewSet)

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(router.urls)),
    path('validator/', views.DataValidatorView.as_view(), name='validator')
]
