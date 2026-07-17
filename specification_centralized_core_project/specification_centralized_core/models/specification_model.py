from django.db import models

from .project_model import ProjectModel


class SpecificationModel(models.Model):
    """Represents a specification created by a user."""

    code = models.CharField(max_length=255)
    content = models.TextField(
        null=True,
        blank=True,
    )
    interface = models.TextField(
        null=True,
        blank=True,
    )
    interface_diagram = models.TextField(
        null=True,
        blank=True,
    )
    internal_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column="internal_id",
    )
    local_file_fullpath = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
    )
    local_file_path = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    project = models.ForeignKey(
        ProjectModel,
        related_name="specification_project_id_x_project_id",
        on_delete=models.DO_NOTHING,
        db_column="project_id",
    )
    raw_content = models.TextField(
        null=True,
        blank=True,
    )
    source = models.TextField(
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=250,
        null=True,
        blank=True,
    )
    type = models.CharField(
        max_length=250,
        null=True,
        blank=True,
    )
    version = models.CharField(
        max_length=40,
        null=True,
        blank=True,
    )
    
    def __str__(self):
        return self.code

    class Meta:
        db_table = "specification"
        verbose_name_plural = "Specifications"
        verbose_name = "Specification"
