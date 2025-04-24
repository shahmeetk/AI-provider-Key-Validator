"""
Mistral API key validator for LLM API Key Validator.
"""

import aiohttp
import json
from typing import Optional, Dict, Any, List

from core.validator import Validator
from core.api_key import APIKey, MistralKey
from utils.logger import app_logger


class MistralValidator(Validator):
    """Validator for Mistral API keys."""
    
    async def validate(self, api_key: APIKey) -> Optional[APIKey]:
        """
        Validate a Mistral API key and retrieve quota information.
        
        Args:
            api_key: The Mistral API key to validate
            
        Returns:
            The updated API key with validation results, or None if validation failed
        """
        if not isinstance(api_key, MistralKey):
            api_key = MistralKey(api_key.api_key)
        
        url = "https://api.mistral.ai/v1/models"
        headers = {
            "Authorization": f"Bearer {api_key.api_key}",
            "Accept": "application/json"
        }
        
        try:
            app_logger.info(f"Validating Mistral API key using URL: {url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    api_key.raw_response = await response.text()
                    
                    if response.status != 200:
                        api_key.is_valid = False
                        if response.status == 401:
                            api_key.message = "Invalid Mistral API key."
                            app_logger.warning(f"Invalid Mistral API key: {response.status}")
                        else:
                            api_key.message = f"Unexpected response from Mistral API: {response.status}"
                            app_logger.warning(f"Unexpected response from Mistral API: {response.status} - {api_key.raw_response[:200]}")
                        return None
                    
                    # Key is valid
                    api_key.is_valid = True
                    api_key.message = "Mistral API key is valid."
                    
                    # Always add basic account summary information for Mistral
                    api_key.quota_info["account_summary"] = {
                        "plan": "Free Developer Tier",
                        "status": "Active",
                        "credit_card": "Not required for free tier"
                    }
                    
                    # Parse models information
                    try:
                        data = await response.json()
                        if "data" in data:
                            models = data["data"]
                            api_key.quota_info["available_models"] = [model.get("id") for model in models]
                            api_key.quota_info["model_count"] = len(models)
                            api_key.quota_info["account_summary"]["available_models"] = f"{len(models)} models available"
                            
                            # Add featured models if available
                            featured_models = []
                            for model in models[:3]:  # Just show first 3
                                if "id" in model:
                                    featured_models.append(model["id"])
                            
                            if featured_models:
                                api_key.quota_info["account_summary"]["featured_models"] = ", ".join(featured_models)
                            
                            # Add model details with capabilities
                            model_details = []
                            for model in models:
                                model_id = model.get("id", "")
                                context_length = model.get("context_length", "Unknown")
                                model_detail = {
                                    "id": model_id,
                                    "context_length": f"{context_length} tokens",
                                    "capabilities": ["Text generation", "Chat completions"]
                                }
                                
                                # Add specific model information based on name
                                if "mistral-large" in model_id.lower():
                                    model_detail["description"] = "Mistral Large - Most powerful Mistral model"
                                elif "mistral-medium" in model_id.lower():
                                    model_detail["description"] = "Mistral Medium - Balanced performance and cost"
                                elif "mistral-small" in model_id.lower():
                                    model_detail["description"] = "Mistral Small - Fast and cost-effective"
                                elif "mistral-tiny" in model_id.lower():
                                    model_detail["description"] = "Mistral Tiny - Fastest and most cost-effective"
                                elif "mixtral" in model_id.lower():
                                    model_detail["description"] = "Mixtral - Powerful mixture of experts model"
                                elif "codestral" in model_id.lower():
                                    model_detail["description"] = "Codestral - Specialized for code generation"
                                    model_detail["capabilities"].append("Code generation")
                                
                                model_details.append(model_detail)
                            
                            api_key.quota_info["model_details"] = model_details
                            
                            # Try to get rate limits from model data
                            if models and "max_tokens_per_minute" in models[0]:
                                rate_limit = models[0].get("max_tokens_per_minute", "Unknown")
                                api_key.quota_info["account_summary"]["rate_limit"] = f"{rate_limit} tokens per minute"
                                api_key.rate_limit = f"{rate_limit} tokens per minute"
                    except Exception as e:
                        error_msg = f"Could not parse models information: {str(e)}"
                        app_logger.warning(error_msg)
                        api_key.quota_info["error"] = error_msg
                    
                    # Check if this is a paid subscription
                    try:
                        # Make a request to check if the user has a paid subscription
                        subscription_url = "https://api.mistral.ai/v1/user"
                        async with session.get(subscription_url, headers=headers, timeout=10) as sub_response:
                            if sub_response.status == 200:
                                sub_data = await sub_response.json()
                                if "data" in sub_data and "subscription" in sub_data["data"]:
                                    subscription = sub_data["data"]["subscription"]
                                    if subscription and subscription.get("status") == "active":
                                        api_key.subbed = True
                                        api_key.quota_info["account_summary"]["subscription"] = "Active Paid Subscription"
                                        api_key.quota_info["account_summary"]["plan"] = "Paid Plan"
                                        api_key.tier = "Paid"
                                    else:
                                        api_key.subbed = False
                                        api_key.tier = "Free"
                    except Exception as e:
                        app_logger.warning(f"Could not check subscription status: {str(e)}")
                    
                    return api_key
        
        except aiohttp.ClientError as e:
            error_msg = f"Error connecting to Mistral API: {str(e)}"
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
        if not isinstance(api_key, MistralKey):
            return {"error": "Not a Mistral API key"}
        
        results = {
            "provider": "Mistral",
            "is_valid": api_key.is_valid,
            "message": api_key.message,
            "api_key": api_key.api_key
        }
        
        if api_key.is_valid:
            results.update({
                "subbed": api_key.subbed,
                "tier": api_key.tier,
                "rate_limit": api_key.rate_limit,
                "model_count": api_key.quota_info.get("model_count", 0),
            })
            
            if "account_summary" in api_key.quota_info:
                results["account_summary"] = api_key.quota_info["account_summary"]
        
        return results
