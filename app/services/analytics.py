"""
PostHog analytics service
"""
from posthog import Posthog
from app.core.config import Config
from typing import Optional, Dict, Any
import os

class AnalyticsService:
    """Service for tracking analytics events with PostHog"""
    
    _instance: Optional[Posthog] = None
    _enabled: bool = False
    
    @classmethod
    def get_instance(cls) -> Optional[Posthog]:
        """Get or create PostHog instance"""
        if cls._instance is not None:
            return cls._instance
        
        # Get PostHog configuration from Pulumi or environment
        project_api_key = os.getenv("POSTHOG_PROJECT_API_KEY", "")
        host = os.getenv("POSTHOG_HOST", "https://us.i.posthog.com")
        
        # Try Pulumi outputs
        if not project_api_key:
            pulumi_outputs = Config._load_pulumi_outputs()
            if pulumi_outputs and "posthog_project_api_key" in pulumi_outputs:
                project_api_key = str(pulumi_outputs["posthog_project_api_key"])
            if pulumi_outputs and "posthog_host" in pulumi_outputs:
                host = str(pulumi_outputs["posthog_host"])
        
        if project_api_key:
            cls._instance = Posthog(
                project_api_key=project_api_key,
                host=host
            )
            cls._enabled = True
        
        return cls._instance
    
    @classmethod
    def capture(
        cls,
        distinct_id: str,
        event: str,
        properties: Optional[Dict[str, Any]] = None
    ):
        """Capture an event"""
        instance = cls.get_instance()
        if instance and cls._enabled:
            try:
                instance.capture(
                    distinct_id=distinct_id,
                    event=event,
                    properties=properties or {}
                )
            except Exception as e:
                # Don't fail the request if analytics fails
                print(f"PostHog error: {e}")
    
    @classmethod
    def identify(
        cls,
        distinct_id: str,
        properties: Optional[Dict[str, Any]] = None
    ):
        """Identify a user"""
        instance = cls.get_instance()
        if instance and cls._enabled:
            try:
                instance.identify(
                    distinct_id=distinct_id,
                    properties=properties or {}
                )
            except Exception as e:
                print(f"PostHog error: {e}")
    
    @classmethod
    def shutdown(cls):
        """Shutdown PostHog (call on app shutdown)"""
        if cls._instance:
            cls._instance.shutdown()
            cls._instance = None





