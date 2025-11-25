"""
Authentication and authorization service
"""
import uuid
import hashlib
import secrets
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_
from passlib.context import CryptContext
import jwt

from models.user import User, UserSession, Role, Tenant
from core.config import settings

logger = logging.getLogger(__name__)

# Password hashing context - support both argon2 and bcrypt
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

# JWT settings
JWT_SECRET_KEY = settings.SECRET_KEY
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


class AuthService:
    """Service for authentication and authorization"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Password Management
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}")
            return False
    
    # User Management
    
    async def create_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None,
        tenant_id: Optional[str] = None,
        roles: Optional[List[str]] = None,
        is_superuser: bool = False
    ) -> User:
        """Create a new user"""
        # Check if user already exists
        existing_user = self.db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            raise ValueError("User with this email or username already exists")
        
        user_id = str(uuid.uuid4())
        hashed_password = self.hash_password(password)
        
        user = User(
            user_id=user_id,
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            tenant_id=tenant_id,
            roles=roles or [],
            is_superuser=is_superuser,
            is_active=True
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by user_id"""
        return self.db.query(User).filter(User.user_id == user_id).first()
    
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[User]:
        """Update user information"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Don't allow direct password updates through this method
        if "password" in updates:
            updates["hashed_password"] = self.hash_password(updates.pop("password"))
        
        for key, value in updates.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        setattr(user, 'updated_at', datetime.utcnow())
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    # Authentication
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        
        if not user.is_active:
            raise ValueError("User account is inactive")
        
        if not self.verify_password(password, user.hashed_password):
            return None
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        self.db.commit()
        
        return user
    
    async def create_session(
        self,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserSession:
        """Create a user session"""
        session_id = str(uuid.uuid4())
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
        
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            is_active=True
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    async def get_session_by_token(self, token: str) -> Optional[UserSession]:
        """Get session by token"""
        session = self.db.query(UserSession).filter(
            and_(
                UserSession.token == token,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            )
        ).first()
        
        return session
    
    async def revoke_session(self, token: str) -> bool:
        """Revoke a session"""
        session = await self.get_session_by_token(token)
        if not session:
            return False
        
        session.is_active = False
        self.db.commit()
        return True
    
    async def revoke_all_user_sessions(self, user_id: str) -> int:
        """Revoke all sessions for a user"""
        sessions = self.db.query(UserSession).filter(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            )
        ).all()
        
        count = 0
        for session in sessions:
            session.is_active = False
            count += 1
        
        self.db.commit()
        return count
    
    # JWT Token Management
    
    def create_access_token(self, user: User) -> str:
        """Create a JWT access token"""
        now = datetime.now(timezone.utc)
        exp_time = now + timedelta(hours=JWT_EXPIRATION_HOURS)
        
        payload = {
            "user_id": user.user_id,
            "email": user.email,
            "username": user.username,
            "roles": user.roles,
            "is_superuser": user.is_superuser,
            "tenant_id": user.tenant_id,
            "exp": int(exp_time.timestamp()),  # Convert to Unix timestamp
            "iat": int(now.timestamp())  # Convert to Unix timestamp
        }
        
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token
    
    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
    
    # Authorization
    
    async def check_permission(self, user: User, permission: str) -> bool:
        """Check if user has a specific permission"""
        # Superusers have all permissions
        if user.is_superuser:
            return True
        
        # Check direct permissions
        if permission in (user.permissions or []):
            return True
        
        # Check role-based permissions
        if user.roles:
            roles = self.db.query(Role).filter(Role.name.in_(user.roles)).all()
            for role in roles:
                if permission in (role.permissions or []):
                    return True
        
        return False
    
    async def has_role(self, user: User, role_name: str) -> bool:
        """Check if user has a specific role"""
        if user.is_superuser:
            return True
        
        return role_name in (user.roles or [])
    
    # Role Management
    
    async def create_role(
        self,
        name: str,
        permissions: List[str],
        description: Optional[str] = None,
        is_system_role: bool = False
    ) -> Role:
        """Create a new role"""
        # Check if role already exists
        existing_role = self.db.query(Role).filter(Role.name == name).first()
        if existing_role:
            raise ValueError("Role with this name already exists")
        
        role_id = str(uuid.uuid4())
        
        role = Role(
            role_id=role_id,
            name=name,
            description=description,
            permissions=permissions,
            is_system_role=is_system_role
        )
        
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        
        return role
    
    async def get_role_by_name(self, name: str) -> Optional[Role]:
        """Get role by name"""
        return self.db.query(Role).filter(Role.name == name).first()
    
    async def get_all_roles(self) -> List[Role]:
        """Get all roles"""
        return self.db.query(Role).all()
    
    # Tenant Management
    
    async def create_tenant(
        self,
        name: str,
        domain: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> Tenant:
        """Create a new tenant"""
        tenant_id = str(uuid.uuid4())
        
        tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            domain=domain,
            settings=settings or {},
            is_active=True
        )
        
        self.db.add(tenant)
        self.db.commit()
        self.db.refresh(tenant)
        
        return tenant
    
    async def get_tenant_by_id(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID"""
        return self.db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    
    async def get_tenant_by_domain(self, domain: str) -> Optional[Tenant]:
        """Get tenant by domain"""
        return self.db.query(Tenant).filter(Tenant.domain == domain).first()

