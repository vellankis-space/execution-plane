"""
Authentication and authorization API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

from services.auth_service import AuthService
from core.database import get_db

router = APIRouter()
security = HTTPBearer()


# Request/Response models
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    tenant_id: Optional[str] = None
    roles: Optional[List[str]] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    user_id: str
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    tenant_id: Optional[str]
    roles: List[str]
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    session_token: str


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str]
    is_system_role: bool = False


class TenantCreate(BaseModel):
    name: str
    domain: Optional[str] = None
    settings: Optional[dict] = None


# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user from JWT token"""
    auth_service = AuthService(db)
    
    token = credentials.credentials
    payload = auth_service.verify_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await auth_service.get_user_by_id(payload.get("user_id"))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


# Dependency to check if user is superuser
async def get_current_superuser(current_user = Depends(get_current_user)):
    """Check if current user is superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


# Authentication Endpoints

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    try:
        auth_service = AuthService(db)
        user = await auth_service.create_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name,
            tenant_id=user_data.tenant_id,
            roles=user_data.roles or []
        )
        
        return UserResponse(
            user_id=user.user_id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            tenant_id=user.tenant_id,
            roles=user.roles or [],
            created_at=user.created_at.isoformat() if user.created_at else ""
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


@router.post("/login", response_model=LoginResponse)
async def login(
    email: EmailStr = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    try:
        auth_service = AuthService(db)
        user = await auth_service.authenticate_user(email, password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create access token
        access_token = auth_service.create_access_token(user)
        
        # Create session
        session = await auth_service.create_session(
            user.user_id,
            ip_address=None,
            user_agent=None
        )
        
        return LoginResponse(
            access_token=access_token,
            user=UserResponse(
                user_id=user.user_id,
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                tenant_id=user.tenant_id,
                roles=user.roles or [],
                created_at=user.created_at.isoformat() if user.created_at else ""
            ),
            session_token=session.token
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during login: {str(e)}")


@router.post("/logout")
async def logout(
    current_user = Depends(get_current_user),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Logout and revoke session"""
    try:
        auth_service = AuthService(db)
        
        # Extract token from Authorization header
        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
            # Revoke session if using session-based auth
            # For JWT, we can't revoke it, but we can revoke the session token
            await auth_service.revoke_session(token)
        
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during logout: {str(e)}")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        tenant_id=current_user.tenant_id,
        roles=current_user.roles or [],
        created_at=current_user.created_at.isoformat() if current_user.created_at else ""
    )


# User Management Endpoints (Admin only)

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    try:
        from models.user import User
        
        users = db.query(User).offset(skip).limit(limit).all()
        return [
            UserResponse(
                user_id=user.user_id,
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                tenant_id=user.tenant_id,
                roles=user.roles or [],
                created_at=user.created_at.isoformat() if user.created_at else ""
            )
            for user in users
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    updates: dict,
    current_user = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """Update user (admin only)"""
    try:
        auth_service = AuthService(db)
        user = await auth_service.update_user(user_id, updates)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User updated successfully", "user_id": user.user_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Role Management Endpoints

@router.post("/roles")
async def create_role(
    role_data: RoleCreate,
    current_user = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """Create a new role (admin only)"""
    try:
        auth_service = AuthService(db)
        role = await auth_service.create_role(
            name=role_data.name,
            description=role_data.description,
            permissions=role_data.permissions,
            is_system_role=role_data.is_system_role
        )
        return {
            "role_id": role.role_id,
            "name": role.name,
            "permissions": role.permissions
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/roles")
async def get_roles(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all roles"""
    try:
        auth_service = AuthService(db)
        roles = await auth_service.get_all_roles()
        return [
            {
                "role_id": role.role_id,
                "name": role.name,
                "description": role.description,
                "permissions": role.permissions,
                "is_system_role": role.is_system_role
            }
            for role in roles
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Tenant Management Endpoints

@router.post("/tenants")
async def create_tenant(
    tenant_data: TenantCreate,
    current_user = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """Create a new tenant (admin only)"""
    try:
        auth_service = AuthService(db)
        tenant = await auth_service.create_tenant(
            name=tenant_data.name,
            domain=tenant_data.domain,
            settings=tenant_data.settings
        )
        return {
            "tenant_id": tenant.tenant_id,
            "name": tenant.name,
            "domain": tenant.domain
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tenants")
async def get_tenants(
    current_user = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """Get all tenants (admin only)"""
    try:
        from models.user import Tenant
        
        tenants = db.query(Tenant).all()
        return [
            {
                "tenant_id": tenant.tenant_id,
                "name": tenant.name,
                "domain": tenant.domain,
                "is_active": tenant.is_active
            }
            for tenant in tenants
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

