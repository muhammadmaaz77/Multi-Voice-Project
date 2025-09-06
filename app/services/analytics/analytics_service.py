"""
Analytics service for Phase 5A
Tracks usage metrics, session analytics, and provides dashboard data.
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import asyncio

@dataclass
class SessionMetric:
    """Session analytics data structure."""
    session_id: str
    user_id: str
    start_time: str
    end_time: Optional[str]
    duration_seconds: float
    message_count: int
    audio_minutes: float
    tokens_used: int
    language: str
    features_used: List[str]
    endpoint_calls: Dict[str, int]
    errors: List[str]

@dataclass
class UsageMetric:
    """Usage analytics data structure."""
    date: str
    total_sessions: int
    total_users: int
    total_messages: int
    total_audio_minutes: float
    total_tokens: int
    avg_session_duration: float
    top_features: List[str]
    error_rate: float
    endpoint_usage: Dict[str, int]

class AnalyticsService:
    """Manages analytics collection and reporting."""
    
    def __init__(self, storage_path: str = "analytics"):
        self.storage_path = storage_path
        self.sessions: Dict[str, SessionMetric] = {}
        self.daily_metrics: Dict[str, UsageMetric] = {}
        self.active_sessions: Dict[str, Dict] = {}
        self._ensure_storage_directory()
        self._load_existing_data()
    
    def _ensure_storage_directory(self):
        """Ensure analytics storage directory exists."""
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "sessions"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "daily"), exist_ok=True)
    
    def _load_existing_data(self):
        """Load existing analytics data."""
        try:
            # Load recent sessions (last 30 days)
            sessions_dir = os.path.join(self.storage_path, "sessions")
            if os.path.exists(sessions_dir):
                cutoff_date = datetime.now() - timedelta(days=30)
                
                for filename in os.listdir(sessions_dir):
                    if filename.endswith('.json'):
                        file_path = os.path.join(sessions_dir, filename)
                        file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                        
                        if file_date >= cutoff_date:
                            with open(file_path, 'r') as f:
                                session_data = json.load(f)
                                session = SessionMetric(**session_data)
                                self.sessions[session.session_id] = session
            
            # Load daily metrics (last 90 days)
            daily_dir = os.path.join(self.storage_path, "daily")
            if os.path.exists(daily_dir):
                cutoff_date = datetime.now() - timedelta(days=90)
                
                for filename in os.listdir(daily_dir):
                    if filename.endswith('.json'):
                        date_str = filename.replace('.json', '')
                        try:
                            file_date = datetime.strptime(date_str, '%Y-%m-%d')
                            if file_date >= cutoff_date:
                                file_path = os.path.join(daily_dir, filename)
                                with open(file_path, 'r') as f:
                                    metric_data = json.load(f)
                                    metric = UsageMetric(**metric_data)
                                    self.daily_metrics[date_str] = metric
                        except ValueError:
                            continue
                            
        except Exception as e:
            print(f"Error loading analytics data: {e}")
    
    def start_session(self, session_id: str, user_id: str, language: str = "en"):
        """Start tracking a new session."""
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "start_time": datetime.now().isoformat(),
            "language": language,
            "message_count": 0,
            "audio_minutes": 0.0,
            "tokens_used": 0,
            "features_used": set(),
            "endpoint_calls": defaultdict(int),
            "errors": []
        }
    
    def end_session(self, session_id: str):
        """End session tracking and save metrics."""
        if session_id not in self.active_sessions:
            return
        
        session_data = self.active_sessions[session_id]
        end_time = datetime.now()
        start_time = datetime.fromisoformat(session_data["start_time"])
        duration = (end_time - start_time).total_seconds()
        
        # Create session metric
        session_metric = SessionMetric(
            session_id=session_id,
            user_id=session_data["user_id"],
            start_time=session_data["start_time"],
            end_time=end_time.isoformat(),
            duration_seconds=duration,
            message_count=session_data["message_count"],
            audio_minutes=session_data["audio_minutes"],
            tokens_used=session_data["tokens_used"],
            language=session_data["language"],
            features_used=list(session_data["features_used"]),
            endpoint_calls=dict(session_data["endpoint_calls"]),
            errors=session_data["errors"]
        )
        
        self.sessions[session_id] = session_metric
        del self.active_sessions[session_id]
        
        # Save session data
        self._save_session_data(session_metric)
        
        # Update daily metrics
        self._update_daily_metrics(session_metric)
    
    def track_message(self, session_id: str, tokens_used: int = 0):
        """Track a message in a session."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["message_count"] += 1
            self.active_sessions[session_id]["tokens_used"] += tokens_used
    
    def track_audio(self, session_id: str, duration_seconds: float):
        """Track audio usage in a session."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["audio_minutes"] += duration_seconds / 60
    
    def track_feature_usage(self, session_id: str, feature: str):
        """Track feature usage in a session."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["features_used"].add(feature)
    
    def track_endpoint_call(self, session_id: str, endpoint: str):
        """Track API endpoint usage."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["endpoint_calls"][endpoint] += 1
    
    def track_error(self, session_id: str, error: str):
        """Track an error in a session."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["errors"].append({
                "error": error,
                "timestamp": datetime.now().isoformat()
            })
    
    def _save_session_data(self, session: SessionMetric):
        """Save session data to file."""
        try:
            sessions_dir = os.path.join(self.storage_path, "sessions")
            filename = f"{session.session_id}.json"
            filepath = os.path.join(sessions_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(asdict(session), f, indent=2)
                
        except Exception as e:
            print(f"Error saving session data: {e}")
    
    def _update_daily_metrics(self, session: SessionMetric):
        """Update daily aggregated metrics."""
        try:
            date_str = session.start_time[:10]  # Extract date part
            
            if date_str not in self.daily_metrics:
                self.daily_metrics[date_str] = UsageMetric(
                    date=date_str,
                    total_sessions=0,
                    total_users=0,
                    total_messages=0,
                    total_audio_minutes=0.0,
                    total_tokens=0,
                    avg_session_duration=0.0,
                    top_features=[],
                    error_rate=0.0,
                    endpoint_usage={}
                )
            
            metric = self.daily_metrics[date_str]
            
            # Update metrics
            metric.total_sessions += 1
            metric.total_messages += session.message_count
            metric.total_audio_minutes += session.audio_minutes
            metric.total_tokens += session.tokens_used
            
            # Recalculate aggregated values for the day
            self._recalculate_daily_metrics(date_str)
            
            # Save daily metrics
            self._save_daily_metrics(metric)
            
        except Exception as e:
            print(f"Error updating daily metrics: {e}")
    
    def _recalculate_daily_metrics(self, date_str: str):
        """Recalculate aggregated metrics for a specific date."""
        # Get all sessions for this date
        date_sessions = [
            session for session in self.sessions.values()
            if session.start_time.startswith(date_str)
        ]
        
        if not date_sessions:
            return
        
        metric = self.daily_metrics[date_str]
        
        # Calculate unique users
        unique_users = set(session.user_id for session in date_sessions)
        metric.total_users = len(unique_users)
        
        # Calculate average session duration
        total_duration = sum(session.duration_seconds for session in date_sessions)
        metric.avg_session_duration = total_duration / len(date_sessions)
        
        # Calculate top features
        feature_counter = Counter()
        for session in date_sessions:
            feature_counter.update(session.features_used)
        metric.top_features = [feature for feature, count in feature_counter.most_common(5)]
        
        # Calculate error rate
        total_errors = sum(len(session.errors) for session in date_sessions)
        total_requests = sum(sum(session.endpoint_calls.values()) for session in date_sessions)
        metric.error_rate = (total_errors / max(total_requests, 1)) * 100
        
        # Aggregate endpoint usage
        endpoint_usage = defaultdict(int)
        for session in date_sessions:
            for endpoint, count in session.endpoint_calls.items():
                endpoint_usage[endpoint] += count
        metric.endpoint_usage = dict(endpoint_usage)
    
    def _save_daily_metrics(self, metric: UsageMetric):
        """Save daily metrics to file."""
        try:
            daily_dir = os.path.join(self.storage_path, "daily")
            filename = f"{metric.date}.json"
            filepath = os.path.join(daily_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(asdict(metric), f, indent=2)
                
        except Exception as e:
            print(f"Error saving daily metrics: {e}")
    
    def get_dashboard_data(self, days: int = 30) -> Dict[str, Any]:
        """Get dashboard analytics data."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get metrics for the date range
            relevant_metrics = []
            current_date = start_date
            
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                if date_str in self.daily_metrics:
                    relevant_metrics.append(self.daily_metrics[date_str])
                current_date += timedelta(days=1)
            
            if not relevant_metrics:
                return self._get_empty_dashboard()
            
            # Calculate summary statistics
            total_sessions = sum(m.total_sessions for m in relevant_metrics)
            total_users = len(set(
                session.user_id for session in self.sessions.values()
                if session.start_time >= start_date.isoformat()
            ))
            total_messages = sum(m.total_messages for m in relevant_metrics)
            total_audio_minutes = sum(m.total_audio_minutes for m in relevant_metrics)
            total_tokens = sum(m.total_tokens for m in relevant_metrics)
            
            # Calculate trends
            if len(relevant_metrics) >= 2:
                recent_avg = sum(m.total_sessions for m in relevant_metrics[-7:]) / min(7, len(relevant_metrics))
                older_avg = sum(m.total_sessions for m in relevant_metrics[:-7]) / max(1, len(relevant_metrics) - 7)
                session_trend = ((recent_avg - older_avg) / max(older_avg, 1)) * 100
            else:
                session_trend = 0.0
            
            # Top features and endpoints
            all_features = []
            all_endpoints = defaultdict(int)
            
            for metric in relevant_metrics:
                all_features.extend(metric.top_features)
                for endpoint, count in metric.endpoint_usage.items():
                    all_endpoints[endpoint] += count
            
            feature_counter = Counter(all_features)
            top_features = [{"name": f, "count": c} for f, c in feature_counter.most_common(10)]
            top_endpoints = [{"name": e, "calls": c} for e, c in 
                           sorted(all_endpoints.items(), key=lambda x: x[1], reverse=True)[:10]]
            
            # Calculate average error rate
            avg_error_rate = sum(m.error_rate for m in relevant_metrics) / len(relevant_metrics)
            
            return {
                "summary": {
                    "total_sessions": total_sessions,
                    "total_users": total_users,
                    "total_messages": total_messages,
                    "total_audio_minutes": round(total_audio_minutes, 2),
                    "total_tokens": total_tokens,
                    "avg_session_duration": round(
                        sum(m.avg_session_duration for m in relevant_metrics) / len(relevant_metrics), 2
                    ),
                    "session_trend_percent": round(session_trend, 2),
                    "error_rate": round(avg_error_rate, 2)
                },
                "daily_stats": [
                    {
                        "date": m.date,
                        "sessions": m.total_sessions,
                        "users": m.total_users,
                        "messages": m.total_messages,
                        "audio_minutes": round(m.total_audio_minutes, 2),
                        "avg_duration": round(m.avg_session_duration, 2)
                    }
                    for m in relevant_metrics[-30:]  # Last 30 days
                ],
                "top_features": top_features,
                "top_endpoints": top_endpoints,
                "active_sessions": len(self.active_sessions),
                "date_range": {
                    "start": start_date.strftime('%Y-%m-%d'),
                    "end": end_date.strftime('%Y-%m-%d'),
                    "days": days
                }
            }
            
        except Exception as e:
            print(f"Error generating dashboard data: {e}")
            return self._get_empty_dashboard()
    
    def _get_empty_dashboard(self) -> Dict[str, Any]:
        """Return empty dashboard structure."""
        return {
            "summary": {
                "total_sessions": 0,
                "total_users": 0,
                "total_messages": 0,
                "total_audio_minutes": 0.0,
                "total_tokens": 0,
                "avg_session_duration": 0.0,
                "session_trend_percent": 0.0,
                "error_rate": 0.0
            },
            "daily_stats": [],
            "top_features": [],
            "top_endpoints": [],
            "active_sessions": 0,
            "date_range": {
                "start": datetime.now().strftime('%Y-%m-%d'),
                "end": datetime.now().strftime('%Y-%m-%d'),
                "days": 0
            }
        }
    
    def get_session_details(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific session."""
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "duration_seconds": session.duration_seconds,
            "message_count": session.message_count,
            "audio_minutes": round(session.audio_minutes, 2),
            "tokens_used": session.tokens_used,
            "language": session.language,
            "features_used": session.features_used,
            "endpoint_calls": session.endpoint_calls,
            "errors": session.errors
        }
    
    def get_user_analytics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get analytics for a specific user."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get user sessions in date range
        user_sessions = [
            session for session in self.sessions.values()
            if session.user_id == user_id and 
            datetime.fromisoformat(session.start_time) >= start_date
        ]
        
        if not user_sessions:
            return {"user_id": user_id, "sessions": [], "summary": {}}
        
        # Calculate user summary
        total_sessions = len(user_sessions)
        total_messages = sum(s.message_count for s in user_sessions)
        total_audio = sum(s.audio_minutes for s in user_sessions)
        total_tokens = sum(s.tokens_used for s in user_sessions)
        avg_duration = sum(s.duration_seconds for s in user_sessions) / total_sessions
        
        # Feature usage
        all_features = []
        for session in user_sessions:
            all_features.extend(session.features_used)
        feature_usage = dict(Counter(all_features))
        
        return {
            "user_id": user_id,
            "date_range": {
                "start": start_date.strftime('%Y-%m-%d'),
                "end": end_date.strftime('%Y-%m-%d')
            },
            "summary": {
                "total_sessions": total_sessions,
                "total_messages": total_messages,
                "total_audio_minutes": round(total_audio, 2),
                "total_tokens": total_tokens,
                "avg_session_duration": round(avg_duration, 2),
                "feature_usage": feature_usage
            },
            "sessions": [
                {
                    "session_id": s.session_id,
                    "start_time": s.start_time,
                    "duration_seconds": s.duration_seconds,
                    "message_count": s.message_count,
                    "features_used": s.features_used
                }
                for s in sorted(user_sessions, key=lambda x: x.start_time, reverse=True)[:50]
            ]
        }

# Global analytics service instance
analytics_service = AnalyticsService()
