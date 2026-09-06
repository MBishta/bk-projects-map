from django.urls import path

from .views import PublicProjectListView

urlpatterns = [
    path(
        "public/projects/",
        PublicProjectListView.as_view(),
        name="public-project-list",
    ),
]