from django.contrib.auth.models import User
from django.db import models


class ProjectModel(models.Model):
    """Represents a project created by a user."""

    code = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    name = models.CharField(max_length=255)
    owner_user = models.ForeignKey(
        User,
        related_name="project_owner_x_user_id",
        on_delete=models.DO_NOTHING,
        db_column="owner_user_id",
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    class Meta:
        db_table = "project"
        verbose_name_plural = "Projects"
        verbose_name = "Project"
