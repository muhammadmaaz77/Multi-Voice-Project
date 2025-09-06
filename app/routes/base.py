from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    """Root endpoint for service status."""
    return {"message": "Voice AI Bot Backend is running"}

@router.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}
