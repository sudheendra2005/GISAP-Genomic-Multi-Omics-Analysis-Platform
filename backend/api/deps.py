from typing import Optional
from fastapi import Header, HTTPException, Depends, status
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.core.config import settings
from backend.core.security import decode_access_token

def get_tenant_id(x_tenant_id: Optional[str] = Header(None)) -> str:
    """
    Enforces tenant context from header or default tenant.
    """
    if x_tenant_id:
        return x_tenant_id
    return settings.DEFAULT_TENANT_ID

def get_current_user(
    authorization: Optional[str] = Header(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
) -> dict:
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        payload = decode_access_token(token)
        if payload:
            return payload

    # Default developer user context for alpha testbed
    return {
        "sub": "usr-default",
        "email": "analyst@gisap.org",
        "role": "bioinformatician",
        "tenant_id": tenant_id
    }

def require_role(allowed_roles: list):
    def role_checker(current_user: dict = Depends(get_current_user)):
        role = current_user.get("role", "viewer")
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires one of roles: {allowed_roles}"
            )
        return current_user
    return role_checker
