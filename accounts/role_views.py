from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .views import is_admin


PERMISSION_LABELS = {
    "view_project": "View Projects — Map and List",
    "add_project": "Add Projects",
    "change_project": "Edit Projects",
    "delete_project": "Delete Projects",
}


class ProjectPermissionField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, permission):
        return PERMISSION_LABELS[permission.codename]


class RoleForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        label="Role Name",
    )

    permissions = ProjectPermissionField(
        queryset=Permission.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Project Permissions",
    )

    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance

        allowed = Permission.objects.filter(
            content_type__app_label="projects",
            content_type__model="project",
            codename__in=PERMISSION_LABELS,
        ).order_by("codename")

        self.fields["permissions"].queryset = allowed

        if instance:
            self.initial["name"] = instance.name
            self.initial["permissions"] = list(
                instance.permissions.filter(
                    pk__in=allowed.values("pk")
                ).values_list("pk", flat=True)
            )

    def clean_name(self):
        name = self.cleaned_data["name"].strip()

        if name.casefold() == "admin":
            raise forms.ValidationError(
                "Admin is a protected role. Choose another name."
            )

        duplicates = Group.objects.filter(name__iexact=name)

        if self.instance:
            duplicates = duplicates.exclude(pk=self.instance.pk)

        if duplicates.exists():
            raise forms.ValidationError(
                "A role with this name already exists."
            )

        return name

    def clean(self):
        cleaned = super().clean()
        permissions = cleaned.get("permissions")

        if permissions is not None:
            codes = {
                permission.codename
                for permission in permissions
            }

            if (
                codes & {
                    "add_project",
                    "change_project",
                    "delete_project",
                }
                and "view_project" not in codes
            ):
                self.add_error(
                    "permissions",
                    "Select View Projects when allowing Add, Edit or Delete.",
                )

        return cleaned

    @transaction.atomic
    def save(self):
        role = self.instance or Group()
        role.name = self.cleaned_data["name"]
        role.save()
        role.permissions.set(self.cleaned_data["permissions"])
        return role


@login_required
@require_http_methods(["GET", "POST"])
def role_manage(request, role_id=None):
    if not is_admin(request.user):
        raise PermissionDenied

    role = None

    if role_id is not None:
        role = get_object_or_404(Group, pk=role_id)

        if role.name.casefold() == "admin":
            raise PermissionDenied

    if request.method == "POST":
        form = RoleForm(request.POST, instance=role)

        if form.is_valid():
            form.save()
            return redirect("accounts:role_list")
    else:
        form = RoleForm(instance=role)

    allowed_permission_ids = set(
        form.fields["permissions"].queryset.values_list(
            "pk", flat=True
        )
    )

    groups = Group.objects.prefetch_related(
        "permissions"
    ).order_by("name")

    rows = []

    for group in groups:
        protected = group.name.casefold() == "admin"

        permission_codes = {
            permission.codename
            for permission in group.permissions.all()
            if permission.pk in allowed_permission_ids
        }

        labels = [
            label
            for code, label in PERMISSION_LABELS.items()
            if code in permission_codes
        ]

        rows.append({
            "role": group,
            "protected": protected,
            "labels": labels,
        })

    return render(
        request,
        "accounts/roles.html",
        {
            "form": form,
            "editing_role": role,
            "rows": rows,
        },
    )