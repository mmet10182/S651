from django.urls import path
from . import views


urlpatterns = [
    path('api/v1/hosts/<uid>/disks/report', views.ApiV1HostDiskReport.as_view(), name='apiV1_host_disk_report'),
]