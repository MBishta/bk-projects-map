from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project

        fields = (
            "reference",
            "public_name",
            "client_name",
            "work_type",
            "area",
            "description",
            "latitude",
            "longitude",
            "is_public",
        )

        labels = {
            "reference": "Project Reference",
            "public_name": "Public Project Name",
            "client_name": "Client Name",
            "work_type": "Work Type",
            "area": "Area",
            "description": "Public Description",
            "latitude": "Latitude",
            "longitude": "Longitude",
            "is_public": "Show on Public Map",
        }

        help_texts = {
            "reference": "Enter a unique project number or reference.",
            "public_name": "This name will appear on the public map.",
            "client_name": "Internal information. Not shown on the public map.",
            "description": "Shown publicly when the project is published.",
            "latitude": "Choose a location on the map or enter coordinates.",
            "is_public": "Allow visitors to view this project without signing in.",
        }

        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "latitude": forms.NumberInput(attrs={
                "step": "0.000001",
                "min": "-90",
                "max": "90",
            }),
            "longitude": forms.NumberInput(attrs={
                "step": "0.000001",
                "min": "-180",
                "max": "180",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["work_type"].choices = [
            ("", "Select work type"),
            ("structure", "Structure"),
            ("finishing", "Finishing"),
            ("both", "Structure & Finishing"),
        ]