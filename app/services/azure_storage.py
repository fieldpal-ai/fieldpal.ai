from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, ContentSettings
from azure.data.tables import TableServiceClient, TableClient
from azure.core.exceptions import AzureError, ResourceExistsError
import json
from typing import Dict, List, Optional
import asyncio
from functools import partial
from datetime import datetime
from app.core.config import Config
import uuid

class AzureStorageService:
    """Service for interacting with Azure Blob Storage"""
    
    def __init__(self):
        self.connection_string = Config.get_azure_storage_connection_string()
        self.container_name = Config.get_azure_storage_container()
        self.table_name = "contacts"
        self._blob_service_client = None
        self._table_service_client = None
        self._is_configured = bool(self.connection_string)
        
        if self._is_configured:
            self._blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
            self._table_service_client = TableServiceClient.from_connection_string(
                self.connection_string
            )
            self._ensure_container_exists()
            self._ensure_table_exists()
    
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
    
    @property
    def table_service_client(self):
        """Lazy-load table service client"""
        if not self._is_configured:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING environment variable is required")
        if self._table_service_client is None:
            self._table_service_client = TableServiceClient.from_connection_string(
                self.connection_string
            )
        return self._table_service_client
    
    def _ensure_table_exists(self):
        """Ensure the contacts table exists, create if it doesn't"""
        if not self._is_configured:
            return
        try:
            table_client = self.table_service_client.get_table_client(self.table_name)
            try:
                # Try to create the table - will raise ResourceExistsError if it already exists
                table_client.create_table()
            except ResourceExistsError:
                # Table already exists, which is fine
                pass
        except AzureError as e:
            # Log other errors but don't fail initialization
            print(f"Error ensuring table exists: {e}")
    
    async def get_content(self, page: str, section: str = None) -> Dict:
        """Get content for a specific page, optionally filtered by section"""
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
            
            data = json.loads(content.decode('utf-8'))
            
            # If section is specified, return only that section
            if section and section in data:
                return {"content": data[section]}
            
            return data
        except AzureError as e:
            if "BlobNotFound" in str(e):
                # Return default content if not found
                if section:
                    return {"content": {}}
                return {"title": page.title(), "content": ""}
            raise
    
    async def save_content(self, page: str, content: Dict, section: str = None):
        """Save content for a specific page, optionally updating only a section"""
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
            
            # If updating a section, merge with existing content
            if section:
                try:
                    existing_content = await loop.run_in_executor(
                        None,
                        lambda: blob_client.download_blob().readall()
                    )
                    full_content = json.loads(existing_content.decode('utf-8'))
                except AzureError:
                    # File doesn't exist, create new
                    full_content = {}
                
                # Update the specific section
                full_content[section] = content
                content_json = json.dumps(full_content, indent=2)
            else:
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
    
    async def save_contact_submission(self, name: str, email: str, message: str, subject: Optional[str] = None) -> str:
        """Save a contact form submission to Azure Table Storage"""
        # Recheck configuration in case it was loaded after service creation
        if not self._is_configured:
            self.connection_string = Config.get_azure_storage_connection_string()
            self._is_configured = bool(self.connection_string)
            if self._is_configured:
                self._table_service_client = TableServiceClient.from_connection_string(
                    self.connection_string
                )
                self._ensure_table_exists()
        
        if not self._is_configured:
            raise Exception("Azure Storage is not configured. Please set AZURE_STORAGE_CONNECTION_STRING or ensure Pulumi outputs are available")
        
        # Generate unique row key
        row_key = str(uuid.uuid4())
        partition_key = datetime.utcnow().strftime("%Y-%m")
        
        # Create entity
        entity = {
            "PartitionKey": partition_key,
            "RowKey": row_key,
            "Name": name,
            "Email": email,
            "Message": message,
            "Subject": subject or "",
            "SubmittedAt": datetime.utcnow().isoformat(),
        }
        
        loop = asyncio.get_event_loop()
        try:
            table_client = self.table_service_client.get_table_client(self.table_name)
            
            # Run blocking operation in thread pool
            await loop.run_in_executor(
                None,
                lambda: table_client.create_entity(entity=entity)
            )
            
            return row_key
        except AzureError as e:
            raise Exception(f"Failed to save contact submission: {str(e)}")
    
    async def get_contact_submissions(self, limit: int = 100) -> List[Dict]:
        """Get contact form submissions from Azure Table Storage"""
        if not self._is_configured:
            return []
        
        loop = asyncio.get_event_loop()
        try:
            table_client = self.table_service_client.get_table_client(self.table_name)
            
            # Run blocking operation in thread pool
            entities = await loop.run_in_executor(
                None,
                lambda: list(table_client.list_entities())
            )
            
            # Convert to list of dicts and sort by SubmittedAt descending
            submissions = []
            for entity in entities[:limit]:
                submissions.append({
                    "partition_key": entity.get("PartitionKey"),
                    "row_key": entity.get("RowKey"),
                    "name": entity.get("Name", ""),
                    "email": entity.get("Email", ""),
                    "message": entity.get("Message", ""),
                    "subject": entity.get("Subject", ""),
                    "submitted_at": entity.get("SubmittedAt", ""),
                })
            
            # Sort by submitted_at descending
            submissions.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)
            
            return submissions
        except AzureError as e:
            raise Exception(f"Failed to get contact submissions: {str(e)}")

