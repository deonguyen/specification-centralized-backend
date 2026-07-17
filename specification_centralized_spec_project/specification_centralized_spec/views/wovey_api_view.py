from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import json

import base64
import requests


API_KEY = "wovey_qSPIcTmTxgGO4DKPxj3Po_uI04IQi03g-ZWS5MXXqeQ"
BASE_URL = "https://wovey-api.woven.tech/vertexai/project/sq_spec_trial/v1"

class WoveyAPIView(viewsets.ViewSet):
    """
    API endpoint that allows interaction with Wovey AI.
    """

    permission_classes = [permissions.IsAuthenticated]
    
    def get_diff_summary(self, content1, content2):
        # 1. Convert string to bytes
        content1_bytes = content1.encode("utf-8")
        # 2. Base64 encode the bytes
        content1_base64_bytes = base64.b64encode(content1_bytes)
        # 3. Convert Base64 bytes back to a string
        content1_base64_string = content1_base64_bytes.decode("utf-8")

        # 1. Convert string to bytes
        content2_bytes = content2.encode("utf-8")
        # 2. Base64 encode the bytes
        content2_base64_bytes = base64.b64encode(content2_bytes)
        # 3. Convert Base64 bytes back to a string
        content2_base64_string = content2_base64_bytes.decode("utf-8")
        
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": "Please compare the following two documents and summarize the differences."
                        },
                        {
                            "inlineData": {
                                "mimeType": "text/plain",
                                "data": content1_base64_string,
                            }
                        },
                        {
                            "inlineData": {
                                "mimeType": "text/plain",
                                "data": content2_base64_string,
                            }
                        },
                    ],
                }
            ],
        }

        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        response = requests.post(
            f"{BASE_URL}/publishers/google/models/gemini-2.5-pro:generateContent",
            headers=headers,
            json=payload,
        )
        json_data = json.loads(response.text)
        print(json_data.get("candidates")[0]
                            .get("content")
                            .get("parts")[0]
                            .get("text"))
        return response
    
    @action(detail=False, methods=["post"])
    def diffsummary(self, request) -> Response:
        content1 = request.data.get("content1")
        content2 = request.data.get("content2")

        if content1 is None or content2 is None:
            return Response(
                {"error": "Both 'content1' and 'content2' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        summary = self.get_diff_summary(content1, content2)
        return Response({"summary": summary}, status=status.HTTP_200_OK)