from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from projects.views import (
    project_add,
    project_delete,
    project_edit,
    project_list,
    project_location,
    projects_map,
)


urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="projects/map.html"),
        name="public-map",
    ),
    path("accounts/", include("accounts.urls")),
    path("admin/", admin.site.urls),
    path("api/v1/", include("projects.urls")),
    path(
        "projects/add/",
        project_add,
        name="project-create",
    ),
    path(
        "projects/",
        project_list,
        name="project-list",
    ),
    path(
        "projects/<uuid:project_id>/edit/",
        project_edit,
        name="project-edit",
    ),
    path(
        "projects/<uuid:project_id>/delete/",
        project_delete,
        name="project-delete",
    ),
    path(
        "projects/<uuid:project_id>/map/",
        project_location,
        name="project-location",
    ),
    path(
        "projects/map/",
        projects_map,
        name="projects-map",
    ),
]