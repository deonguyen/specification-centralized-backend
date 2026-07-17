from django.db import models

class SpecificationTestSuiteModel(models.Model):
    code = models.CharField(max_length=250)
    description = models.TextField(null=True, blank=True)
    name = models.CharField(max_length=250)
    project = models.ForeignKey(
        "ProjectModel",
        related_name="specification_test_suite_project_id_x_project_id",
        on_delete=models.DO_NOTHING,
        db_column="project_id",
    )
    raw_content = models.TextField(null=True, blank=True)
    specification = models.ForeignKey(
        "SpecificationModel",
        related_name="specification_test_suite_specification_id_x_specification_id",
        on_delete=models.DO_NOTHING,
        db_column="specification_id",
    )
    specification_revision = models.ForeignKey(
        "SpecificationRevisionModel",
        related_name="specification_test_suite_specification_revision_id_x_specification_revision_id",
        on_delete=models.DO_NOTHING,
        db_column="specification_revision_id",
    )
    status = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        db_table = "specification_test_suite"
        verbose_name_plural = "Specification Test Suites"
        verbose_name = "Specification Test Suite"
