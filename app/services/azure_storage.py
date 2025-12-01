from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, ContentSettings
from azure.core.exceptions import AzureError
import json
from typing import Dict, List, Optional
import asyncio
from functools import partial
from app.core.config import Config

class AzureStorageService:
    """Service for interacting with Azure Blob Storage"""
    
    def __init__(self):
        self.connection_string = Config.get_azure_storage_connection_string()
        self.container_name = Config.get_azure_storage_container()
        self._blob_service_client = None
        self._is_configured = bool(self.connection_string)
        
        if self._is_configured:
            self._blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
            self._ensure_container_exists()
    
    @property
    def blob_service_client(self):
        """Lazy-load blob service client"""
        if not self._is_configured:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING environment variable is required")
        if self._blob_service_client is None:
            self._blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
        return self._blob_service_client
    
    def _ensure_container_exists(self):
        """Ensure the container exists, create if it doesn't"""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            if not container_client.exists():
                container_client.create_container()
        except AzureError as e:
            print(f"Error ensuring container exists: {e}")
    
    async def get_content(self, page: str) -> Dict:
        """Get content for a specific page"""
        if not self._is_configured:
            # Return default content for local development
            return {"title": page.title(), "content": ""}
        
        blob_name = f"content/{page}.json"
        
        loop = asyncio.get_event_loop()
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Run blocking operation in thread pool
            content = await loop.run_in_executor(
                None,
                lambda: blob_client.download_blob().readall()
            )
            
            return json.loads(content.decode('utf-8'))
        except AzureError as e:
            if "BlobNotFound" in str(e):
                # Return default content if not found
                return {"title": page.title(), "content": ""}
            raise
    
    async def save_content(self, page: str, content: Dict):
        """Save content for a specific page"""
        # Recheck configuration in case it was loaded after service creation
        if not self._is_configured:
            # Try to reload connection string
            self.connection_string = Config.get_azure_storage_connection_string()
            self._is_configured = bool(self.connection_string)
            if self._is_configured:
                self._blob_service_client = BlobServiceClient.from_connection_string(
                    self.connection_string
                )
                self._ensure_container_exists()
        
        if not self._is_configured:
            raise Exception("Azure Storage is not configured. Please set AZURE_STORAGE_CONNECTION_STRING or ensure Pulumi outputs are available with storage_account_name and resource_group_name")
        
        blob_name = f"content/{page}.json"
        
        loop = asyncio.get_event_loop()
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            content_json = json.dumps(content, indent=2)
            
            content_settings = ContentSettings(content_type="application/json")
            await loop.run_in_executor(
                None,
                lambda: blob_client.upload_blob(
                    content_json,
                    overwrite=True,
                    content_settings=content_settings
                )
            )
        except AzureError as e:
            raise Exception(f"Failed to save content: {str(e)}")
    
    async def upload_image(self, filename: str, file_content: bytes, content_type: str) -> str:
        """Upload an image to blob storage"""
        # Recheck configuration in case it was loaded after service creation
        if not self._is_configured:
            self.connection_string = Config.get_azure_storage_connection_string()
            self._is_configured = bool(self.connection_string)
            if self._is_configured:
                self._blob_service_client = BlobServiceClient.from_connection_string(
                    self.connection_string
                )
        
        if not self._is_configured:
            raise Exception("Azure Storage is not configured. Please set AZURE_STORAGE_CONNECTION_STRING or ensure Pulumi outputs are available")
        
        blob_name = f"images/{filename}"
        
        loop = asyncio.get_event_loop()
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            content_settings = ContentSettings(content_type=content_type)
            await loop.run_in_executor(
                None,
                lambda: blob_client.upload_blob(
                    file_content,
                    overwrite=True,
                    content_settings=content_settings
                )
            )
            
            # Return the URL of the uploaded blob
            return blob_client.url
        except AzureError as e:
            raise Exception(f"Failed to upload image: {str(e)}")
    
    async def list_images(self) -> List[Dict]:
        """List all images in blob storage"""
        if not self._is_configured:
            # Return empty list for local development
            return []
        
        prefix = "images/"
        
        loop = asyncio.get_event_loop()
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            
            # Run blocking operation in thread pool
            blobs = await loop.run_in_executor(
                None,
                lambda: list(container_client.list_blobs(name_starts_with=prefix))
            )
            
            images = []
            for blob in blobs:
                blob_client = self.blob_service_client.get_blob_client(
                    container=self.container_name,
                    blob=blob.name
                )
                images.append({
                    "name": blob.name.replace(prefix, ""),
                    "url": blob_client.url,
                    "size": blob.size,
                    "last_modified": blob.last_modified.isoformat() if blob.last_modified else None
                })
            
            return images
        except AzureError as e:
            raise Exception(f"Failed to list images: {str(e)}")
    
    async def delete_image(self, image_name: str):
        """Delete an image from blob storage"""
        # Recheck configuration in case it was loaded after service creation
        if not self._is_configured:
            self.connection_string = Config.get_azure_storage_connection_string()
            self._is_configured = bool(self.connection_string)
            if self._is_configured:
                self._blob_service_client = BlobServiceClient.from_connection_string(
                    self.connection_string
                )
        
        if not self._is_configured:
            raise Exception("Azure Storage is not configured. Please set AZURE_STORAGE_CONNECTION_STRING or ensure Pulumi outputs are available")
        
        blob_name = f"images/{image_name}"
        
        loop = asyncio.get_event_loop()
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            await loop.run_in_executor(
                None,
                lambda: blob_client.delete_blob()
            )
        except AzureError as e:
            raise Exception(f"Failed to delete image: {str(e)}")
    
    def get_image_url(self, image_name: str) -> str:
        """Get the URL for an image"""
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=f"images/{image_name}"
        )
        return blob_client.url

