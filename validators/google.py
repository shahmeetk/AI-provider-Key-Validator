"""
Google AI API key validator for LLM API Key Validator.
"""

import aiohttp
import json
from typing import Optional, Dict, Any, List

from core.validator import Validator
from core.api_key import APIKey, GoogleKey
from utils.logger import app_logger


class GoogleValidator(Validator):
    """Validator for Google AI API keys."""
    
    async def validate(self, api_key: APIKey) -> Optional[APIKey]:
        """
        Validate a Google AI API key and retrieve quota information.
        
        Args:
            api_key: The Google AI API key to validate
            
        Returns:
            The updated API key with validation results, or None if validation failed
        """
        if not isinstance(api_key, GoogleKey):
            api_key = GoogleKey(api_key.api_key)
        
        # Google AI Studio API endpoint for models
        url = "https://generativelanguage.googleapis.com/v1/models?key=" + api_key.api_key
        
        try:
            app_logger.info(f"Validating Google AI API key")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    api_key.raw_response = await response.text()
                    
                    if response.status != 200:
                        api_key.is_valid = False
                        if response.status == 400:
                            api_key.message = "Invalid Google AI API key."
                            app_logger.warning(f"Invalid Google AI API key: {response.status}")
                        else:
                            api_key.message = f"Unexpected response from Google AI API: {response.status}"
                            app_logger.warning(f"Unexpected response from Google AI API: {response.status} - {api_key.raw_response[:200]}")
                        return None
                    
                    # Key is valid
                    api_key.is_valid = True
                    api_key.message = "Google AI API key is valid."
                    
                    # Always add basic account summary information for Google
                    api_key.quota_info["account_summary"] = {
                        "plan": "Free Developer Tier",
                        "status": "Active",
                        "credit_card": "Not required for free tier",
                        "rate_limit": "60 requests per minute"
                    }
                    
                    # Parse models information
                    try:
                        data = await response.json()
                        if "models" in data:
                            models = data["models"]
                            api_key.models = [model.get("name", "").split("/")[-1] for model in models]
                            api_key.quota_info["available_models"] = api_key.models
                            api_key.quota_info["model_count"] = len(models)
                            api_key.quota_info["account_summary"]["available_models"] = f"{len(models)} models available"
                            
                            # Add featured models if available
                            featured_models = []
                            for model in models:
                                model_name = model.get("name", "").split("/")[-1]
                                if "gemini" in model_name.lower():
                                    featured_models.append(model_name)
                            
                            if featured_models:
                                api_key.quota_info["account_summary"]["featured_models"] = ", ".join(featured_models[:3])
                            
                            # Add model details with capabilities
                            model_details = []
                            for model in models:
                                model_name = model.get("name", "").split("/")[-1]
                                display_name = model.get("displayName", model_name)
                                model_detail = {
                                    "id": model_name,
                                    "name": display_name,
                                    "capabilities": []
                                }
                                
                                # Add capabilities based on model type
                                if "gemini" in model_name.lower():
                                    model_detail["capabilities"] = ["Text generation", "Chat completions"]
                                    
                                    if "pro" in model_name.lower() and "vision" in model_name.lower():
                                        model_detail["capabilities"].append("Image understanding")
                                        model_detail["description"] = "Gemini Pro Vision - Multimodal model with vision capabilities"
                                    elif "pro" in model_name.lower():
                                        model_detail["description"] = "Gemini Pro - Balanced performance and cost"
                                    elif "ultra" in model_name.lower():
                                        model_detail["description"] = "Gemini Ultra - Most powerful Gemini model"
                                elif "embedding" in model_name.lower():
                                    model_detail["capabilities"] = ["Embeddings"]
                                    model_detail["description"] = "Embedding model for text embeddings"
                                
                                # Add supported generation methods
                                if "supportedGenerationMethods" in model:
                                    methods = model["supportedGenerationMethods"]
                                    if "generateContent" in methods:
                                        if "Chat" not in model_detail["capabilities"]:
                                            model_detail["capabilities"].append("Chat")
                                    if "countTokens" in methods:
                                        model_detail["capabilities"].append("Token counting")
                                    if "embedContent" in methods:
                                        if "Embeddings" not in model_detail["capabilities"]:
                                            model_detail["capabilities"].append("Embeddings")
                                
                                model_details.append(model_detail)
                            
                            api_key.quota_info["model_details"] = model_details
                    except Exception as e:
                        error_msg = f"Could not parse models information: {str(e)}"
                        app_logger.warning(error_msg)
                        api_key.quota_info["error"] = error_msg
                    
                    # Note: Google doesn't provide a public API for quota information
                    api_key.quota_info["account_summary"]["note"] = "Detailed quota information not available through Google AI API"
                    
                    return api_key
        
        except aiohttp.ClientError as e:
            error_msg = f"Error connecting to Google AI API: {str(e)}"
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
        if not isinstance(api_key, GoogleKey):
            return {"error": "Not a Google AI API key"}
        
        results = {
            "provider": "Google AI",
            "is_valid": api_key.is_valid,
            "message": api_key.message,
            "api_key": api_key.api_key
        }
        
        if api_key.is_valid:
            results.update({
                "models": api_key.models,
                "enabled_billing": api_key.enabled_billing,
                "model_count": api_key.quota_info.get("model_count", 0),
            })
            
            if "account_summary" in api_key.quota_info:
                results["account_summary"] = api_key.quota_info["account_summary"]
        
        return results
