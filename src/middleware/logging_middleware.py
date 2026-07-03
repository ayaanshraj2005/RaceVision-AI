import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("RaceVisionAPI")
logger.setLevel(logging.INFO)

# Ensure console logging format is registered
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request metadata
        client_host = request.client.host if request.client else "unknown"
        logger.info(f"Incoming Request: {request.method} {request.url.path} from client {client_host}")
        
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            
            # Log response metrics
            logger.info(
                f"Completed: {request.method} {request.url.path} | "
                f"Status: {response.status_code} | "
                f"Latency: {process_time:.2f}ms"
            )
            return response
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"Request Failed: {request.method} {request.url.path} | "
                f"Error: {str(e)} | "
                f"Latency: {process_time:.2f}ms"
            )
            raise e
