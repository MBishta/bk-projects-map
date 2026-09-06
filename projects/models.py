import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Project(models.Model):
    class WorkType(models.TextChoices):
        STRUCTURE = "structure", "عظم"
        FINISHING = "finishing", "تشطيب"
        BOTH = "both", "عظم وتشطيب"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    reference = models.CharField("رقم المشروع", max_length=50, unique=True)
    public_name = models.CharField("اسم العرض", max_length=200)
    client_name = models.CharField("اسم العميل الداخلي", max_length=200, blank=True)
    work_type = models.CharField(
        "نوع الأعمال",
        max_length=20,
        choices=WorkType.choices,
    )
    area = models.CharField("المنطقة", max_length=100)
    description = models.TextField("الوصف العام", blank=True)

    latitude = models.DecimalField(
        "خط العرض",
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        "خط الطول",
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )

    is_public = models.BooleanField("إظهار على الخريطة العامة", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["reference"]

    def __str__(self):
        return f"{self.reference} - {self.public_name}"