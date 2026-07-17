from django.contrib.auth.models import User
from django.db import models
from specification_centralized_core.models.project_milestone_model import ProjectMilestoneModel
from specification_centralized_core.models.project_model import ProjectModel
from specification_centralized_core.models.project_specification_model import ProjectSpecificationModel
from specification_centralized_core.models.specification_model import SpecificationModel
from specification_centralized_core.models.specification_revision_model import SpecificationRevisionModel


class ProjectSpecificationMilestoneBaselineModel(models.Model):
    """Represents a project milestone created by a user."""

    project = models.ForeignKey(
        ProjectModel,
        related_name="project_specification_milestone_baseline_project_id_x_project_id",
        on_delete=models.DO_NOTHING,
        db_column="project_id",
    )
    project_milestone = models.ForeignKey(
        ProjectMilestoneModel,
        related_name="project_specification_milestone_baseline_project_milestone_id_x_project_milestone_id",
        on_delete=models.DO_NOTHING,
        db_column="project_milestone_id",
    )
    project_specification = models.ForeignKey(
        ProjectSpecificationModel,
        related_name="project_specification_milestone_baseline_project_specification_id_x_project_specification_id",
        on_delete=models.DO_NOTHING,
        db_column="project_specification_id",
    )
    specification = models.ForeignKey(
        SpecificationModel,
        related_name="project_specification_milestone_baseline_specification_id_x_specification_id",
        on_delete=models.DO_NOTHING,
        db_column="specification_id",
    )
    specification_revision = models.ForeignKey(
        SpecificationRevisionModel,
        related_name="project_specification_milestone_baseline_specification_revision_id_x_specification_revision_id",
        on_delete=models.DO_NOTHING,
        db_column="specification_revision_id",
    )
    user = models.ForeignKey(
        User,
        related_name="project_specification_milestone_baseline_user_id_x_user_id",
        on_delete=models.DO_NOTHING,
        db_column="user_id",
    )

    def __int__(self):
        return int(self.id)

    class Meta:
        db_table = "project_specification_milestone_baseline"
        verbose_name_plural = "Project Specification Milestone Baselines"
        verbose_name = "Project Specification Milestone Baseline"
        constraints = [
            models.UniqueConstraint(fields=['project_id', 'project_milestone_id', 'project_specification_id', 'user_id'], name='unique_project_specification_milestone_baseline')
        ]
