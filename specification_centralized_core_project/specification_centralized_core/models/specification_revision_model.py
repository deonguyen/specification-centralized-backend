from django.contrib.auth.models import User
from django.db import models
from .project_model import ProjectModel
from .specification_model import SpecificationModel


class SpecificationRevisionModel(models.Model):
    """Represents a specification revision created by a user."""

    change_date = models.DateTimeField(auto_now=True)
    change_summary = models.TextField(
        null=True,
        blank=True,
    )
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
    previous_version = models.CharField(
        max_length=40,
        null=True,
        blank=True,
    )
    project = models.ForeignKey(
        ProjectModel,
        related_name="specification_revision_project_id_x_project_id",
        on_delete=models.DO_NOTHING,
        db_column="project_id",
    )
    raw_content = models.TextField(
        null=True,
        blank=True,
    )
    specification = models.ForeignKey(
        SpecificationModel,
        related_name="specification_revision_specification_id_x_specification_id",
        on_delete=models.DO_NOTHING,
        db_column="specification_id",
    )
    updated_by = models.ForeignKey(
        User,
        related_name="specification_revision_updated_by_x_user_id",
        on_delete=models.DO_NOTHING,
        db_column="updated_by",
    )
    version = models.CharField(
        max_length=40,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "specification_revision"
        verbose_name_plural = "Specification Revisions"
        verbose_name = "Specification Revision"
