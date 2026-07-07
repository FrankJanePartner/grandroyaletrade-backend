from django.urls import path

from .views import ProcessROIAPIView

urlpatterns = [
    path(
        "process-roi/",
        ProcessROIAPIView.as_view(),
    ),
    path(
    "api/cron/",
    include("cronjobs.urls"),
),
]