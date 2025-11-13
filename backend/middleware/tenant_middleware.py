"""
Tenant context middleware for multi-tenancy support
"""
import logging
from typing import Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from services.auth_service import AuthService
from core.database import get_db

logger = logging.getLogger(__name__)


class TenantContext:
    """Thread-local tenant context"""
    def __init__(self):
        self._tenant_id: Optional[str] = None
        self._user_id: Optional[str] = None
    
    def set_tenant(self, tenant_id: str, user_id: Optional[str] = None):
        """Set the current tenant context"""
        self._tenant_id = tenant_id
        self._user_id = user_id
    
    def get_tenant_id(self) -> Optional[str]:
        """Get the current tenant ID"""
        return self._tenant_id
    
    def get_user_id(self) -> Optional[str]:
        """Get the current user ID"""
        return self._user_id
    
    def clear(self):
        """Clear the tenant context"""
        self._tenant_id = None
        self._user_id = None


# Global tenant context (thread-local would be better, but this works for now)
tenant_context = TenantContext()


class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware to extract and set tenant context from request"""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and set tenant context"""
        # Clear context at start
        tenant_context.clear()
        
        # Try to get tenant from various sources
        tenant_id = None
        user_id = None
        
        # 1. Check Authorization header (JWT token)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                # Decode JWT to get tenant_id and user_id
                from services.auth_service import AuthService
                db = next(get_db())
                try:
                    auth_service = AuthService(db)
                    user = await auth_service.get_user_from_token(token)
                    if user:
                        tenant_id = user.tenant_id
                        user_id = user.user_id
                finally:
                    db.close()
            except Exception as e:
                logger.debug(f"Could not extract tenant from token: {e}")
        
        # 2. Check X-Tenant-ID header (for API calls)
        if not tenant_id:
            tenant_id = request.headers.get("X-Tenant-ID")
        
        # 3. Check query parameter (for development/testing)
        if not tenant_id:
            tenant_id = request.query_params.get("tenant_id")
        
        # Set tenant context if found
        if tenant_id:
            tenant_context.set_tenant(tenant_id, user_id)
            logger.debug(f"Tenant context set: {tenant_id}")
        
        # Process request
        response = await call_next(request)
        
        # Clear context after request
        tenant_context.clear()
        
        return response


def get_current_tenant_id() -> Optional[str]:
    """Get the current tenant ID from context"""
    return tenant_context.get_tenant_id()


def require_tenant() -> str:
    """Require tenant context, raise exception if not set"""
    tenant_id = tenant_context.get_tenant_id()
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant context required"
        )
    return tenant_id

