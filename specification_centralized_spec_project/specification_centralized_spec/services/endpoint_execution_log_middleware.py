ENABLE_ENDPOINT_EXECUTION_LOG = True # Set to False to disable the log
import logging
import time
from django.conf import settings

logger = logging.getLogger(__name__)

class EndpointExecutionLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the endpoint execution log is enabled in settings
        if not getattr(settings, 'ENABLE_ENDPOINT_EXECUTION_LOG', False):
            return self.get_response(request)

        start_time = time.time()
        
        response = self.get_response(request)
        
        execution_time = time.time() - start_time

        logger.info(
            f"Endpoint: {request.path} | Method: {request.method} | Status: {response.status_code} | Execution Time: {execution_time:.4f}s"
        )

        return response