from django.db import models

from specification_centralized_core.models.project_model import ProjectModel
from specification_centralized_core.models.specification_test_case_model import SpecificationTestCaseModel
from specification_centralized_core.models.specification_test_suite_model import (
    SpecificationTestSuiteModel,
)
from specification_centralized_core.models.test_execution_trace_model import TestExecutionTraceModel


class TestExecutionTraceLogModel(models.Model):
    """Represents a specification created by a user."""

    project = models.ForeignKey(
        ProjectModel,
        related_name="test_execution_trace_log_project_id_x_project_id",
        on_delete=models.DO_NOTHING,
        db_column="project_id",
    )
    specification_test_case = models.ForeignKey(
        SpecificationTestCaseModel,
        related_name="test_execution_trace_log_specification_test_case_id_x_specification_test_case_id",
        on_delete=models.DO_NOTHING,
        db_column="specification_test_case_id",
    )
    specification_test_suite = models.ForeignKey(
        SpecificationTestSuiteModel,
        related_name="test_execution_trace_log_specification_test_suite_id_x_specification",
        on_delete=models.DO_NOTHING,
        db_column="specification_test_suite_id",
    )
    test_execution_trace = models.ForeignKey(
        TestExecutionTraceModel,
        related_name="test_execution_trace_log_test_execution_trace_id_x_test_execution_trace_id",
        on_delete=models.DO_NOTHING,
        db_column="test_execution_trace_id",
    )
    test_result = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    test_status = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "test_execution_trace_log"
        verbose_name_plural = "Test Execution Trace Logs"
        verbose_name = "Test Execution Trace Log"
