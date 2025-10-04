from django.urls import include, path
from pest_control.views.process_occurence import ProcessOccurrenceApiView
from rest_framework.routers import DefaultRouter

app_name = "pest_control"

router = DefaultRouter()

urlpatterns = [
    path(
        "process/occurence/",
        ProcessOccurrenceApiView.as_view(),
        name="process-occurence"
    ),
    path("", include(router.urls))
]
