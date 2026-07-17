from django.contrib.auth.models import User
from django.db import models
from specification_centralized_core.models.project_model import ProjectModel


class UserSettingModel(models.Model):
    """Represents a complexity created by a user."""

    page_size = models.IntegerField(
        null=True,
        blank=True,
    )
    project = models.ForeignKey(
        ProjectModel,
        related_name="user_setting_project_id_x_project_id",
        on_delete=models.DO_NOTHING,
        db_column="project_id",
        null=True,
        blank=True,
    )
    theme = models.CharField(
        max_length=10,
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        User,
        related_name="user_setting_user_id_x_user_id",
        on_delete=models.DO_NOTHING,
        db_column="user_id",
    )

    class Meta:
        db_table = "user_setting"
        verbose_name_plural = "User Settings"
        verbose_name = "User Setting"
