from django.db import models


class PriorityModel(models.Model):
    """Represents a priority created by a user."""

    code = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    project = models.ForeignKey(
        "ProjectModel",
        related_name="priority_project_id_x_project_id",
        on_delete=models.DO_NOTHING,
        db_column="project_id",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    class Meta:
        db_table = "priority"
        verbose_name_plural = "Priorities"
        verbose_name = "Priority"
