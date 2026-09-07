from django.urls import path
from .views import project_add

from .views import PublicProjectListView

urlpatterns = [
    path(
        "public/projects/",
        PublicProjectListView.as_view(),
        name="public-project-list",
    ),
    path("projects/add/", project_add, name="project_add"),
]