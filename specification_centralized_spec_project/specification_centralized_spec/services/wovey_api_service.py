
import base64
import json
import requests

API_KEY = "wovey_RXOrAttehDax1XrdUyBplR8Iu0ow_TXzrf7KE0kr_18"
BASE_URL = "https://wovey-api.woven.tech/vertexai/project/sq_spec_trial/v1"

def compare_diff_summary(content1, content2):
    try:
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
            f"{BASE_URL}/publishers/google/models/gemini-3.5-flash:generateContent",
            headers=headers,
            json=payload,
        )
        if response.status_code != 200:
            return None, response.status_code
        json_data = json.loads(response.text)
        result = json_data.get("candidates")[0].get("content").get("parts")[0].get("text")
        print(result)
        return result, response.status_code
    except Exception as e:
        print(f"Error in get_diff_summary: {e}")
        raise

def generate_diagram(input_data, output_data):
    try:
        # 1. Convert string to bytes
        input_bytes = ("Input description: " + input_data).encode("utf-8")
        # 2. Base64 encode the bytes
        input_base64_bytes = base64.b64encode(input_bytes)
        # 3. Convert Base64 bytes back to a string
        input_base64_string = input_base64_bytes.decode("utf-8")

        # 1. Convert string to bytes
        output_bytes = ("Output description: " + output_data).encode("utf-8")
        # 2. Base64 encode the bytes
        output_base64_bytes = base64.b64encode(output_bytes)
        # 3. Convert Base64 bytes back to a string
        output_base64_string = output_base64_bytes.decode("utf-8")

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": "You are an expert software architect. Your task is to generate a diagram in the Mermaid JS format based on the provided input and output descriptions. Only return the Mermaid JS code and exclude all other information."
                        },
                        {
                            "inlineData": {
                                "mimeType": "text/plain",
                                "data": input_base64_string,
                            }
                        },
                        {
                            "inlineData": {
                                "mimeType": "text/plain",
                                "data": output_base64_string,
                            }
                        },
                    ],
                }
            ],
        }

        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        response = requests.post(
            f"{BASE_URL}/publishers/google/models/gemini-3.5-flash:generateContent",
            headers=headers,
            json=payload,
        )
        if response.status_code != 200:
            return None, response.status_code
        json_data = json.loads(response.text)
        result = json_data.get("candidates")[0].get("content").get("parts")[0].get("text")
        print(result)
        return result, response.status_code
    except Exception as e:
        print(f"Error in generate_diagram: {e}")
        raise

def generate_test_cases(content):
    """
    Uses Google Vertex AI to generate test cases based on specification content.
    """
    try:
        # 1. Convert string to bytes
        specification_bytes = ("Specification: " + content).encode("utf-8")
        # 2. Base64 encode the bytes
        specification_base64_bytes = base64.b64encode(specification_bytes)
        # 3. Convert Base64 bytes back to a string
        specification_base64_string = specification_base64_bytes.decode("utf-8")

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": "As an expert QA engineer, generate a comprehensive suite of test cases based on the following specification"
                        },
                        {
                            "inlineData": {
                                "mimeType": "text/plain",
                                "data": specification_base64_string,
                            }
                        },
                        {
                            "text": """
                                    Provide the output STRICTLY as a JSON object with the following structure,
                                    without any markdown formatting or additional text:
                                    {
                                        "test_suite_name": "A descriptive name for the test suite",
                                        "test_suite_code": "A unique identifier or code for the test suite, identifier or code must be include header of specification content",
                                        "test_suite_status": "Status of the test suite (e.g., Draft, Active)",
                                        "test_cases": [
                                            {
                                                "name": "Test Case Title",
                                                "code": "A unique identifier or code for the test case, identifier or code must be include header of specification content",
                                                "status": "Status of the test case (e.g., Draft, Active)",
                                                "description": "Description of the test case",
                                                "steps": "Steps to execute",
                                                "expected_result": "Expected outcome"
                                            }
                                        ]
                                    }
                                    """
                        },
                    ],
                }
            ],
        }

        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        response = requests.post(
            f"{BASE_URL}/publishers/google/models/gemini-3.5-flash:generateContent",
            headers=headers,
            json=payload,
        )
        if response.status_code != 200:
            return None, response.status_code
        json_data = json.loads(response.text)
        result = json_data.get("candidates")[0].get("content").get("parts")[0].get("text")
        print(result)
        return result, response.status_code
    except Exception as e:
        print(f"Error in generate_diagram: {e}")
        raise