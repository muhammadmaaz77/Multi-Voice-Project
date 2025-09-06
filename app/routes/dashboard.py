"""
Dashboard routes for Phase 5A
Serves the analytics dashboard HTML interface.
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, FileResponse

from ..auth import verify_admin_key

router = APIRouter()

@router.get("/dashboard", response_class=HTMLResponse)
async def analytics_dashboard(
    request: Request,
    admin_key: str = Depends(verify_admin_key)
):
    """
    Serve the analytics dashboard. Requires admin authentication.
    """
    try:
        # Serve the static HTML file directly
        import os
        dashboard_path = os.path.join("templates", "analytics_dashboard.html")
        if os.path.exists(dashboard_path):
            return FileResponse(dashboard_path, media_type="text/html")
        else:
            return HTMLResponse("""
            <html>
                <head><title>Analytics Dashboard</title></head>
                <body>
                    <h1>Analytics Dashboard</h1>
                    <p>Dashboard template not found. Please ensure templates/analytics_dashboard.html exists.</p>
                </body>
            </html>
            """)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving dashboard: {str(e)}")

@router.get("/dashboard/health")
async def dashboard_health():
    """Dashboard service health check."""
    return {
        "service": "dashboard",
        "status": "healthy",
        "template_engine": "jinja2"
    }
