"""
OpenAI API key validator for LLM API Key Validator.
"""

import aiohttp
import json
from datetime import datetime
from typing import Optional, Dict, Any, List, Set

from core.validator import Validator
from core.api_key import APIKey, OpenAIKey
from utils.logger import app_logger


class OpenAIValidator(Validator):
    """Validator for OpenAI API keys."""
    
    async def validate(self, api_key: APIKey) -> Optional[APIKey]:
        """
        Validate an OpenAI API key and retrieve quota information.
        
        Args:
            api_key: The OpenAI API key to validate
            
        Returns:
            The updated API key with validation results, or None if validation failed
        """
        if not isinstance(api_key, OpenAIKey):
            api_key = OpenAIKey(api_key.api_key)
        
        headers = {"Authorization": f"Bearer {api_key.api_key}"}
        
        try:
            app_logger.info("Validating OpenAI API key")
            
            # First check if the key is valid by listing models
            async with aiohttp.ClientSession() as session:
                models_url = "https://api.openai.com/v1/models"
                async with session.get(models_url, headers=headers, timeout=10) as models_response:
                    api_key.raw_response = await models_response.text()
                    
                    if models_response.status != 200:
                        api_key.is_valid = False
                        if models_response.status == 401:
                            api_key.message = "Invalid OpenAI API key."
                            app_logger.warning(f"Invalid OpenAI API key: {models_response.status}")
                        else:
                            api_key.message = f"Unexpected response from OpenAI API: {models_response.status}"
                            app_logger.warning(f"Unexpected response from OpenAI API: {models_response.status} - {api_key.raw_response[:200]}")
                        return None
                    
                    # Key is valid, parse models information
                    try:
                        models_data = await models_response.json()
                        if "data" in models_data:
                            models = models_data["data"]
                            api_key.quota_info["available_models"] = [model.get("id") for model in models]
                            api_key.quota_info["model_count"] = len(models)
                            
                            # Check for special models
                            for model in models:
                                model_id = model.get("id", "").lower()
                                if "gpt-4" in model_id:
                                    api_key.has_special_models = True
                                    api_key.extra_models = True
                                    api_key.extra_model_list.add(model_id)
                    except Exception as e:
                        app_logger.warning(f"Could not parse models information: {str(e)}")
                
                # Key is valid, now try to get quota information
                billing_url = "https://api.openai.com/dashboard/billing/subscription"
                async with session.get(billing_url, headers=headers, timeout=10) as billing_response:
                    api_key.is_valid = True
                    api_key.message = "OpenAI API key is valid."
                    
                    # Always add basic account summary information
                    api_key.quota_info["account_summary"] = {
                        "plan": "Pay-as-you-go",
                        "status": "Active",
                        "credit_card": "Required for full access"
                    }
                    
                    if billing_response.status == 200:
                        try:
                            billing_data = await billing_response.json()
                            
                            # Add billing data to quota info
                            api_key.quota_info["plan"] = billing_data.get("plan", {}).get("title", "Unknown")
                            api_key.quota_info["hard_limit_usd"] = billing_data.get("hard_limit_usd")
                            api_key.quota_info["has_payment_method"] = billing_data.get("has_payment_method", False)
                            api_key.quota_info["soft_limit_usd"] = billing_data.get("soft_limit_usd")
                            
                            # Add billing data to account summary
                            api_key.quota_info["account_summary"]["plan"] = billing_data.get("plan", {}).get("title", "Unknown")
                            if billing_data.get("hard_limit_usd") is not None:
                                api_key.quota_info["account_summary"]["hard_limit"] = f"${billing_data.get('hard_limit_usd')}"
                            if billing_data.get("soft_limit_usd") is not None:
                                api_key.quota_info["account_summary"]["soft_limit"] = f"${billing_data.get('soft_limit_usd')}"
                            api_key.quota_info["account_summary"]["payment_method"] = "✅ Added" if billing_data.get("has_payment_method", False) else "❌ Not added"
                            
                            # Set has_quota based on payment method
                            api_key.has_quota = billing_data.get("has_payment_method", False)
                            
                            # Try to get usage data
                            usage_url = "https://api.openai.com/dashboard/billing/usage"
                            current_date = datetime.now()
                            start_date = f"{current_date.year}-{current_date.month:02d}-01"
                            end_date = f"{current_date.year}-{current_date.month:02d}-{current_date.day:02d}"
                            
                            async with session.get(
                                f"{usage_url}?start_date={start_date}&end_date={end_date}",
                                headers=headers,
                                timeout=10
                            ) as usage_response:
                                if usage_response.status == 200:
                                    usage_data = await usage_response.json()
                                    total_usage = usage_data.get("total_usage", 0) / 100  # Convert from cents to dollars
                                    
                                    api_key.quota_info["usage"] = {
                                        "total_usage": total_usage,
                                        "period": f"{start_date} to {end_date}"
                                    }
                                    
                                    # Add usage data to account summary
                                    api_key.quota_info["account_summary"]["current_usage"] = f"${total_usage:.2f}"
                                    api_key.quota_info["account_summary"]["billing_period"] = f"{start_date} to {end_date}"
                        except Exception as e:
                            error_msg = f"Could not parse quota information: {str(e)}"
                            app_logger.warning(error_msg)
                            api_key.quota_info["error"] = error_msg
                    else:
                        app_logger.warning(f"Could not get billing information: {billing_response.status}")
                        api_key.quota_info["account_summary"]["billing_status"] = "Billing information not available"
                
                # Try to get organization information
                orgs_url = "https://api.openai.com/v1/organizations"
                async with session.get(orgs_url, headers=headers, timeout=10) as orgs_response:
                    if orgs_response.status == 200:
                        try:
                            orgs_data = await orgs_response.json()
                            if "data" in orgs_data:
                                orgs = orgs_data["data"]
                                api_key.organizations = [org.get("id") for org in orgs]
                                
                                # Get default org
                                for org in orgs:
                                    if org.get("is_default", False):
                                        api_key.default_org = org.get("id", "")
                                        break
                                
                                # Add organization info to account summary
                                if api_key.organizations:
                                    api_key.quota_info["account_summary"]["organizations"] = len(api_key.organizations)
                                    if api_key.default_org:
                                        api_key.quota_info["account_summary"]["default_org"] = api_key.default_org
                        except Exception as e:
                            app_logger.warning(f"Could not parse organization information: {str(e)}")
                
                # Try to get rate limit information by making a small request
                rate_url = "https://api.openai.com/v1/chat/completions"
                rate_data = {
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 1
                }
                rate_headers = {
                    "Authorization": f"Bearer {api_key.api_key}",
                    "Content-Type": "application/json"
                }
                
                async with session.post(rate_url, headers=rate_headers, json=rate_data, timeout=10) as rate_response:
                    if rate_response.status == 200:
                        # Check headers for rate limit info
                        if "x-ratelimit-limit-requests" in rate_response.headers:
                            rpm = rate_response.headers.get("x-ratelimit-limit-requests")
                            api_key.rpm = int(rpm) if rpm and rpm.isdigit() else 0
                            api_key.quota_info["account_summary"]["rate_limit"] = f"{rpm} requests per minute"
                        
                        # Determine tier based on RPM
                        if api_key.rpm >= 10000:
                            api_key.tier = "Very High Tier"
                        elif api_key.rpm >= 5000:
                            api_key.tier = "High Tier"
                        elif api_key.rpm >= 3500:
                            api_key.tier = "Medium Tier"
                        elif api_key.rpm > 60:
                            api_key.tier = "Low Tier"
                        else:
                            api_key.tier = "Free Tier"
                        
                        api_key.quota_info["account_summary"]["tier"] = api_key.tier
            
            return api_key
        
        except aiohttp.ClientError as e:
            error_msg = f"Error connecting to OpenAI API: {str(e)}"
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
        if not isinstance(api_key, OpenAIKey):
            return {"error": "Not an OpenAI API key"}
        
        results = {
            "provider": "OpenAI",
            "is_valid": api_key.is_valid,
            "message": api_key.message,
        }
        
        if api_key.is_valid:
            results.update({
                "plan": api_key.quota_info.get("plan", "Unknown"),
                "has_quota": api_key.has_quota,
                "tier": api_key.tier,
                "rpm": api_key.rpm,
                "model_count": api_key.quota_info.get("model_count", 0),
                "has_special_models": api_key.has_special_models,
                "special_models": list(api_key.extra_model_list) if api_key.extra_models else [],
                "organizations": len(api_key.organizations) if api_key.organizations else 0,
            })
            
            if "usage" in api_key.quota_info:
                results["usage"] = api_key.quota_info["usage"]
            
            if "account_summary" in api_key.quota_info:
                results["account_summary"] = api_key.quota_info["account_summary"]
        
        return results
