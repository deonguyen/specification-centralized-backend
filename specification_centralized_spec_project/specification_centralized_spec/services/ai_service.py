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


def get_diff_summary(content1, content2):
    """
    Uses Google Vertex AI to generate a summary of differences between two contents.
    """
    # Note: Ensure you have authenticated with Google Cloud CLI (`gcloud auth application-default login`)
    # and have set GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION in your Django settings.
    try:
        # Use Application Default Credentials. This works for local dev (gcloud auth),
        # GKE (Workload Identity), and Cloud Run (attached service account).
        credentials, project_id = google.auth.default()
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
