from django.db import models


class CategoryModel(models.Model):
    """Represents a category created by a user."""

    code = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    project = models.ForeignKey(
        "ProjectModel",
        related_name="category_project_id_x_project_id",
        on_delete=models.DO_NOTHING,
        db_column="project_id",
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    class Meta:
        db_table = "category"
        verbose_name_plural = "Categories"
        verbose_name = "Category"
