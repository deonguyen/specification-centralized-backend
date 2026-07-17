from django.contrib.auth.models import User
from django.db import models


class BaseModel(models.Model):
    """Represents a specification import type."""

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        related_name="%(class)s_created_by_x_user_id",
        on_delete=models.DO_NOTHING,
        db_column="created_by_id",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        related_name="%(class)s_updated_by_x_user_id",
        on_delete=models.DO_NOTHING,
        db_column="updated_by_id",
    )

    class Meta:
        abstract = True
