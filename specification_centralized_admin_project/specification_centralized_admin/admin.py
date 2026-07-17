from django.contrib import admin
from specification_centralized_core.models.category_model import CategoryModel
from specification_centralized_core.models.complexity_model import ComplexityModel
from specification_centralized_core.models.component_model import ComponentModel
from specification_centralized_core.models.function_model import FunctionModel
from specification_centralized_core.models.priority_model import PriorityModel
from specification_centralized_core.models.process_model import ProcessModel
from specification_centralized_core.models.project_milestone_model import ProjectMilestoneModel
from specification_centralized_core.models.project_model import ProjectModel
from specification_centralized_core.models.project_specification_model import ProjectSpecificationModel
from specification_centralized_core.models.specification_model import SpecificationModel
from specification_centralized_core.models.specification_revision_model import SpecificationRevisionModel
from specification_centralized_core.models.user_setting_model import UserSettingModel

# Register your models here.


@admin.register(CategoryModel)
class CategoryAdmin(admin.ModelAdmin):
    """Admin View for Category"""

    list_display = ("name", "code", "project", "created_at", "updated_at")
    list_filter = ("project", "created_at")
    search_fields = ("name", "code")


@admin.register(ComponentModel)
class ComponentAdmin(admin.ModelAdmin):
    """Admin View for Component"""

    list_display = ("name", "code", "type")
    search_fields = ("name", "code", "description")
    list_filter = ("type",)


@admin.register(FunctionModel)
class FunctionAdmin(admin.ModelAdmin):
    """Admin View for Function"""

    list_display = ("name", "code", "type")
    search_fields = ("name", "code", "description")
    list_filter = ("type",)


@admin.register(ProcessModel)
class ProcessAdmin(admin.ModelAdmin):
    """Admin View for Process"""

    list_display = ("name", "code", "type")
    search_fields = ("name", "code", "description")
    list_filter = ("type",)


@admin.register(PriorityModel)
class PriorityAdmin(admin.ModelAdmin):
    """Admin View for Priority"""

    list_display = ("name", "code", "type")
    search_fields = ("name", "code", "description")
    list_filter = ("type",)


@admin.register(ComplexityModel)
class ComplexityAdmin(admin.ModelAdmin):
    """Admin View for Complexity"""

    list_display = ("name", "code", "type")
    search_fields = ("name", "code", "description")
    list_filter = ("type",)


@admin.register(ProjectModel)
class ProjectAdmin(admin.ModelAdmin):
    """Admin View for Project"""

    list_display = ("name", "code", "owner_user", "created_at", "updated_at")
    list_filter = ("owner_user", "created_at")
    search_fields = ("name", "code", "description")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ProjectSpecificationModel)
class ProjectSpecificationAdmin(admin.ModelAdmin):
    """Admin View for ProjectSpecification"""

    list_display = (
        "id",
        "project",
        "component",
        "function",
        "specification",
    )


@admin.register(SpecificationModel)
class SpecificationAdmin(admin.ModelAdmin):
    """Admin View for Specification"""

    list_display = ("name", "code", "status", "type")
    list_filter = ("source", "status", "type")
    search_fields = ("internal_id", "source", "status", "type")


@admin.register(SpecificationRevisionModel)
class SpecificationRevisionAdmin(admin.ModelAdmin):
    """Admin View for SpecificationRevision"""

    list_display = (
        "id",
        "specification",
        "updated_by",
        "version",
        "previous_version",
        "change_summary",
        "change_date",
    )
    search_fields = (
        "specification__name",
        "updated_by__username",
        "version",
        "previous_version",
    )
    list_filter = ("updated_by",)


@admin.register(ProjectMilestoneModel)
class ProjectMilestoneAdmin(admin.ModelAdmin):
    """Admin View for ProjectMilestone"""

    list_display = ("name", "project", "start_date", "end_date")
    search_fields = ("name", "description", "project__name")
    list_filter = ("project",)


@admin.register(UserSettingModel)
class UserSettingAdmin(admin.ModelAdmin):
    """Admin View for UserSetting"""

    list_display = ("user", "project", "page_size", "theme")
    search_fields = ("user__username", "project__name")
    list_filter = ("user",)
