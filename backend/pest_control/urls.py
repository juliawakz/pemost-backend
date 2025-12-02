from django.urls import include, path
from pest_control.views.occurence import PestOccurrenceListView
from pest_control.views.process_occurence import ProcessOccurrenceApiView
from rest_framework.routers import DefaultRouter

app_name = "pest_control"

router = DefaultRouter()

urlpatterns = [
    path(
        "occurences/",
        PestOccurrenceListView.as_view(),
        name="occurence-list"
    ),
    path(
        "process/occurence/",
        ProcessOccurrenceApiView.as_view(),
        name="process-occurence"
    ),
    path("", include(router.urls))
]
