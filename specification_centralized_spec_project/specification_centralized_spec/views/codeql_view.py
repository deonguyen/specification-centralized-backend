from specification_centralized_spec.apps import SpecificationCentralizedSpecConfig
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from vertexai.generative_models import GenerativeModel
import json
from django.db import transaction
import re
import subprocess
import os
import tempfile
from django.conf import settings
from django.db.models import Count, Q
from specification_centralized_core.models.test_execution_trace_log_model import TestExecutionTraceLogModel
from bs4 import BeautifulSoup, NavigableString, Tag


class CodeQlViewSet(viewsets.ModelViewSet):
    @action(detail=False, methods=["post"])
    def run_codeql_query(self, request):
        query_file = request.data.get("query_file")
        if not query_file:
            return Response(
                {"error": "Parameter 'query_file' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        base_dir = getattr(settings, "BASE_DIR", "")
        db_path = os.path.join(base_dir, "codeql-db")
        if not os.path.exists(db_path):
            return Response(
                {
                    "error": "CodeQL database not found at ./codeql-db. Please generate it first."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Securely construct the full path and prevent directory traversal
        query_path = os.path.abspath(os.path.join(base_dir, query_file))
        if not query_path.startswith(os.path.abspath(base_dir)):
            return Response(
                {
                    "error": "Invalid query file path. Directory traversal is not allowed."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not os.path.exists(query_path):
            return Response(
                {"error": f"Query file not found: {query_file}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                bqrs_file = os.path.join(temp_dir, "results.bqrs")
                json_file = os.path.join(temp_dir, "results.json")

                # Step 1: Run the CodeQL query to produce a BQRS file
                run_cmd = [
                    "codeql",
                    "query",
                    "run",
                    query_path,
                    "--database",
                    db_path,
                    "--output",
                    bqrs_file,
                ]
                run_result = subprocess.run(run_cmd, capture_output=True, text=True)

                if run_result.returncode != 0:
                    return Response(
                        {
                            "error": "CodeQL query execution failed.",
                            "details": run_result.stderr,
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

                # Step 2: Decode the BQRS file to JSON format
                decode_cmd = [
                    "codeql",
                    "bqrs",
                    "decode",
                    bqrs_file,
                    "--format=json",
                    "--output",
                    json_file,
                ]
                decode_result = subprocess.run(
                    decode_cmd, capture_output=True, text=True
                )

                if decode_result.returncode != 0:
                    return Response(
                        {
                            "error": "Failed to decode BQRS results to JSON.",
                            "details": decode_result.stderr,
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

                with open(json_file, "r", encoding="utf-8") as f:
                    json_results = json.load(f)

                return Response(json_results, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["get"])
    def execution_summary(self, request):
        # """
        # Calculates the percentage of passed and failed unit tests vs total cases.
        # """
        # metrics = TestExecutionTraceLogModel.objects.aggregate(
        #     total=Count("id"),
        #     passed=Count("id", filter=Q(test_status__iexact="passed")),
        #     failed=Count("id", filter=Q(test_status__iexact="failed")),
        # )

        # total = metrics["total"]
        # passed_percentage = (metrics["passed"] / total * 100) if total > 0 else 0
        # failed_percentage = (metrics["failed"] / total * 100) if total > 0 else 0

        # return Response(
        #     {
        #         "total_cases": total,
        #         "passed_percentage": round(passed_percentage, 2),
        #         "failed_percentage": round(failed_percentage, 2),
        #         "passed_cases": metrics["passed"],
        #         "failed_cases": metrics["failed"],
        #     },
        #     status=status.HTTP_200_OK,
        # )

        # try:
        #     base_dir = getattr(settings, "BASE_DIR", "")
        #     test_dir = os.path.join(base_dir, "test")

        #     # Run pytest command targeting the test directory
        #     result = subprocess.run(
        #         ["pytest", test_dir], capture_output=True, text=True
        #     )
        #     output = result.stdout + "\n" + result.stderr

        #     # Parse pytest summary results via regex
        #     passed_match = re.search(r"(\d+)\s+passed", output)
        #     failed_match = re.search(r"(\d+)\s+failed", output)
        #     error_match = re.search(r"(\d+)\s+errors?", output)

        #     passed_cases = int(passed_match.group(1)) if passed_match else 0
        #     failed = int(failed_match.group(1)) if failed_match else 0
        #     errors = int(error_match.group(1)) if error_match else 0

        #     failed_cases = failed + errors
        #     total_cases = passed_cases + failed_cases

        #     passed_percentage = (
        #         (passed_cases / total_cases * 100) if total_cases > 0 else 0
        #     )
        #     failed_percentage = (
        #         (failed_cases / total_cases * 100) if total_cases > 0 else 0
        #     )

        #     return Response(
        #         results={
        #             "total_cases": total_cases,
        #             "passed_percentage": round(passed_percentage, 2),
        #             "failed_percentage": round(failed_percentage, 2),
        #             "passed_cases": passed_cases,
        #             "failed_cases": failed_cases,
        #         },
        #         status=status.HTTP_200_OK,
        #     )
        # except Exception as e:
        #     return Response(
        #         {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        #     )

        try:
            base_dir = getattr(settings, "BASE_DIR", "")
            # Path from pytest.ini: --html=./test/reports/report.html
            report_path = os.path.join(base_dir, "test", "reports", "report.html")
            if not os.path.exists(report_path):
                return Response(
                    {"error": "Test report 'report.html' not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            with open(report_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, "html.parser")
            # Extract all text from the html, separated by spaces to ensure words don't merge
            text_content = soup.get_text(separator=" ")

            passed_match = re.search(r"(\d+)\s+passed", text_content, re.IGNORECASE)
            failed_match = re.search(r"(\d+)\s+failed", text_content, re.IGNORECASE)
            error_match = re.search(r"(\d+)\s+errors?", text_content, re.IGNORECASE)

            passed_cases = int(passed_match.group(1)) if passed_match else 0
            failed = int(failed_match.group(1)) if failed_match else 0
            errors = int(error_match.group(1)) if error_match else 0

            failed_cases = failed + errors
            total_cases = passed_cases + failed_cases

            passed_percentage = (
                (passed_cases / total_cases * 100) if total_cases > 0 else 0
            )
            failed_percentage = (
                (failed_cases / total_cases * 100) if total_cases > 0 else 0
            )

            return Response(
                {
                    "total_cases": total_cases,
                    "passed_percentage": round(passed_percentage, 2),
                    "failed_percentage": round(failed_percentage, 2),
                    "passed_cases": passed_cases,
                    "failed_cases": failed_cases,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
