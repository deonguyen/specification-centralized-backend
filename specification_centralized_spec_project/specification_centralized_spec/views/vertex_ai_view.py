from specification_centralized_spec.apps import SpecificationCentralizedSpecConfig
from google.oauth2 import service_account
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from vertexai.generative_models import GenerativeModel
import vertexai
import json
from django.db import transaction

from specification_centralized_core.models.project_model import ProjectModel
from specification_centralized_core.models.specification_model import SpecificationModel
from specification_centralized_core.models.specification_revision_model import SpecificationRevisionModel
from specification_centralized_core.models.specification_test_suite_model import (
    SpecificationTestSuiteModel,
)
from specification_centralized_core.models.specification_test_case_model import SpecificationTestCaseModel
from specification_centralized_spec.services.google_cloud_service import get_gcp_credential


class VertexAIView(viewsets.ViewSet):
    """
    API endpoint that allows interaction with Google Vertex AI.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_diff_summary(self, content1, content2):
        """
        Uses Google Vertex AI to generate a summary of differences between two contents.
        """
        # Note: Ensure you have authenticated with Google Cloud CLI (`gcloud auth application-default login`)
        # and have set GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION in your Django settings.
        try:
            credentials = get_gcp_credential()
            vertexai.init(
                project=SpecificationCentralizedSpecConfig.GOOGLE_PROJECT_ID,
                location=SpecificationCentralizedSpecConfig.GOOGLE_LOCATION,
                credentials=credentials,
            )
            model = GenerativeModel("gemini-2.5-pro")

            prompt = f"""
            You are an expert software engineer. Your task is to summarize the changes between two versions of a content.
            Provide a concise, human-readable summary. Focus on the semantic meaning of the changes.
            
            Here is the new version of the content:
            ---NEW VERSION---
            {content1}
            ---END NEW VERSION---

            Here is the old version of the content:
            ---OLD VERSION---
            {content2}
            ---END OLD VERSION---
           
            Summary of changes:
            """

            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Could not generate summary due to an error: {e}"

    def get_document_hierarchy(self, file_list):
        """
        Uses Google Vertex AI to organize a list of files into a hierarchy.
        """
        try:
            credentials = get_gcp_credential()
            vertexai.init(
                project=SpecificationCentralizedSpecConfig.GOOGLE_PROJECT_ID,
                location=SpecificationCentralizedSpecConfig.GOOGLE_LOCATION,
                credentials=credentials,
            )
            model = GenerativeModel("gemini-2.5-pro")

            prompt = f"""
            You are an expert information architect.
            Analyze the following list of file paths and determine a logical hierarchy based on semantic relationships and naming conventions.
            
            List of files:
            {file_list}
            
            Output a JSON object where the keys are the child file paths and the values are the parent file paths.
            If a file should be at the root (no parent), do not include it as a key, or set the value to null.
            Only include files from the provided list.
            
            Example JSON format:
            {{
                "path/to/child.py": "path/to/parent.py",
                "another/child.md": "another/parent.md"
            }}
            """

            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {e}"

    def get_document_bulletin(self, content):
        """
        Uses Google Vertex AI to generate a bulleted summary (bulletin) of a document's content.
        """
        try:
            credentials = get_gcp_credential()
            vertexai.init(
                project=SpecificationCentralizedSpecConfig.GOOGLE_PROJECT_ID,
                location=SpecificationCentralizedSpecConfig.GOOGLE_LOCATION,
                credentials=credentials,
            )
            model = GenerativeModel("gemini-2.5-pro")

            prompt = f"""
            You are an expert technical writer. Your task is to summarize the following document into key bullet points (a bulletin).
            Provide a clear, concise, and informative bulleted list representing the most important information.
            
            Here is the document content:
            ---DOCUMENT START---
            {content}
            ---DOCUMENT END---
           
            Bulleted summary:
            """

            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Could not generate bulletin due to an error: {e}"

    def get_bulletin_item_content(self, content, bulletin_item):
        """
        Uses Google Vertex AI to extract detailed content related to a specific bulletin item from a document.
        """
        try:
            credentials = service_account.Credentials.from_service_account_file(
                SpecificationCentralizedSpecConfig.GOOGLE_CREDENTIALS
            )
            vertexai.init(
                project=SpecificationCentralizedSpecConfig.GOOGLE_PROJECT_ID,
                location=SpecificationCentralizedSpecConfig.GOOGLE_LOCATION,
                credentials=credentials,
            )
            model = GenerativeModel("gemini-2.5-pro")

            prompt = f"""
            You are an expert technical writer. Your task is to extract and provide the detailed content 
            from the following document that corresponds to the provided bulletin item.
            
            Here is the specific bulletin item:
            {bulletin_item}

            Here is the document content:
            ---DOCUMENT START---
            {content}
            ---DOCUMENT END---
           
            Detailed content for the bulletin item:
            """

            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Could not extract content due to an error: {e}"

    def get_specification_category(self, content):
        """
        Uses Google Vertex AI to identify the category of a specification document based on its file path.
        """
        try:
            credentials = get_gcp_credential()
            vertexai.init(
                project=SpecificationCentralizedSpecConfig.GOOGLE_PROJECT_ID,
                location=SpecificationCentralizedSpecConfig.GOOGLE_LOCATION,
                credentials=credentials,
            )
            model = GenerativeModel("gemini-2.5-pro")

            prompt = f"""
            You are an expert technical business analyst. Your task is to categorize a specification document based on its file path.
            
            Here is the file content:
            {content}
            
            Provide a short, concise category name for this document (e.g., "LCA", "LK", "VF", "Lane Change Assist", "Lane Keep", "Vehicle Follow"). 
            Output ONLY the category name and nothing else.
            """

            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Could not determine category due to an error: {e}"

    def get_document_hyperlink_and_hierarchy(self, file_list):
        """
        Uses Google Vertex AI to extract hyperlinks and determine the document hierarchy.
        """
        try:
            credentials = service_account.Credentials.from_service_account_file(
                SpecificationCentralizedSpecConfig.GOOGLE_CREDENTIALS
            )
            vertexai.init(
                project=SpecificationCentralizedSpecConfig.GOOGLE_PROJECT_ID,
                location=SpecificationCentralizedSpecConfig.GOOGLE_LOCATION,
                credentials=credentials,
            )
            model = GenerativeModel("gemini-2.5-pro")

            prompt = f"""
            You are an expert technical writer and information architect. Your task is to analyze the following documents 
            and extract two things:
            1. A list of all hyperlinks (URLs and their corresponding text).
            2. The documents hierarchy to show the relationship between documents.
            
            List of files:
            {file_list}
           
            Provide the output in a structured JSON format with two keys: "hyperlinks" (a list of objects with "text" and "url") 
            and "hierarchy" (a nested object representing the heading structure).
            """

            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Could not extract hyperlinks and hierarchy due to an error: {e}"

    def get_diagram(self, input_data, output_data):
        """
        Uses Google Vertex AI to generate a diagram (Mermaid JS format) based on input and output descriptions.
        """
        try:
            credentials = get_gcp_credential()
            vertexai.init(
                project=SpecificationCentralizedSpecConfig.GOOGLE_PROJECT_ID,
                location=SpecificationCentralizedSpecConfig.GOOGLE_LOCATION,
                credentials=credentials,
            )
            model = GenerativeModel("gemini-2.5-pro")

            prompt = f"""
            You are an expert software architect. Your task is to generate a diagram in the Mermaid JS format 
            based on the provided input and output descriptions.
            
            Input description:
            {input_data}
            
            Output description:
            {output_data}
            
            Provide ONLY the valid Mermaid JS code block (e.g., starting with ```mermaid and ending with ```).
            Do not include any other explanations or surrounding text.
            """

            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Could not generate diagram due to an error: {e}"

    def get_diagram_text_output(self, input_data, output_data):
        """
        Uses Google Vertex AI to generate a diagram (Mermaid JS format) based on input and output descriptions.
        """
        try:
            credentials = get_gcp_credential()
            vertexai.init(
                project=SpecificationCentralizedSpecConfig.GOOGLE_PROJECT_ID,
                location=SpecificationCentralizedSpecConfig.GOOGLE_LOCATION,
                credentials=credentials,
            )
            model = GenerativeModel("gemini-2.5-pro")

            prompt = f"""
            You are an expert software architect. Your task is to generate a diagram in the text format 
            based on the provided input and output descriptions.
            
            Input description:
            {input_data}
            
            Output description:
            {output_data}
            
            Provide ONLY the valid Mermaid JS code block (e.g., starting with ```mermaid and ending with ```).
            Do not include any other explanations or surrounding text.
            """

            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Could not generate diagram due to an error: {e}"

    @action(detail=False, methods=["post"])
    def generatediagram(self, request):
        """
        API endpoint to generate a diagram based on input and output descriptions.
        Expects 'input_data' and 'output_data' in the request body.
        """
        input_data = request.data.get("input_data")
        output_data = request.data.get("output_data")

        if not input_data or not output_data:
            return Response(
                {"error": "Both 'input_data' and 'output_data' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        diagram = self.get_diagram(input_data, output_data)
        return Response({"diagram": diagram}, status=status.HTTP_200_OK)

    def get_test_cases(self, content):
        """
        Uses Google Vertex AI to generate test cases based on specification content.
        """
        try:
            credentials = get_gcp_credential()
            vertexai.init(
                project=SpecificationCentralizedSpecConfig.GOOGLE_PROJECT_ID,
                location=SpecificationCentralizedSpecConfig.GOOGLE_LOCATION,
                credentials=credentials,
            )
            model = GenerativeModel("gemini-2.5-pro")

            prompt = f"""
            You are an expert QA engineer. Your task is to generate comprehensive test cases 
            based on the provided specification content.
            
            Specification content:
            {content}
            
            Provide the output STRICTLY as a JSON object with the following structure, 
            without any markdown formatting or additional text:
            {{
                "test_suite_name": "A descriptive name for the test suite",
                "test_suite_code": "A unique identifier or code for the test suite, identifier or code must be include header of specification content",
                "test_suite_status": "Status of the test suite (e.g., Draft, Active)",
                "test_cases": [
                    {{
                        "name": "Test Case Title",
                        "code": "A unique identifier or code for the test case, identifier or code must be include header of specification content",
                        "status": "Status of the test case (e.g., Draft, Active)",
                        "description": "Description of the test case",
                        "steps": "Steps to execute",
                        "expected_result": "Expected outcome"
                    }}
                ]
            }}
            """

            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Could not generate test cases due to an error: {e}")

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

        project = ProjectModel.objects.filter(id=project_id).first()
        specification = SpecificationModel.objects.filter(id=specification_id).first()
        specification_revision = SpecificationRevisionModel.objects.filter(
            id=specification_revision_id
        ).first()

        if not specification_content or not project_id or not specification_id:
            return Response(
                {
                    "error": "'specification_content', 'project_id', and 'specification_id' are required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            test_cases_response = self.get_test_cases(specification_content)

            # Clean up the response to ensure it's valid JSON
            cleaned_response = test_cases_response.strip()
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

        summary = self.get_diff_summary(content1, content2)
        return Response({"summary": summary}, status=status.HTTP_200_OK)
