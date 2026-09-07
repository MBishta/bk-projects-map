from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from .forms import ProjectForm
from .models import Project
from .serializers import PublicProjectSerializer


class PublicProjectListView(ListAPIView):
    serializer_class = PublicProjectSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    queryset = Project.objects.filter(is_public=True)


@login_required
@permission_required("projects.add_project", raise_exception=True)
def project_add(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("project-list")
    else:
        form = ProjectForm()

    return render(
        request,
        "projects/project_form.html",
        {
            "form": form,
            "is_edit": False,
        },
    )


@login_required
@permission_required("projects.view_project", raise_exception=True)
def project_list(request):
    query = request.GET.get("q", "").strip()
    projects = Project.objects.all().order_by("reference")

    if query:
        projects = projects.filter(
            Q(reference__icontains=query)
            | Q(public_name__icontains=query)
            | Q(client_name__icontains=query)
            | Q(area__icontains=query)
        )

    can_delete_projects = request.user.has_perm(
        "projects.delete_project"
    )

    return render(
        request,
        "projects/project_list.html",
        {
            "projects": projects,
            "query": query,
            "can_delete_projects": can_delete_projects,
        },
    )


@login_required
@permission_required("projects.change_project", raise_exception=True)
def project_edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            form.save()
            return redirect("project-list")
    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        "projects/project_form.html",
        {
            "form": form,
            "project": project,
            "is_edit": True,
        },
    )


@login_required
@permission_required("projects.delete_project", raise_exception=True)
@require_http_methods(["GET", "POST"])
def project_delete(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        return redirect("project-list")

    return render(
        request,
        "projects/project_confirm_delete.html",
        {"project": project},
    )


@login_required
@permission_required("projects.view_project", raise_exception=True)
def project_location(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    location = {
        "name": project.public_name,
        "reference": project.reference,
        "latitude": float(project.latitude),
        "longitude": float(project.longitude),
    }

    return render(
        request,
        "projects/project_location.html",
        {
            "project": project,
            "location": location,
        },
    )


@login_required
@permission_required("projects.view_project", raise_exception=True)
def projects_map(request):
    map_projects = PublicProjectSerializer(
        Project.objects.all().order_by("reference"),
        many=True,
    ).data

    return render(
        request,
        "projects/map.html",
        {
            "internal_map": True,
            "map_projects": map_projects,
        },
    )