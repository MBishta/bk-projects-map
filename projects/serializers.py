from rest_framework import serializers

from .models import Project


class PublicProjectSerializer(serializers.ModelSerializer):
    work_type_label = serializers.CharField(
        source="get_work_type_display",
        read_only=True,
    )

    class Meta:
        model = Project
        fields = (
            "id",
            "reference",
            "public_name",
            "work_type",
            "work_type_label",
            "area",
            "description",
            "latitude",
            "longitude",
        )
        read_only_fields = fields