from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = "Create the project map user roles."

    @transaction.atomic
    def handle(self, *args, **options):
        roles = {
            "Admin": {
                ("projects", "project"): [
                    "view_project",
                    "add_project",
                    "change_project",
                    "delete_project",
                ],
                ("auth", "user"): [
                    "view_user",
                    "add_user",
                    "change_user",
                    "delete_user",
                ],
            },
            "User": {
                ("projects", "project"): [
                    "view_project",
                    "add_project",
                    "change_project",
                ],
            },
            "Viewer": {
                ("projects", "project"): [
                    "view_project",
                ],
            },
        }

        for role_name, models in roles.items():
            permissions = []

            for (app_label, model_name), codenames in models.items():
                for codename in codenames:
                    try:
                        permission = Permission.objects.get(
                            content_type__app_label=app_label,
                            content_type__model=model_name,
                            codename=codename,
                        )
                    except Permission.DoesNotExist:
                        raise CommandError(
                            f"Missing permission: {app_label}.{codename}. "
                            "Run migrate first."
                        )

                    permissions.append(permission)

            group, _ = Group.objects.get_or_create(name=role_name)
            group.permissions.set(permissions)

            self.stdout.write(
                self.style.SUCCESS(f"Role ready: {role_name}")
            )