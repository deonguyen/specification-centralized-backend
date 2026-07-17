from google import genai

from specification_centralized_spec.apps import SpecificationCentralizedSpecConfig
import google.auth
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


def compare_diff_summary(content1, content2):
    """
    Uses Google Vertex AI to generate a summary of differences between two contents.
    """
    # Note: Ensure you have authenticated with Google Cloud CLI (`gcloud auth application-default login`)
    # and have set GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION in your Django settings.
    try:
        # Use Application Default Credentials. This works for local dev (gcloud auth),
        # GKE (Workload Identity), and Cloud Run (attached service account).
        credentials = get_gcp_credential()
        # This will use the default credentials from the environment when running in Google Cloud
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


def generate_diagram(input_data, output_data):
    """
    Uses Google Vertex AI to generate a diagram (Mermaid JS format) based on input and output descriptions.
    """
    try:
        credentials = get_gcp_credential()
        # vertexai.init(
        #     project=SpecificationCentralizedSpecConfig.GOOGLE_PROJECT_ID,
        #     location=SpecificationCentralizedSpecConfig.GOOGLE_LOCATION,
        #     credentials=credentials,
        # )
        # client = genai.Client(
        #     project=SpecificationCentralizedSpecConfig.GOOGLE_PROJECT_ID,
        #     location=SpecificationCentralizedSpecConfig.GOOGLE_LOCATION,
        #     #credentials=credentials,
        #     api_key="AQ.Ab8RN6K6PJvzK_ZrQc7ecOXA83C5NVGt2MA3Zvu6S7C15d79Gw"
        # )

        client = genai.Client(
            vertexai=True,
            project=SpecificationCentralizedSpecConfig.GOOGLE_PROJECT_ID,
            #location=SpecificationCentralizedSpecConfig.GOOGLE_LOCATION,
            location="global",
            credentials=credentials,
        )

        # model = GenerativeModel("gemini-3.5-flash")

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

        response = client.models.generate_content(
            model="gemini-3.5-flash", contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Could not generate diagram due to an error: {e}"
