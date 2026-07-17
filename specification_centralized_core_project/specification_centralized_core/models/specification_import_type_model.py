from django.db import models
from specification_centralized_core.models.base_model import BaseModel


class SpecificationImportTypeModel(BaseModel):
    """Represents a specification import type."""

    code = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "specification_import_type"
        verbose_name = "Specification Import Type"
        verbose_name_plural = "Specification Import Types"