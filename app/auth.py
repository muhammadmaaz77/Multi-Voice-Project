from fastapi import Header, HTTPException, status
from app.config import settings

async def verify_api_key(x_api_key: str = Header(None)):
    """Verify standard API key for user endpoints."""
    if not x_api_key or x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return x_api_key

async def verify_admin_key(x_admin_key: str = Header(None)):
    """Verify admin API key for admin-only endpoints."""
    if not x_admin_key or x_admin_key != settings.ADMIN_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin key"
        )
    return x_admin_key