from django.db import models

from specification_centralized_core.models.code_implementation_trace_model import (
    CodeImplementationTraceModel,
)
from specification_centralized_core.models.project_model import ProjectModel


class CodeImplementationTraceLogModel(models.Model):
    """Represents a specification created by a user."""

    code_implementation_trace = models.ForeignKey(
        CodeImplementationTraceModel,
        related_name="code_implementation_trace_log_code_implementation_trace_id_x_code_implementation_trace_id",
        on_delete=models.DO_NOTHING,
        db_column="code_implementation_trace_id",
    )
    project = models.ForeignKey(
        ProjectModel,
        related_name="code_implementation_trace_log_project_id_x_project_id",
        on_delete=models.DO_NOTHING,
        db_column="project_id",
    )
    pull_request_comments = models.TextField(
        null=True,
        blank=True,
    )
    pull_request_link = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
    )
    pull_request_sha = models.CharField(
        max_length=40,
        null=True,
        blank=True,
    )
    name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    path = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
    )
    sha = models.CharField(
        max_length=40,
        null=True,
        blank=True,
    )
    url = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
    )
    git_url = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
    )
    download_url = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "code_implementation_trace_log"
        verbose_name_plural = "Code Implementation Trace Logs"
        verbose_name = "Code Implementation Trace Log"
