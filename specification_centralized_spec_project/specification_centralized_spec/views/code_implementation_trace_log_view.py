import django_filters
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from specification_centralized_core.models.code_implementation_trace_log_model import CodeImplementationTraceLogModel
from specification_centralized_spec.serializers.code_implementation_trace_log_serializer import CodeImplementationTraceLogSerializer
from specification_centralized_core.models.code_implementation_trace_model import CodeImplementationTraceModel


class StandardResultsSetPagination(PageNumberPagination):
    page_size = None
    page_size_query_param = "page_size"
    max_page_size = None


class CodeImplementationTraceLogViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Code Implementation Trace Logs to be viewed or edited.
    """
    queryset = CodeImplementationTraceLogModel.objects.all().order_by("-id")
    serializer_class = CodeImplementationTraceLogSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ["project", "code_implementation_trace", "pull_request_sha"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        project_id = request.query_params.get("project_id")
        code_implementation_trace_id = request.query_params.get("code_implementation_trace_id")
        pull_request_sha = request.query_params.get("pull_request_sha")

        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if code_implementation_trace_id:
            queryset = queryset.filter(code_implementation_trace_id=code_implementation_trace_id)
        if pull_request_sha:
            queryset = queryset.filter(pull_request_sha=pull_request_sha)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

        for item in data:
            trace_id = item.get("code_implementation_trace")
            if isinstance(trace_id, dict):
                trace_id = trace_id.get("id")
            trace = CodeImplementationTraceModel.objects.filter(id=trace_id).first()
            item["specification_name"] = trace.specification.name if trace and getattr(trace, "specification", None) else None

        if page is not None:
            return self.get_paginated_response(data)

        return Response(data)