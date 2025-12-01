"""
Configuration service that reads from Pulumi stack outputs
Falls back to environment variables for local development
"""
import os
import json
import subprocess
from typing import Optional, Dict
from functools import lru_cache
from pathlib import Path

class Config:
    """Configuration manager that reads from Pulumi or environment variables"""
    
    _pulumi_outputs: Optional[Dict] = None
    _pulumi_loaded: bool = False
    
    @classmethod
    def _load_pulumi_outputs(cls) -> Optional[Dict]:
        """Load Pulumi stack outputs"""
        if cls._pulumi_loaded:
            return cls._pulumi_outputs
        
        cls._pulumi_loaded = True
        
        try:
            # Try to get Pulumi outputs
            pulumi_dir = Path(__file__).resolve().parent.parent.parent / "pulumi"
            if not pulumi_dir.exists():
                return None
            
            result = subprocess.run(
                ["pulumi", "stack", "output", "--json"],
                cwd=str(pulumi_dir),
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                cls._pulumi_outputs = json.loads(result.stdout)
                return cls._pulumi_outputs
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
            # Pulumi not available or not configured
            pass
        
        return None
    
    @classmethod
    def get(cls, key: str, default: str = "") -> str:
        """Get configuration value from Pulumi or environment variable"""
        # First try Pulumi outputs (keys are lowercase with underscores)
        pulumi_outputs = cls._load_pulumi_outputs()
        if pulumi_outputs:
            # Try exact key match first
            if key in pulumi_outputs:
                value = pulumi_outputs[key]
                return str(value) if value is not None else default
            # Try lowercase version
            key_lower = key.lower()
            if key_lower in pulumi_outputs:
                value = pulumi_outputs[key_lower]
                return str(value) if value is not None else default
        
        # Fall back to environment variable
        return os.getenv(key, default)
    
    @classmethod
    def get_auth0_domain(cls) -> str:
        """Get Auth0 domain (without protocol)"""
        # Try Pulumi output key first (lowercase), then env var
        pulumi_outputs = cls._load_pulumi_outputs()
        domain = ""
        if pulumi_outputs and "auth0_domain" in pulumi_outputs:
            domain = str(pulumi_outputs["auth0_domain"]) if pulumi_outputs["auth0_domain"] else ""
        else:
            domain = os.getenv("AUTH0_DOMAIN", "")
        
        # Strip https:// or http:// if present
        if domain:
            domain = domain.replace("https://", "").replace("http://", "").strip("/")
        
        return domain
    
    @classmethod
    def get_auth0_client_id(cls) -> str:
        """Get Auth0 client ID"""
        pulumi_outputs = cls._load_pulumi_outputs()
        if pulumi_outputs and "auth0_client_id" in pulumi_outputs:
            return str(pulumi_outputs["auth0_client_id"]) if pulumi_outputs["auth0_client_id"] else ""
        return os.getenv("AUTH0_CLIENT_ID", "")
    
    @classmethod
    def get_auth0_client_secret(cls) -> str:
        """Get Auth0 client secret"""
        pulumi_outputs = cls._load_pulumi_outputs()
        if pulumi_outputs and "auth0_client_secret" in pulumi_outputs:
            return str(pulumi_outputs["auth0_client_secret"]) if pulumi_outputs["auth0_client_secret"] else ""
        return os.getenv("AUTH0_CLIENT_SECRET", "")
    
    @classmethod
    def get_auth0_audience(cls) -> str:
        """Get Auth0 audience"""
        pulumi_outputs = cls._load_pulumi_outputs()
        if pulumi_outputs and "auth0_audience" in pulumi_outputs:
            return str(pulumi_outputs["auth0_audience"]) if pulumi_outputs["auth0_audience"] else ""
        return os.getenv("AUTH0_AUDIENCE", "")
    
    @classmethod
    def get_auth0_callback_url(cls) -> str:
        """Get Auth0 callback URL"""
        pulumi_outputs = cls._load_pulumi_outputs()
        if pulumi_outputs and "auth0_callback_url" in pulumi_outputs:
            return str(pulumi_outputs["auth0_callback_url"]) if pulumi_outputs["auth0_callback_url"] else ""
        return os.getenv("AUTH0_CALLBACK_URL", "http://localhost:8003/auth/callback")
    
    _storage_connection_string_cache: Optional[str] = None
    
    @classmethod
    def get_azure_storage_connection_string(cls) -> str:
        """Get Azure Storage connection string from Pulumi outputs or environment"""
        # First try environment variable (for deployed environments)
        conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
        if conn_str:
            return conn_str
        
        # Use cached value if available
        if cls._storage_connection_string_cache is not None:
            return cls._storage_connection_string_cache
        
        # Try to get from Pulumi outputs and fetch from Azure
        pulumi_outputs = cls._load_pulumi_outputs()
        if pulumi_outputs and "resource_group_name" in pulumi_outputs and "storage_account_name" in pulumi_outputs:
            try:
                result = subprocess.run(
                    [
                        "az", "storage", "account", "show-connection-string",
                        "--resource-group", str(pulumi_outputs["resource_group_name"]),
                        "--name", str(pulumi_outputs["storage_account_name"]),
                        "--query", "connectionString",
                        "--output", "tsv"
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    conn_str = result.stdout.strip()
                    cls._storage_connection_string_cache = conn_str
                    return conn_str
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
                # Azure CLI not available or not logged in
                print(f"Warning: Could not fetch Azure Storage connection string from Azure: {e}")
        
        return ""
    
    @classmethod
    def get_azure_storage_container(cls) -> str:
        """Get Azure Storage container name"""
        return os.getenv("AZURE_STORAGE_CONTAINER", "website-content")
    
    @classmethod
    def is_auth0_configured(cls) -> bool:
        """Check if Auth0 is configured"""
        return bool(cls.get_auth0_domain() and cls.get_auth0_audience())

