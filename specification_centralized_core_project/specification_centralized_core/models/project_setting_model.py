from django.db import models


class ProjectSettingModel(models.Model):
    """Represents a setting for a project."""

    github_url = models.TextField(
        null=True,
        blank=True,
    )
    jama_project_id = models.TextField(
        null=True,
        blank=True,
    )
    jama_url = models.TextField(
        null=True,
        blank=True,
    )
    jama_swrd_item_type = models.IntegerField(
        null=True,
        blank=True,
    )
    jama_swqt_item_type = models.IntegerField(
        null=True,
        blank=True,
    )
    jama_scrd_item_type = models.IntegerField(
        null=True,
        blank=True,
    )
    jama_scqt_item_type = models.IntegerField(
        null=True,
        blank=True,
    )
    jama_sud_item_type = models.IntegerField(
        null=True,
        blank=True,
    )
    jama_sut_item_type = models.IntegerField(
        null=True,
        blank=True,
    )

    project = models.ForeignKey(
        "ProjectModel",
        related_name="project_setting_project_id_x_project_id",
        on_delete=models.DO_NOTHING,
        db_column="project_id",
    )

    class Meta:
        db_table = "project_setting"
        verbose_name_plural = "Project Settings"
        verbose_name = "Project Settings"
