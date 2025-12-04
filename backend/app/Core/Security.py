
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from collections import defaultdict

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_counts = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Current time
        now = time.time()
        
        # Filter out old requests from the window
        self.request_counts[client_ip] = [
            timestamp for timestamp in self.request_counts[client_ip]
            if now - timestamp < self.window_seconds
        ]
        
        # Check if limit exceeded
        if len(self.request_counts[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"error": "Too many requests. Please try again later."}
            )
        
        # Add current request
        self.request_counts[client_ip].append(now)
        
        # Proceed
        response = await call_next(request)
        return response
