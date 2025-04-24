"""OpenRouter API key validator for LLM API Key Validator."""

import aiohttp
from typing import Optional, Dict, Any

from core.validator import Validator
from core.api_key import APIKey, OpenRouterKey
from utils.logger import app_logger


class OpenRouterValidator(Validator):
    """Validator for OpenRouter API keys."""

    async def validate(self, api_key: APIKey) -> Optional[APIKey]:
        """
        Validate an OpenRouter API key and retrieve quota information.

        Args:
            api_key: The OpenRouter API key to validate

        Returns:
            The updated API key with validation results, or None if validation failed
        """
        if not isinstance(api_key, OpenRouterKey):
            api_key = OpenRouterKey(api_key.api_key)

        # OpenRouter uses OpenAI-compatible endpoints
        models_url = "https://openrouter.ai/api/v1/models"
        headers = {
            "Authorization": f"Bearer {api_key.api_key}",
            "HTTP-Referer": "https://llm-api-key-validator.app",  # Required by OpenRouter
            "X-Title": "LLM API Key Validator"  # Required by OpenRouter
        }

        try:
            # No need to log normal validation operations at WARNING level

            async with aiohttp.ClientSession() as session:
                # First check if the key is valid by listing models
                async with session.get(models_url, headers=headers, timeout=10) as models_response:
                    api_key.raw_response = await models_response.text()

                    if models_response.status != 200:
                        api_key.is_valid = False
                        if models_response.status == 401:
                            api_key.message = "Invalid OpenRouter API key."
                            app_logger.warning(f"Invalid OpenRouter API key: {models_response.status}")
                        else:
                            api_key.message = f"Unexpected response from OpenRouter API: {models_response.status}"
                            app_logger.warning(f"Unexpected response from OpenRouter API: {models_response.status} - {api_key.raw_response[:200]}")
                        return None

                    # Key is valid
                    api_key.is_valid = True
                    api_key.message = "OpenRouter API key is valid."

                    # Always add basic account summary information for OpenRouter
                    api_key.quota_info["account_summary"] = {
                        "plan": "Free Tier",
                        "status": "Active",
                        "credit_card": "Not required for free tier"
                    }

                    # Parse models information
                    try:
                        models_data = await models_response.json()
                        if "data" in models_data:
                            models = models_data["data"]
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

                                # Add pricing information if available
                                if "pricing" in model:
                                    pricing = model["pricing"]
                                    if "prompt" in pricing:
                                        model_detail["prompt_price"] = f"${pricing['prompt']} per 1M tokens"
                                    if "completion" in pricing:
                                        model_detail["completion_price"] = f"${pricing['completion']} per 1M tokens"

                                model_details.append(model_detail)

                            api_key.quota_info["model_details"] = model_details
                    except Exception as e:
                        error_msg = f"Could not parse models information: {str(e)}"
                        app_logger.warning(error_msg)
                        api_key.quota_info["error"] = error_msg

                # Try to get credits information using the new endpoint
                credits_url = "https://openrouter.ai/api/v1/credits"
                async with session.get(credits_url, headers=headers, timeout=10) as credits_response:
                    if credits_response.status == 200:
                        try:
                            credits_data = await credits_response.json()

                            # Extract data from the response
                            if "data" in credits_data:
                                data = credits_data["data"]

                                # Extract credit/usage information
                                if "total_credits" in data:
                                    total_credits = data["total_credits"]
                                    api_key.credit_limit = total_credits
                                    api_key.quota_info["account_summary"]["total_credits"] = f"${total_credits:.4f}"

                                if "total_usage" in data:
                                    total_usage = data["total_usage"]
                                    api_key.usage = total_usage
                                    api_key.quota_info["account_summary"]["total_usage"] = f"${total_usage:.4f}"

                                # Calculate remaining balance
                                if "total_credits" in data and "total_usage" in data:
                                    total_credits = data["total_credits"]
                                    total_usage = data["total_usage"]
                                    balance = total_credits - total_usage
                                    api_key.balance = balance
                                    api_key.quota_info["account_summary"]["balance"] = f"${balance:.4f}"

                                    # Check if user has reached their limit
                                    if total_credits > 0 and total_usage >= total_credits:
                                        api_key.limit_reached = True
                                        api_key.quota_info["account_summary"]["limit_reached"] = "Yes"
                                    else:
                                        api_key.limit_reached = False
                                        api_key.quota_info["account_summary"]["limit_reached"] = "No"

                                # Determine if user has bought credits
                                # If total_credits > 1.0, they likely purchased credits (default is $1)
                                if "total_credits" in data:
                                    total_credits = data["total_credits"]
                                    api_key.bought_credits = total_credits > 1.0
                                    api_key.quota_info["account_summary"]["bought_credits"] = "Yes" if total_credits > 1.0 else "No"

                                    # Update plan information based on credits
                                    if total_credits > 1.0:
                                        api_key.quota_info["account_summary"]["plan"] = "Paid Tier"
                                    else:
                                        api_key.quota_info["account_summary"]["plan"] = "Free Tier"

                                # Set default rate limit if not available from API
                                if "rate_limit" not in api_key.quota_info["account_summary"]:
                                    api_key.rpm = 60  # Default value
                                    api_key.quota_info["account_summary"]["rate_limit"] = "60 requests per minute"
                        except Exception as e:
                            app_logger.warning(f"Could not parse credits information: {str(e)}")
                    else:
                        app_logger.warning(f"Could not get credits information: {credits_response.status}")

                return api_key

        except aiohttp.ClientError as e:
            error_msg = f"Error connecting to OpenRouter API: {str(e)}"
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
        if not isinstance(api_key, OpenRouterKey):
            return {"error": "Not an OpenRouter API key"}

        results = {
            "provider": "OpenRouter",
            "is_valid": api_key.is_valid,
            "message": api_key.message,
            "api_key": api_key.api_key
        }

        if api_key.is_valid:
            results.update({
                "usage": api_key.usage,
                "credit_limit": api_key.credit_limit,
                "rpm": api_key.rpm,
                "balance": api_key.balance,
                "limit_reached": api_key.limit_reached,
                "bought_credits": api_key.bought_credits,
                "model_count": api_key.quota_info.get("model_count", 0),
            })

            # Include all quota information
            results["quota_info"] = api_key.quota_info

            if "account_summary" in api_key.quota_info:
                results["account_summary"] = api_key.quota_info["account_summary"]

        return results
