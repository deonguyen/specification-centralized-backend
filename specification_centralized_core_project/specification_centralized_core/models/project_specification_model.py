from django.db import models
from .complexity_model import ComplexityModel
from .component_model import ComponentModel
from .function_model import FunctionModel
from .priority_model import PriorityModel
from .process_model import ProcessModel
from .project_model import ProjectModel
from .specification_model import SpecificationModel
from .specification_revision_model import SpecificationRevisionModel


class ProjectSpecificationModel(models.Model):
    """Represents a project specification created by a user."""

    category1 = models.CharField(max_length=250, null=True, blank=True)
    category2 = models.CharField(max_length=250, null=True, blank=True)
    complexity = models.ForeignKey(
        ComplexityModel,
        related_name="project_specification_complexity_id_x_complexity_id",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        db_column="complexity_id",
    )
    component = models.ForeignKey(
        ComponentModel,
        related_name="project_specification_component_id_x_component_id",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        db_column="component_id",
    )
    function = models.ForeignKey(
        FunctionModel,
        related_name="project_specification_function_id_x_function_id",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        db_column="function_id",
    )
    parent = models.ForeignKey(
        "self",
        related_name="project_specification_parent_id_x_project_specification_id",
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        db_column="parent_id",
    )
    priority = models.ForeignKey(
        PriorityModel,
        related_name="project_specification_priority_id_x_priority_id",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        db_column="priority_id",
    )
    process = models.ForeignKey(
        ProcessModel,
        related_name="project_specification_process_id_x_process_id",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        db_column="process_id",
    )
    progress = models.IntegerField(null=True, blank=True)
    project = models.ForeignKey(
        ProjectModel,
        related_name="project_specification_project_id_x_project_id",
        on_delete=models.DO_NOTHING,
        db_column="project_id",
    )
    specification = models.ForeignKey(
        SpecificationModel,
        related_name="project_specification_specification_id_x_specification_id",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        db_column="specification_id",
    )
    specification_order = models.IntegerField(null=True, blank=True)
    specification_revision = models.ForeignKey(
        SpecificationRevisionModel,
        related_name="project_specification_specification_revision_id_x_specification_revision_id",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        db_column="specification_revision_id",
    )

    def __int__(self):
        return int(self.id)

    class Meta:
        db_table = "project_specification"
        verbose_name_plural = "Project Specifications"
        verbose_name = "Project Specification"
