from django.db import models


class FunctionModel(models.Model):
    """Represents a function created by a user."""

    code = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    name = models.CharField(max_length=255)
    project = models.ForeignKey(
        "ProjectModel",
        related_name="function_project_id_x_project_id",
        on_delete=models.DO_NOTHING,
        db_column="project_id",
    )
    type = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    class Meta:
        db_table = "function"
        verbose_name_plural = "Functions"
        verbose_name = "Function"
