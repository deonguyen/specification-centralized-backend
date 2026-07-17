from django.db import models
from specification_centralized_core.models.project_model import ProjectModel


class ProjectMilestoneModel(models.Model):
    """Represents a project milestone created by a user."""

    description = models.TextField(blank=True, null=True)
    end_date = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=250)
    project = models.ForeignKey(
        ProjectModel,
        related_name="project_milestone_project_id_x_project_id",
        on_delete=models.DO_NOTHING,
        db_column="project_id",
    )
    start_date = models.DateTimeField(null=True, blank=True)

    def __int__(self):
        return int(self.id)

    class Meta:
        db_table = "project_milestone"
        verbose_name_plural = "Project Milestones"
        verbose_name = "Project Milestone"
