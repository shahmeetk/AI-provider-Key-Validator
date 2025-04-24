"""
Anthropic API key validator for LLM API Key Validator.
"""

import aiohttp
import json
from typing import Optional, Dict, Any, List

from core.validator import Validator
from core.api_key import APIKey, AnthropicKey
from utils.logger import app_logger


class AnthropicValidator(Validator):
    """Validator for Anthropic API keys."""
    
    async def validate(self, api_key: APIKey) -> Optional[APIKey]:
        """
        Validate an Anthropic API key and retrieve quota information.
        
        Args:
            api_key: The Anthropic API key to validate
            
        Returns:
            The updated API key with validation results, or None if validation failed
        """
        if not isinstance(api_key, AnthropicKey):
            api_key = AnthropicKey(api_key.api_key)
        
        # Updated to use the latest Anthropic API version
        url = "https://api.anthropic.com/v1/models"
        headers = {
            "x-api-key": api_key.api_key,
            "anthropic-version": "2023-06-01",  # This is still the stable version
            "Accept": "application/json"
        }
        
        try:
            app_logger.info(f"Validating Anthropic API key using URL: {url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    api_key.raw_response = await response.text()
                    
                    if response.status != 200:
                        api_key.is_valid = False
                        if response.status == 401:
                            api_key.message = "Invalid Anthropic API key."
                            app_logger.warning(f"Invalid Anthropic API key: {response.status}")
                        else:
                            api_key.message = f"Unexpected response from Anthropic API: {response.status}"
                            app_logger.warning(f"Unexpected response from Anthropic API: {response.status} - {api_key.raw_response[:200]}")
                        return None
                    
                    # Key is valid
                    api_key.is_valid = True
                    api_key.message = "Anthropic API key is valid."
                    
                    # Always add basic account summary information for Anthropic
                    api_key.quota_info["account_summary"] = {
                        "plan": "Pay-as-you-go",
                        "status": "Active",
                        "credit_card": "Required for full access"
                    }
                    
                    # Try to parse models information
                    try:
                        data = await response.json()
                        if "models" in data:
                            models = data["models"]
                            api_key.quota_info["available_models"] = [model.get("name") for model in models]
                            api_key.quota_info["model_count"] = len(models)
                            api_key.quota_info["account_summary"]["available_models"] = f"{len(models)} models available"
                            
                            # Add featured models if available
                            featured_models = []
                            for model in models[:3]:  # Just show first 3
                                if "name" in model:
                                    featured_models.append(model["name"])
                            
                            if featured_models:
                                api_key.quota_info["account_summary"]["featured_models"] = ", ".join(featured_models)
                            
                            # Add model details with capabilities
                            model_details = []
                            for model in models:
                                model_name = model.get("name", "")
                                model_detail = {
                                    "id": model_name,
                                    "capabilities": ["Text generation", "Chat completions"]
                                }
                                
                                # Add specific model information based on name
                                if "claude-3" in model_name.lower():
                                    if "opus" in model_name.lower():
                                        model_detail["description"] = "Claude 3 Opus - Most powerful Claude model"
                                        model_detail["context_length"] = "200K tokens"
                                    elif "sonnet" in model_name.lower():
                                        model_detail["description"] = "Claude 3 Sonnet - Balanced performance and cost"
                                        model_detail["context_length"] = "200K tokens"
                                    elif "haiku" in model_name.lower():
                                        model_detail["description"] = "Claude 3 Haiku - Fastest and most cost-effective"
                                        model_detail["context_length"] = "200K tokens"
                                elif "claude-2" in model_name.lower():
                                    model_detail["description"] = "Claude 2 - Previous generation model"
                                    model_detail["context_length"] = "100K tokens"
                                
                                model_details.append(model_detail)
                            
                            api_key.quota_info["model_details"] = model_details
                    except Exception as e:
                        error_msg = f"Could not parse models information: {str(e)}"
                        app_logger.warning(error_msg)
                        api_key.quota_info["error"] = error_msg
                    
                    # Try to get rate limit information
                    try:
                        # Check for rate limit headers
                        if "x-ratelimit-limit" in response.headers:
                            rate_limit = response.headers.get("x-ratelimit-limit")
                            api_key.quota_info["account_summary"]["rate_limit"] = f"{rate_limit} requests per minute"
                        
                        # Check for remaining tokens
                        if "x-ratelimit-remaining" in response.headers:
                            remaining = response.headers.get("x-ratelimit-remaining")
                            api_key.quota_info["account_summary"]["remaining_requests"] = remaining
                    except Exception as e:
                        app_logger.warning(f"Could not get rate limit information: {str(e)}")
                    
                    # Note: Anthropic doesn't have a public API for quota information yet
                    api_key.quota_info["account_summary"]["note"] = "Detailed quota information not available through Anthropic API"
                    
                    return api_key
        
        except aiohttp.ClientError as e:
            error_msg = f"Error connecting to Anthropic API: {str(e)}"
            app_logger.error(error_msg)
            api_key.is_valid = False
            api_key.message = error_msg
            api_key.error = str(e)
            return None
    
    def format_results(self, api_key: APIKey) -> Dict[str, Any]:
        """
        Format the validation results for display.
        
        Args:
            api_key: The validated API key
            
        Returns:
            A dictionary with formatted results
        """
        if not isinstance(api_key, AnthropicKey):
            return {"error": "Not an Anthropic API key"}
        
        results = {
            "provider": "Anthropic",
            "is_valid": api_key.is_valid,
            "message": api_key.message,
            "api_key": api_key.api_key
        }
        
        if api_key.is_valid:
            results.update({
                "has_quota": api_key.has_quota,
                "tier": api_key.tier,
                "rate_limited": api_key.rate_limited,
                "model_count": api_key.quota_info.get("model_count", 0),
            })
            
            if "account_summary" in api_key.quota_info:
                results["account_summary"] = api_key.quota_info["account_summary"]
        
        return results
