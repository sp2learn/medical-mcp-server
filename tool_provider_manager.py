"""
Tool Provider Management System
Handles external medical tool providers, APIs, and integrations
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, HttpUrl
import hashlib
import secrets

class APICredentials(BaseModel):
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    custom_headers: Optional[Dict[str, str]] = None

class InputSchema(BaseModel):
    type: str = "object"
    properties: Dict[str, Any] = {}
    required: List[str] = []
    examples: List[Dict[str, Any]] = []

class OutputSchema(BaseModel):
    type: str = "object"
    properties: Dict[str, Any] = {}
    examples: List[Dict[str, Any]] = []

class ToolProvider(BaseModel):
    # Basic Information
    id: str
    name: str
    description: str
    version: str = "1.0.0"
    provider_company: str
    contact_email: str
    
    # Technical Details
    server_url: HttpUrl
    endpoint_path: str
    http_method: str = "POST"
    content_type: str = "application/json"
    
    # Schemas
    input_schema: InputSchema
    output_schema: OutputSchema
    
    # Use Cases & Categories
    use_cases: List[str] = []
    medical_categories: List[str] = []  # e.g., ["cardiology", "radiology", "pathology"]
    
    # Security & Authentication
    auth_type: str = "api_key"  # api_key, oauth2, basic_auth, bearer_token
    credentials: APICredentials
    
    # Operational Details
    rate_limit: int = 100  # requests per minute
    timeout_seconds: int = 30
    retry_attempts: int = 3
    
    # Monitoring
    enabled: bool = True
    last_tested: Optional[datetime] = None
    total_invocations: int = 0
    success_rate: float = 100.0
    avg_response_time: float = 0.0
    
    # Metadata
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    created_by: str = "admin"

class ToolProviderManager:
    def __init__(self, data_file: str = "config/tool_providers.json"):
        self.data_file = data_file
        self.providers: Dict[str, ToolProvider] = {}
        # Ensure config directory exists
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        self._load_providers()
    
    def _load_providers(self):
        """Load tool providers from JSON file."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    for provider_id, provider_data in data.items():
                        # Convert datetime strings back to datetime objects
                        if 'created_at' in provider_data:
                            provider_data['created_at'] = datetime.fromisoformat(provider_data['created_at'])
                        if 'updated_at' in provider_data:
                            provider_data['updated_at'] = datetime.fromisoformat(provider_data['updated_at'])
                        if 'last_tested' in provider_data and provider_data['last_tested']:
                            provider_data['last_tested'] = datetime.fromisoformat(provider_data['last_tested'])
                        
                        self.providers[provider_id] = ToolProvider(**provider_data)
        except Exception as e:
            print(f"Error loading tool providers: {e}")
            self.providers = {}
    
    def _save_providers(self):
        """Save tool providers to JSON file."""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            # Convert to serializable format
            data = {}
            for provider_id, provider in self.providers.items():
                provider_dict = provider.dict()
                # Convert datetime objects to strings
                if provider_dict['created_at']:
                    provider_dict['created_at'] = provider_dict['created_at'].isoformat()
                if provider_dict['updated_at']:
                    provider_dict['updated_at'] = provider_dict['updated_at'].isoformat()
                if provider_dict['last_tested']:
                    provider_dict['last_tested'] = provider_dict['last_tested'].isoformat()
                
                data[provider_id] = provider_dict
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving tool providers: {e}")
    
    def add_provider(self, provider: ToolProvider) -> bool:
        """Add a new tool provider."""
        try:
            if provider.id in self.providers:
                return False  # Provider already exists
            
            provider.created_at = datetime.now()
            provider.updated_at = datetime.now()
            self.providers[provider.id] = provider
            self._save_providers()
            return True
        except Exception as e:
            print(f"Error adding provider: {e}")
            return False
    
    def update_provider(self, provider_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing tool provider."""
        try:
            if provider_id not in self.providers:
                return False
            
            provider = self.providers[provider_id]
            for key, value in updates.items():
                if hasattr(provider, key):
                    setattr(provider, key, value)
            
            provider.updated_at = datetime.now()
            self._save_providers()
            return True
        except Exception as e:
            print(f"Error updating provider: {e}")
            return False
    
    def delete_provider(self, provider_id: str) -> bool:
        """Delete a tool provider."""
        try:
            if provider_id in self.providers:
                del self.providers[provider_id]
                self._save_providers()
                return True
            return False
        except Exception as e:
            print(f"Error deleting provider: {e}")
            return False
    
    def get_provider(self, provider_id: str) -> Optional[ToolProvider]:
        """Get a specific tool provider."""
        return self.providers.get(provider_id)
    
    def list_providers(self, enabled_only: bool = False) -> List[ToolProvider]:
        """List all tool providers."""
        providers = list(self.providers.values())
        if enabled_only:
            providers = [p for p in providers if p.enabled]
        return sorted(providers, key=lambda x: x.name)
    
    def test_provider(self, provider_id: str) -> Dict[str, Any]:
        """Test a tool provider connection."""
        provider = self.get_provider(provider_id)
        if not provider:
            return {"success": False, "error": "Provider not found"}
        
        try:
            import requests
            import time
            
            start_time = time.time()
            
            # Prepare test request
            headers = {"Content-Type": provider.content_type}
            if provider.credentials.custom_headers:
                headers.update(provider.credentials.custom_headers)
            
            # Add authentication
            auth = None
            if provider.auth_type == "api_key" and provider.credentials.api_key:
                headers["Authorization"] = f"Bearer {provider.credentials.api_key}"
            elif provider.auth_type == "basic_auth":
                auth = (provider.credentials.username, provider.credentials.password)
            
            # Simple test payload
            test_data = {"test": True, "timestamp": datetime.now().isoformat()}
            
            # Make request
            url = f"{provider.server_url}{provider.endpoint_path}"
            response = requests.request(
                method=provider.http_method,
                url=url,
                json=test_data,
                headers=headers,
                auth=auth,
                timeout=provider.timeout_seconds
            )
            
            response_time = time.time() - start_time
            
            # Update provider stats
            provider.last_tested = datetime.now()
            provider.total_invocations += 1
            
            if response.status_code == 200:
                provider.avg_response_time = (provider.avg_response_time + response_time) / 2
                self._save_providers()
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "response_data": response.json() if response.content else None
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text,
                    "response_time": response_time
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """Get overall provider statistics."""
        total_providers = len(self.providers)
        enabled_providers = len([p for p in self.providers.values() if p.enabled])
        
        categories = {}
        for provider in self.providers.values():
            for category in provider.medical_categories:
                categories[category] = categories.get(category, 0) + 1
        
        return {
            "total_providers": total_providers,
            "enabled_providers": enabled_providers,
            "disabled_providers": total_providers - enabled_providers,
            "medical_categories": categories,
            "total_invocations": sum(p.total_invocations for p in self.providers.values()),
            "avg_success_rate": sum(p.success_rate for p in self.providers.values()) / total_providers if total_providers > 0 else 0
        }
    
    def generate_api_key(self) -> str:
        """Generate a secure API key."""
        return secrets.token_urlsafe(32)
    
    def encrypt_credentials(self, credentials: str) -> str:
        """Encrypt sensitive credentials (basic implementation)."""
        # In production, use proper encryption like Fernet
        return hashlib.sha256(credentials.encode()).hexdigest()

# Global instance
tool_provider_manager = ToolProviderManager()