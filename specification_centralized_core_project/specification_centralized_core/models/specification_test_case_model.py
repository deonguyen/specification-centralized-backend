from django.db import models
from .project_model import ProjectModel
from .specification_model import SpecificationModel
from .specification_revision_model import SpecificationRevisionModel
from .specification_test_suite_model import SpecificationTestSuiteModel

class SpecificationTestCaseModel(models.Model):
    actual_result = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=250)
    description = models.TextField(null=True, blank=True)
    expected_result = models.TextField(null=True, blank=True)
    name = models.CharField(max_length=250)
    project = models.ForeignKey(
        ProjectModel,
        related_name="specification_test_case_project_id_x_project_id",
        on_delete=models.DO_NOTHING,
        db_column="project_id",
    )
    specification = models.ForeignKey(
        SpecificationModel,
        related_name="specification_test_case_specification_id_x_specification_id",
        on_delete=models.DO_NOTHING,
        db_column="specification_id",
    )
    specification_revision = models.ForeignKey(
        SpecificationRevisionModel,
        related_name="specification_test_case_specification_revision_id_x_specification_revision_id",
        on_delete=models.DO_NOTHING,
        db_column="specification_revision_id",
    )
    specification_test_suite = models.ForeignKey(
        SpecificationTestSuiteModel,
        related_name="specification_test_case_specification_test_suite_id_x_specification_test_suite_id",
        on_delete=models.DO_NOTHING,
        db_column="specification_test_suite_id",
    )
    status = models.CharField(max_length=250, null=True, blank=True)
    steps = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "specification_test_case"
        verbose_name_plural = "Specification Test Cases"
        verbose_name = "Specification Test Case"
