from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "public_name",
        "work_type",
        "area",
        "is_public",
    )
    list_filter = ("work_type", "is_public")
    search_fields = ("reference", "public_name", "client_name", "area")
    readonly_fields = ("id", "created_at", "updated_at")