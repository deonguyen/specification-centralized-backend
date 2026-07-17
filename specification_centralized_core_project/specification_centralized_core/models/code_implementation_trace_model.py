from django.db import models

from specification_centralized_core.models.project_milestone_model import ProjectMilestoneModel
from specification_centralized_core.models.project_model import ProjectModel
from specification_centralized_core.models.project_specification_model import ProjectSpecificationModel
from specification_centralized_core.models.specification_model import SpecificationModel
from specification_centralized_core.models.specification_revision_model import SpecificationRevisionModel


class CodeImplementationTraceModel(models.Model):
    """Represents a specification created by a user."""

    code_implementation_status = models.CharField(max_length=255, unique=True)
    milestone = models.ForeignKey(
        ProjectMilestoneModel,
        related_name="code_implementation_trace_milestone_id_x_project_milestone_id",
        on_delete=models.DO_NOTHING,
        db_column="milestone_id",
        null=True,
        blank=True,
    )
    project = models.ForeignKey(
        ProjectModel,
        related_name="code_implementation_trace_project_id_x_project_id",
        on_delete=models.DO_NOTHING,
        db_column="project_id",
    )
    project_specification = models.ForeignKey(
        ProjectSpecificationModel,
        related_name="code_implementation_trace_project_specification_id_x_project_specification_id",
        on_delete=models.DO_NOTHING,
        db_column="project_specification_id",
    )
    specification = models.ForeignKey(
        SpecificationModel,
        related_name="code_implementation_trace_specification_id_x_specification_id",
        on_delete=models.DO_NOTHING,
        db_column="specification_id",
    )
    specification_revision = models.ForeignKey(
        SpecificationRevisionModel,
        related_name="code_implementation_trace_specification_revision_id_x_specification_revision_id",
        on_delete=models.DO_NOTHING,
        db_column="specification_revision_id",
    )

    class Meta:
        db_table = "code_implementation_trace"
        verbose_name_plural = "Code Implementation Traces"
        verbose_name = "Code Implementation Trace"
