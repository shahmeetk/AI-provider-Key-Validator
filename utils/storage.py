"""
Storage utilities for LLM API Key Validator.
"""

import json
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional

from core.api_key import APIKey
from utils.logger import app_logger


class Storage:
    """Storage manager for validation history."""
    
    HISTORY_FILE = "data/history.json"
    
    @classmethod
    def save_validation_result(cls, api_key: APIKey) -> None:
        """
        Save a validation result to the history.
        
        Args:
            api_key: The validated API key
        """
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Load existing history
        history = cls.load_history()
        
        # Create a hashed reference to the key for security
        key_hash = cls._hash_key(api_key.api_key)
        
        # Create a record of the validation
        record = {
            "provider": api_key.provider.value,
            "key_hash": key_hash,
            "is_valid": api_key.is_valid,
            "timestamp": datetime.now().isoformat(),
            "message": api_key.message,
        }
        
        # Add provider-specific information
        if api_key.is_valid and api_key.quota_info:
            # Don't store the full quota info, just a summary
            if "account_summary" in api_key.quota_info:
                record["summary"] = api_key.quota_info["account_summary"]
            
            # Store model count if available
            if "model_count" in api_key.quota_info:
                record["model_count"] = api_key.quota_info["model_count"]
        
        # Add the record to the history
        history.append(record)
        
        # Save the updated history
        cls._save_history(history)
    
    @classmethod
    def load_history(cls) -> List[Dict[str, Any]]:
        """
        Load the validation history.
        
        Returns:
            A list of validation records
        """
        if not os.path.exists(cls.HISTORY_FILE):
            return []
        
        try:
            with open(cls.HISTORY_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            app_logger.error(f"Error loading history: {str(e)}")
            return []
    
    @classmethod
    def get_history_for_key(cls, api_key: str) -> List[Dict[str, Any]]:
        """
        Get the validation history for a specific key.
        
        Args:
            api_key: The API key to look up
            
        Returns:
            A list of validation records for the key
        """
        history = cls.load_history()
        key_hash = cls._hash_key(api_key)
        
        return [record for record in history if record.get("key_hash") == key_hash]
    
    @classmethod
    def clear_history(cls) -> None:
        """Clear the validation history."""
        if os.path.exists(cls.HISTORY_FILE):
            try:
                os.remove(cls.HISTORY_FILE)
                app_logger.info("Validation history cleared")
            except IOError as e:
                app_logger.error(f"Error clearing history: {str(e)}")
    
    @classmethod
    def _save_history(cls, history: List[Dict[str, Any]]) -> None:
        """
        Save the validation history.
        
        Args:
            history: The history to save
        """
        try:
            with open(cls.HISTORY_FILE, "w") as f:
                json.dump(history, f, indent=2)
        except IOError as e:
            app_logger.error(f"Error saving history: {str(e)}")
    
    @staticmethod
    def _hash_key(api_key: str) -> str:
        """
        Create a secure hash of an API key.
        
        Args:
            api_key: The API key to hash
            
        Returns:
            A hash of the API key
        """
        return hashlib.sha256(api_key.encode()).hexdigest()


class ProviderInfo:
    """Manager for provider information."""
    
    PROVIDER_INFO_FILE = "data/provider_info.json"
    
    @classmethod
    def load_provider_info(cls) -> Dict[str, Any]:
        """
        Load provider information.
        
        Returns:
            A dictionary with provider information
        """
        if not os.path.exists(cls.PROVIDER_INFO_FILE):
            return cls._create_default_provider_info()
        
        try:
            with open(cls.PROVIDER_INFO_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            app_logger.error(f"Error loading provider info: {str(e)}")
            return cls._create_default_provider_info()
    
    @classmethod
    def _create_default_provider_info(cls) -> Dict[str, Any]:
        """
        Create default provider information.
        
        Returns:
            A dictionary with default provider information
        """
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Create default provider info
        provider_info = {
            "categories": {
                "free": {
                    "name": "Free Providers",
                    "description": "Providers that offer free access without requiring a credit card",
                    "providers": ["google", "mistral"]
                },
                "premium": {
                    "name": "Premium Providers",
                    "description": "Providers that require a credit card for access",
                    "providers": ["openai", "anthropic", "groq"]
                },
                "freemium": {
                    "name": "Freemium Providers",
                    "description": "Providers that offer limited free access with paid tiers",
                    "providers": ["cohere", "perplexity", "anyscale"]
                },
                "credit": {
                    "name": "Credit-Based Providers",
                    "description": "Providers that offer free credits for new users",
                    "providers": ["together", "replicate", "openrouter"]
                }
            },
            "providers": {
                "openai": {
                    "name": "OpenAI",
                    "description": "Provider of GPT models including GPT-3.5 and GPT-4",
                    "website": "https://openai.com",
                    "signup_url": "https://platform.openai.com/signup",
                    "pricing_url": "https://openai.com/pricing",
                    "docs_url": "https://platform.openai.com/docs",
                    "free_tier": False,
                    "credit_card_required": True,
                    "key_format": "sk-...",
                    "rate_limit": "Varies by tier",
                    "token_limit": "Varies by model",
                    "featured_models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
                },
                "anthropic": {
                    "name": "Anthropic",
                    "description": "Provider of Claude models",
                    "website": "https://anthropic.com",
                    "signup_url": "https://console.anthropic.com/signup",
                    "pricing_url": "https://www.anthropic.com/pricing",
                    "docs_url": "https://docs.anthropic.com",
                    "free_tier": False,
                    "credit_card_required": True,
                    "key_format": "sk-ant-...",
                    "rate_limit": "Varies by tier",
                    "token_limit": "Varies by model",
                    "featured_models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
                },
                # Add more providers...
            }
        }
        
        # Save the default provider info
        try:
            with open(cls.PROVIDER_INFO_FILE, "w") as f:
                json.dump(provider_info, f, indent=2)
        except IOError as e:
            app_logger.error(f"Error saving default provider info: {str(e)}")
        
        return provider_info
