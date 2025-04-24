"""
Cohere API key validator for LLM API Key Validator.
"""

import aiohttp
import json
from typing import Optional, Dict, Any, List

from core.validator import Validator
from core.api_key import APIKey, CohereKey
from utils.logger import app_logger


class CohereValidator(Validator):
    """Validator for Cohere API keys."""
    
    async def validate(self, api_key: APIKey) -> Optional[APIKey]:
        """
        Validate a Cohere API key and retrieve quota information.
        
        Args:
            api_key: The Cohere API key to validate
            
        Returns:
            The updated API key with validation results, or None if validation failed
        """
        if not isinstance(api_key, CohereKey):
            api_key = CohereKey(api_key.api_key)
        
        url = "https://api.cohere.ai/v1/models"
        headers = {
            "Authorization": f"Bearer {api_key.api_key}",
            "Accept": "application/json"
        }
        
        try:
            app_logger.info(f"Validating Cohere API key using URL: {url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    api_key.raw_response = await response.text()
                    
                    if response.status != 200:
                        api_key.is_valid = False
                        if response.status == 401:
                            api_key.message = "Invalid Cohere API key."
                            app_logger.warning(f"Invalid Cohere API key: {response.status}")
                        else:
                            api_key.message = f"Unexpected response from Cohere API: {response.status}"
                            app_logger.warning(f"Unexpected response from Cohere API: {response.status} - {api_key.raw_response[:200]}")
                        return None
                    
                    # Key is valid
                    api_key.is_valid = True
                    api_key.message = "Cohere API key is valid."
                    
                    # Always add basic account summary information for Cohere
                    api_key.quota_info["account_summary"] = {
                        "plan": "Free Developer Tier",
                        "status": "Active",
                        "credit_card": "Not required for free tier"
                    }
                    
                    # Parse models information
                    try:
                        data = await response.json()
                        if isinstance(data, list):
                            models = data
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
                                    "capabilities": []
                                }
                                
                                # Add capabilities based on model type
                                if "command" in model_name.lower():
                                    model_detail["capabilities"] = ["Text generation", "Chat completions"]
                                    if "light" in model_name.lower():
                                        model_detail["description"] = "Command Light - Fastest and most cost-effective"
                                    elif "r-plus" in model_name.lower():
                                        model_detail["description"] = "Command R+ - Most powerful Command model"
                                    elif "r" in model_name.lower():
                                        model_detail["description"] = "Command R - Balanced performance and cost"
                                    else:
                                        model_detail["description"] = "Command - General purpose model"
                                elif "embed" in model_name.lower():
                                    model_detail["capabilities"] = ["Embeddings"]
                                    model_detail["description"] = "Embed - Text embedding model"
                                
                                model_details.append(model_detail)
                            
                            api_key.quota_info["model_details"] = model_details
                    except Exception as e:
                        error_msg = f"Could not parse models information: {str(e)}"
                        app_logger.warning(error_msg)
                        api_key.quota_info["error"] = error_msg
                    
                    # Try to get usage information
                    try:
                        usage_url = "https://api.cohere.ai/v1/usage"
                        async with session.get(usage_url, headers=headers, timeout=10) as usage_response:
                            if usage_response.status == 200:
                                usage_data = await usage_response.json()
                                
                                # Extract usage information
                                if "token_units_used" in usage_data:
                                    api_key.used_tokens = usage_data["token_units_used"]
                                    api_key.quota_info["account_summary"]["used_tokens"] = f"{api_key.used_tokens} tokens"
                                
                                if "token_units_granted" in usage_data:
                                    api_key.monthly_limit = usage_data["token_units_granted"]
                                    api_key.quota_info["account_summary"]["monthly_limit"] = f"{api_key.monthly_limit} tokens"
                                    
                                    # Calculate remaining tokens
                                    if api_key.used_tokens and api_key.monthly_limit:
                                        remaining = int(api_key.monthly_limit) - int(api_key.used_tokens)
                                        api_key.token_limit = str(remaining)
                                        api_key.quota_info["account_summary"]["remaining_tokens"] = f"{remaining} tokens"
                                        
                                        # Calculate usage percentage
                                        if int(api_key.monthly_limit) > 0:
                                            usage_percent = (int(api_key.used_tokens) / int(api_key.monthly_limit)) * 100
                                            api_key.quota_info["account_summary"]["usage_percentage"] = f"{usage_percent:.1f}%"
                            else:
                                app_logger.warning(f"Could not get usage information: {usage_response.status}")
                    except Exception as e:
                        app_logger.warning(f"Could not get usage information: {str(e)}")
                    
                    return api_key
        
        except aiohttp.ClientError as e:
            error_msg = f"Error connecting to Cohere API: {str(e)}"
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
        if not isinstance(api_key, CohereKey):
            return {"error": "Not a Cohere API key"}
        
        results = {
            "provider": "Cohere",
            "is_valid": api_key.is_valid,
            "message": api_key.message,
            "api_key": api_key.api_key
        }
        
        if api_key.is_valid:
            results.update({
                "token_limit": api_key.token_limit,
                "used_tokens": api_key.used_tokens,
                "monthly_limit": api_key.monthly_limit,
                "model_count": api_key.quota_info.get("model_count", 0),
            })
            
            if "account_summary" in api_key.quota_info:
                results["account_summary"] = api_key.quota_info["account_summary"]
        
        return results
