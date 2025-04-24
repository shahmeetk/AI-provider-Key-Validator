"""Groq API key validator for LLM API Key Validator."""

import aiohttp
from typing import Optional, Dict, Any

from core.validator import Validator
from core.api_key import APIKey, GroqKey
from utils.logger import app_logger


class GroqValidator(Validator):
    """Validator for Groq API keys."""

    async def validate(self, api_key: APIKey) -> Optional[APIKey]:
        """
        Validate a Groq API key and retrieve available models.

        Args:
            api_key: The Groq API key to validate

        Returns:
            The updated API key with validation results, or None if validation failed
        """
        if not isinstance(api_key, GroqKey):
            api_key = GroqKey(api_key.api_key)

        # Groq uses OpenAI-compatible endpoints
        url = "https://api.groq.com/openai/v1/models"
        headers = {
            "Authorization": f"Bearer {api_key.api_key}",
            "Accept": "application/json"
        }

        try:
            # No need to log normal validation operations at WARNING level

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    api_key.raw_response = await response.text()

                    if response.status != 200:
                        api_key.is_valid = False
                        if response.status == 401:
                            api_key.message = "Invalid Groq API key."
                            app_logger.warning(f"Invalid Groq API key: {response.status}")
                        else:
                            api_key.message = f"Unexpected response from Groq API: {response.status}"
                            app_logger.warning(f"Unexpected response from Groq API: {response.status} - {api_key.raw_response[:200]}")
                        return None

                    # Key is valid
                    api_key.is_valid = True
                    api_key.message = "Groq API key is valid."

                    # Initialize account summary with basic information
                    api_key.quota_info["account_summary"] = {
                        "plan": "Free Developer Tier",
                        "status": "Active",
                        "rate_limit": "60 requests per minute",
                        "token_limit": "Generous token limits",
                        "inference_speed": "Ultra-fast inference",
                        "credit_card": "Not required"
                    }

                    # Groq doesn't have a public billing API endpoint, but we can get model information
                    # which is useful for showing available models and capabilities

                    # Get detailed model information
                    try:
                        # Parse the models from the initial response
                        data = await response.json()
                        models = []

                        if "data" in data:
                            models = data["data"]

                            # Extract model information
                            model_info = {}
                            for model in models:
                                model_id = model.get("id", "")
                                context_window = model.get("context_window", 0)

                                model_info[model_id] = {
                                    "context_window": context_window,
                                    "owned_by": model.get("owned_by", "Unknown")
                                }

                            # Update account summary with model information
                            api_key.quota_info["account_summary"]["model_count"] = len(models)

                            # Add featured models
                            featured_models = []
                            for model in models[:3]:  # Just show first 3
                                if "id" in model:
                                    featured_models.append(model["id"])

                            if featured_models:
                                api_key.quota_info["account_summary"]["featured_models"] = ", ".join(featured_models)
                    except Exception as e:
                        app_logger.warning(f"Could not parse model information: {str(e)}")

                    # Add model details with capabilities
                    model_details = []
                    for model_id, info in model_info.items():
                        model_detail = {
                            "id": model_id,
                            "capabilities": ["Text generation", "Chat completions"],
                            "context_length": f"{info['context_window']} tokens",
                            "owned_by": info["owned_by"]
                        }

                        # Add specific model information based on name
                        if "llama" in model_id.lower():
                            model_detail["description"] = "LLaMA model - Open source model from Meta"
                            if "3" in model_id:
                                model_detail["description"] = "LLaMA 3 - Latest generation from Meta"
                                if "70b" in model_id.lower():
                                    model_detail["description"] = "LLaMA 3 70B - Large parameter model"
                                elif "8b" in model_id.lower():
                                    model_detail["description"] = "LLaMA 3 8B - Small parameter model"
                        elif "mixtral" in model_id.lower():
                            model_detail["description"] = "Mixtral - Mixture of experts model"
                        elif "gemma" in model_id.lower():
                            model_detail["description"] = "Gemma - Lightweight model from Google"
                        elif "whisper" in model_id.lower():
                            model_detail["description"] = "Whisper - Speech-to-text model"
                            model_detail["capabilities"] = ["Speech to text", "Audio transcription"]

                        model_details.append(model_detail)

                    # Store model information
                    api_key.quota_info["available_models"] = list(model_info.keys())
                    api_key.quota_info["model_count"] = len(model_info)
                    api_key.quota_info["account_summary"]["available_models"] = f"{len(model_info)} models available"
                    api_key.quota_info["model_details"] = model_details

                    return api_key

        except aiohttp.ClientError as e:
            error_msg = f"Error connecting to Groq API: {str(e)}"
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
        if not isinstance(api_key, GroqKey):
            return {"error": "Not a Groq API key"}

        results = {
            "provider": "Groq",
            "is_valid": api_key.is_valid,
            "message": api_key.message,
            "api_key": api_key.api_key
        }

        if api_key.is_valid:
            results.update({
                "model": api_key.model,
                "rate_limit": api_key.rate_limit,
                "token_limit": api_key.token_limit,
                "model_count": api_key.quota_info.get("model_count", 0),
            })

            # Include all quota information
            results["quota_info"] = api_key.quota_info

            if "account_summary" in api_key.quota_info:
                results["account_summary"] = api_key.quota_info["account_summary"]

        return results
