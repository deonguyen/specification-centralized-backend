from specification_centralized_spec.apps import SpecificationCentralizedSpecConfig
from google.oauth2 import service_account
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from vertexai.generative_models import GenerativeModel
import vertexai
import json
from django.db import transaction

from specification_centralized_core.models import (
    ProjectModel,
    SpecificationModel,
    SpecificationRevisionModel,
    SpecificationTestSuiteModel,
    SpecificationTestCaseModel,
)
from specification_centralized_spec.services import vertex_ai_service, wovey_api_service
from specification_centralized_spec.services.google_cloud_service import get_gcp_credential


class AIView(viewsets.ViewSet):
    @action(detail=False, methods=["post"])
    def generatediagram(self, request):
        """
        API endpoint to generate a diagram based on input and output descriptions.
        Expects 'input_data' and 'output_data' in the request body.
        """
        project_id = request.data.get("project_id")
        specification_id = request.data.get("specification_id")
        input_data = request.data.get("input_data")
        output_data = request.data.get("output_data")

        if not input_data and not output_data:
            return Response(
                {"error": "At least one of the fields 'input_data' or 'output_data' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        specification = SpecificationModel.objects.filter(id=specification_id).first()
        existing_diagram = specification.interface_diagram if specification else None
        if existing_diagram:
            return Response(
                {"diagram": existing_diagram},
                status=status.HTTP_200_OK,
            )

        diagram_result = None
        vertex_ai_result = None
        wovey_api_result = None

        try:
            wovey_api_result = wovey_api_service.generate_diagram(input_data, output_data)
        except Exception as e: 
            print(f"Cannot call to Wovey API: {e}")
            wovey_api_result = None

        try:
            if(not wovey_api_result):
                vertex_ai_result = vertex_ai_service.generate_diagram(input_data, output_data)
        except Exception as e: 
            print(f"Cannot call to Vetex AI: {e}")
            vertex_ai_result = None
        
        diagram_result = vertex_ai_result or wovey_api_result[0]
        # Save diagram to database
        if specification and diagram_result:
            specification.interface_diagram = diagram_result
            specification.save(update_fields=["interface_diagram"])
        return Response(
            {"diagram": diagram_result},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"])
    def generatetestcases(self, request):
        """
        API endpoint to generate test cases based on specification content
        and insert them into the database.
        Expects 'content', 'project_id', and 'specification_id' in the request body.
        """

        project_id = request.data.get("project_id")
        specification_id = request.data.get("specification_id")
        specification_revision_id = request.data.get("specification_revision_id")
        specification_content = request.data.get("specification_content")

        if not specification_content or not project_id or not specification_id:
            return Response(
                {
                    "error": "'specification_content', 'project_id', and 'specification_id' are required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        project = ProjectModel.objects.filter(id=project_id).first()
        specification = SpecificationModel.objects.filter(id=specification_id).first()
        specification_revision = SpecificationRevisionModel.objects.filter(id=specification_revision_id).first()

        existing_suite = SpecificationTestSuiteModel.objects.filter(
            project=project,
            specification=specification,
            specification_revision=specification_revision,
        ).first()

        if existing_suite:
            existing_test_cases = SpecificationTestCaseModel.objects.filter(
                specification_test_suite=existing_suite
            )
            return Response(
                {
                    "message": "Test cases retrieved from database.",
                    "test_suite_id": existing_suite.id,
                    "test_suite_name": existing_suite.name,
                    "test_cases": [
                        {
                            "id": tc.id,
                            "actual_result": tc.actual_result or "",
                            "code": tc.code,
                            "description": tc.description or "",
                            "expected_result": tc.expected_result or "",
                            "name": tc.name,
                            "status": tc.status or "",
                            "steps": tc.steps or "",
                        }
                        for tc in existing_test_cases
                    ],
                },
                status=status.HTTP_200_OK,
            )

        try:
            test_cases_response = wovey_api_service.generate_test_cases(specification_content)

            # Clean up the response to ensure it's valid JSON
            cleaned_response = test_cases_response[0].strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]

            parsed_data = json.loads(cleaned_response.strip())

            with transaction.atomic():
                # Insert or Update Test Suite
                specification_test_suite, suite_created = (
                    SpecificationTestSuiteModel.objects.update_or_create(
                        project=project,
                        specification=specification,
                        specification_revision=specification_revision,
                        name=parsed_data.get("test_suite_name", "Generated Test Suite"),
                        defaults={
                            "code": parsed_data.get("test_suite_code", ""),
                            "status": parsed_data.get("test_suite_status", "Draft"),
                            "raw_content": test_cases_response,
                        },
                    )
                )

                # Insert or Update Test Cases
                created_test_cases = []
                for tc_data in parsed_data.get("test_cases", []):
                    test_case, tc_created = (
                        SpecificationTestCaseModel.objects.update_or_create(
                            project=project,
                            specification=specification,
                            specification_revision=specification_revision,
                            specification_test_suite=specification_test_suite,
                            name=tc_data.get("name", "Untitled Test Case"),
                            code=tc_data.get("code", ""),
                            defaults={
                                "status": tc_data.get("status", "Draft"),
                                "description": tc_data.get("description", ""),
                                "steps": tc_data.get("steps", ""),
                                "expected_result": tc_data.get("expected_result", ""),
                                "actual_result": tc_data.get("actual_result", ""),
                            },
                        )
                    )
                    created_test_cases.append(
                        {
                            "id": test_case.id,
                            "actual_result": tc_data.get("actual_result", ""),
                            "code": test_case.code,
                            "description": tc_data.get("description", ""),
                            "expected_result": tc_data.get("expected_result", ""),
                            "name": test_case.name,
                            "status": "created" if tc_created else "updated",
                            "steps": tc_data.get("steps", ""),
                        }
                    )

            return Response(
                {
                    "message": "Test cases generated and saved successfully.",
                    # "test_suite_content": test_cases_response,
                    "test_suite_id": specification_test_suite.id,
                    "test_suite_name": specification_test_suite.name,
                    "test_cases": created_test_cases,
                },
                status=status.HTTP_201_CREATED,
            )

        except json.JSONDecodeError:
            return Response(
                {
                    "error": "Failed to parse the AI response as JSON.",
                    "raw_response": test_cases_response,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def diffsummary(self, request):
        content1 = request.data.get("content1")
        content2 = request.data.get("content2")

        if content1 is None or content2 is None:
            return Response(
                {"error": "Both 'content1' and 'content2' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        summary, status_code = wovey_api_service.compare_diff_summary(
            content1, content2
        )
        return Response({"summary": summary}, status=status_code)
