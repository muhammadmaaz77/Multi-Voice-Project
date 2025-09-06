"""
Analytics API routes for Phase 5A
REST endpoints for analytics data and dashboard.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional

from ..auth import verify_api_key, verify_admin_key
from ..services.analytics.analytics_service import analytics_service

router = APIRouter()

@router.get("/analytics/dashboard")
async def get_analytics_dashboard(
    days: int = Query(30, ge=1, le=365, description="Number of days to include in analytics"),
    admin_key: str = Depends(verify_admin_key)
):
    """
    Get analytics dashboard data. Requires admin authentication.
    
    - **days**: Number of days to include (1-365, default: 30)
    """
    try:
        dashboard_data = analytics_service.get_dashboard_data(days=days)
        
        return {
            "success": True,
            "data": dashboard_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving dashboard data: {str(e)}")

@router.get("/analytics/sessions/{session_id}")
async def get_session_analytics(
    session_id: str,
    admin_key: str = Depends(verify_admin_key)
):
    """
    Get detailed analytics for a specific session. Requires admin authentication.
    """
    try:
        session_data = analytics_service.get_session_details(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "success": True,
            "session": session_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session analytics: {str(e)}")

@router.get("/analytics/users/{user_id}")
async def get_user_analytics(
    user_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    admin_key: str = Depends(verify_admin_key)
):
    """
    Get analytics for a specific user. Requires admin authentication.
    
    - **days**: Number of days to include (1-365, default: 30)
    """
    try:
        user_data = analytics_service.get_user_analytics(user_id=user_id, days=days)
        
        return {
            "success": True,
            "user_analytics": user_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user analytics: {str(e)}")

@router.get("/analytics/my-usage")
async def get_my_usage_analytics(
    days: int = Query(30, ge=1, le=90, description="Number of days to include"),
    api_key: str = Depends(verify_api_key)
):
    """
    Get usage analytics for the authenticated user.
    
    - **days**: Number of days to include (1-90, default: 30)
    """
    try:
        user_data = analytics_service.get_user_analytics(user_id=api_key, days=days)
        
        # Remove sensitive admin information
        sanitized_data = {
            "date_range": user_data["date_range"],
            "summary": {
                "total_sessions": user_data["summary"]["total_sessions"],
                "total_messages": user_data["summary"]["total_messages"],
                "total_audio_minutes": user_data["summary"]["total_audio_minutes"],
                "avg_session_duration": user_data["summary"]["avg_session_duration"],
                "feature_usage": user_data["summary"]["feature_usage"]
            },
            "recent_sessions": [
                {
                    "session_id": s["session_id"],
                    "start_time": s["start_time"],
                    "duration_seconds": s["duration_seconds"],
                    "message_count": s["message_count"],
                    "features_used": s["features_used"]
                }
                for s in user_data["sessions"][:10]  # Only last 10 sessions
            ]
        }
        
        return {
            "success": True,
            "usage": sanitized_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving usage analytics: {str(e)}")

@router.post("/analytics/track/session-start")
async def track_session_start(
    session_id: str,
    language: str = "en",
    api_key: str = Depends(verify_api_key)
):
    """
    Start tracking a new session. (Internal API)
    """
    try:
        analytics_service.start_session(
            session_id=session_id,
            user_id=api_key,
            language=language
        )
        
        return {
            "success": True,
            "message": "Session tracking started",
            "session_id": session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting session tracking: {str(e)}")

@router.post("/analytics/track/session-end")
async def track_session_end(
    session_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    End session tracking. (Internal API)
    """
    try:
        analytics_service.end_session(session_id)
        
        return {
            "success": True,
            "message": "Session tracking ended",
            "session_id": session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ending session tracking: {str(e)}")

@router.post("/analytics/track/message")
async def track_message(
    session_id: str,
    tokens_used: int = 0,
    api_key: str = Depends(verify_api_key)
):
    """
    Track a message in a session. (Internal API)
    """
    try:
        analytics_service.track_message(
            session_id=session_id,
            tokens_used=tokens_used
        )
        
        return {
            "success": True,
            "message": "Message tracked"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking message: {str(e)}")

@router.post("/analytics/track/audio")
async def track_audio_usage(
    session_id: str,
    duration_seconds: float,
    api_key: str = Depends(verify_api_key)
):
    """
    Track audio usage in a session. (Internal API)
    """
    try:
        analytics_service.track_audio(
            session_id=session_id,
            duration_seconds=duration_seconds
        )
        
        return {
            "success": True,
            "message": "Audio usage tracked"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking audio usage: {str(e)}")

@router.post("/analytics/track/feature")
async def track_feature_usage(
    session_id: str,
    feature: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Track feature usage in a session. (Internal API)
    """
    try:
        analytics_service.track_feature_usage(
            session_id=session_id,
            feature=feature
        )
        
        return {
            "success": True,
            "message": "Feature usage tracked",
            "feature": feature
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking feature usage: {str(e)}")

@router.post("/analytics/track/endpoint")
async def track_endpoint_call(
    session_id: str,
    endpoint: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Track API endpoint usage. (Internal API)
    """
    try:
        analytics_service.track_endpoint_call(
            session_id=session_id,
            endpoint=endpoint
        )
        
        return {
            "success": True,
            "message": "Endpoint call tracked",
            "endpoint": endpoint
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking endpoint call: {str(e)}")

@router.post("/analytics/track/error")
async def track_error(
    session_id: str,
    error: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Track an error in a session. (Internal API)
    """
    try:
        analytics_service.track_error(
            session_id=session_id,
            error=error
        )
        
        return {
            "success": True,
            "message": "Error tracked"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking error: {str(e)}")

@router.get("/analytics/active-sessions")
async def get_active_sessions(admin_key: str = Depends(verify_admin_key)):
    """
    Get currently active sessions. Requires admin authentication.
    """
    try:
        active_sessions = [
            {
                "session_id": session_id,
                "user_id": data["user_id"],
                "start_time": data["start_time"],
                "language": data["language"],
                "message_count": data["message_count"],
                "audio_minutes": round(data["audio_minutes"], 2),
                "features_used": list(data["features_used"])
            }
            for session_id, data in analytics_service.active_sessions.items()
        ]
        
        return {
            "success": True,
            "active_sessions": active_sessions,
            "count": len(active_sessions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving active sessions: {str(e)}")

@router.get("/analytics/health")
async def analytics_health():
    """Analytics service health check."""
    try:
        return {
            "service": "analytics",
            "status": "healthy",
            "active_sessions": len(analytics_service.active_sessions),
            "total_sessions_tracked": len(analytics_service.sessions),
            "daily_metrics_available": len(analytics_service.daily_metrics)
        }
        
    except Exception as e:
        return {
            "service": "analytics",
            "status": "error",
            "error": str(e)
        }

@router.get("/analytics/export")
async def export_analytics_data(
    days: int = Query(30, ge=1, le=365, description="Number of days to export"),
    format: str = Query("json", description="Export format"),
    admin_key: str = Depends(verify_admin_key)
):
    """
    Export analytics data. Requires admin authentication.
    
    - **days**: Number of days to export (1-365, default: 30)
    - **format**: Export format (currently only 'json' supported)
    """
    try:
        if format != "json":
            raise HTTPException(status_code=400, detail="Only JSON format is currently supported")
        
        dashboard_data = analytics_service.get_dashboard_data(days=days)
        
        # Add export metadata
        from datetime import datetime
        export_data = {
            "export_metadata": {
                "exported_at": datetime.now().isoformat(),
                "days_included": days,
                "format": format
            },
            "analytics_data": dashboard_data
        }
        
        return {
            "success": True,
            "export": export_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting analytics data: {str(e)}")
