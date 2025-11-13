"""
Audit middleware for automatic request logging
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
from typing import Callable

from services.audit_service import AuditService
from core.database import SessionLocal


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically log API requests"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.excluded_paths = [
            "/docs",
            "/openapi.json",
            "/redoc",
            "/health",
            "/metrics"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip audit logging for excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Get user from request state (set by auth middleware if available)
        user_id = getattr(request.state, "user_id", None)
        tenant_id = getattr(request.state, "tenant_id", None)
        
        # Extract action and resource from path
        action, resource_type, resource_id = self._parse_request_path(request)
        
        start_time = time.time()
        status_code = 200
        error_message = None
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            success = status_code < 400
        except Exception as e:
            status_code = 500
            error_message = str(e)
            success = False
            raise
        finally:
            # Log the request
            try:
                db = SessionLocal()
                audit_service = AuditService(db)
                
                await audit_service.log_action(
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    user_id=user_id,
                    tenant_id=tenant_id,
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                    request_method=request.method,
                    request_path=request.url.path,
                    status_code=status_code,
                    success=success,
                    error_message=error_message,
                    metadata={
                        "execution_time": time.time() - start_time,
                        "query_params": dict(request.query_params)
                    }
                )
                db.close()
            except Exception as e:
                # Don't fail the request if audit logging fails
                print(f"Error logging audit: {str(e)}")
        
        return response
    
    def _parse_request_path(self, request: Request) -> tuple:
        """Parse request path to extract action, resource type, and resource ID"""
        path_parts = request.url.path.strip("/").split("/")
        
        # Remove API version prefix if present
        if len(path_parts) > 0 and path_parts[0] == "api":
            path_parts = path_parts[2:]  # Skip "api" and "v1"
        
        if len(path_parts) == 0:
            return "unknown", "unknown", None
        
        resource_type = path_parts[0]
        resource_id = path_parts[1] if len(path_parts) > 1 else None
        
        # Determine action from HTTP method
        method = request.method.upper()
        if method == "GET":
            action = "read"
        elif method == "POST":
            action = "create"
        elif method == "PUT" or method == "PATCH":
            action = "update"
        elif method == "DELETE":
            action = "delete"
        else:
            action = method.lower()
        
        return action, resource_type, resource_id

