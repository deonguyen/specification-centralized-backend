from django.db import models


class JamaItemTypeModel(models.Model):
    """Represents a priority created by a user."""

    type_key = models.CharField(max_length=255, unique=True)
    display = models.TextField(blank=True)
    def __str__(self):
        return self.type_key

    class Meta:
        db_table = "jama_item_type"
        verbose_name_plural = "Jama Item Types"
        verbose_name = "Jama Item Type"
