# Quota Information Structure

This document explains the structure of the quota information returned by the validators in the LLM API Key Validator.

## Overview

When a validator validates an API key, it retrieves quota information from the provider's API and stores it in the `quota_info` dictionary of the `APIKey` object. This information is then formatted and displayed in the UI.

## Common Quota Information

Most providers return similar types of quota information:

1. **Plan Information**: The user's subscription plan (e.g., Free, Pro, Enterprise)
2. **Usage Information**: How much of the quota has been used
3. **Limit Information**: The user's quota limits (e.g., tokens per month, requests per minute)
4. **Model Information**: Which models the user has access to
5. **Rate Limit Information**: How many requests the user can make per minute

## Quota Information Structure

The `quota_info` dictionary has the following structure:

```python
quota_info = {
    "account_summary": {
        "plan": "Plan name",
        "status": "Active/Inactive",
        "credit_card": "Added/Not added",
        "rate_limit": "Requests per minute",
        "token_limit": "Tokens per month",
        "current_usage": "Current usage",
        "billing_period": "Billing period",
        "featured_models": "List of featured models",
        # Other provider-specific information
    },
    "available_models": ["model1", "model2", "model3"],
    "model_count": 3,
    "model_details": [
        {
            "id": "model1",
            "description": "Model description",
            "context_length": "Context length",
            "capabilities": ["Capability 1", "Capability 2"]
        },
        # More model details
    ],
    "usage": {
        "total_usage": 0.0,
        "period": "Start date to end date"
    },
    # Other provider-specific information
}
```

## Provider-Specific Quota Information

Each provider returns different quota information:

### OpenAI

```python
quota_info = {
    "account_summary": {
        "plan": "Pay-as-you-go",
        "status": "Active",
        "payment_method": "✅ Added",
        "hard_limit": "$120",
        "soft_limit": "$100",
        "current_usage": "$10.50",
        "billing_period": "2023-05-01 to 2023-05-31",
        "organizations": 1,
        "default_org": "org-abcdefgh",
        "rate_limit": "3500 requests per minute",
        "tier": "Medium Tier"
    },
    "available_models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
    "model_count": 3,
    "usage": {
        "total_usage": 10.50,
        "period": "2023-05-01 to 2023-05-31"
    }
}
```

### Anthropic

```python
quota_info = {
    "account_summary": {
        "plan": "Pay-as-you-go",
        "status": "Active",
        "credit_card": "Required for full access",
        "available_models": "3 models available",
        "featured_models": "claude-3-opus, claude-3-sonnet, claude-3-haiku",
        "rate_limit": "100 requests per minute",
        "remaining_requests": "95"
    },
    "available_models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
    "model_count": 3,
    "model_details": [
        {
            "id": "claude-3-opus",
            "description": "Claude 3 Opus - Most powerful Claude model",
            "context_length": "200K tokens",
            "capabilities": ["Text generation", "Chat completions"]
        },
        # More model details
    ]
}
```

### Mistral

```python
quota_info = {
    "account_summary": {
        "plan": "Free Developer Tier",
        "status": "Active",
        "credit_card": "Not required for free tier",
        "available_models": "4 models available",
        "featured_models": "mistral-small, mistral-medium, mistral-large, mixtral-8x7b",
        "rate_limit": "5 tokens per minute",
        "subscription": "Free Tier"
    },
    "available_models": ["mistral-small", "mistral-medium", "mistral-large", "mixtral-8x7b"],
    "model_count": 4,
    "model_details": [
        {
            "id": "mistral-small",
            "description": "Mistral Small - Fast and cost-effective",
            "context_length": "32K tokens",
            "capabilities": ["Text generation", "Chat completions"]
        },
        # More model details
    ]
}
```

## Displaying Quota Information

The quota information is displayed in the UI in three tabs:

1. **Summary Tab**: Displays the account summary information
2. **Models Tab**: Displays the available models and their details
3. **Raw Data Tab**: Displays the raw quota information as JSON

The summary tab is the most important, as it provides a quick overview of the user's account status and quota information.

## Adding Quota Information for a New Provider

When adding a new provider, you should retrieve as much quota information as possible from the provider's API. The more information you can provide, the more useful the validator will be.

Here's an example of how to add quota information for a new provider:

```python
# Add basic account summary information
api_key.quota_info["account_summary"] = {
    "plan": "Free Developer Tier",
    "status": "Active",
    "credit_card": "Not required for free tier"
}

# Parse models information
try:
    data = await response.json()
    if "models" in data:
        models = data["models"]
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
            model_detail = {
                "id": model_id,
                "capabilities": ["Text generation", "Chat completions"]
            }
            
            # Add specific model information based on name
            if "large" in model_id.lower():
                model_detail["description"] = "Large model - Most powerful"
            elif "medium" in model_id.lower():
                model_detail["description"] = "Medium model - Balanced performance and cost"
            elif "small" in model_id.lower():
                model_detail["description"] = "Small model - Fast and cost-effective"
            
            model_details.append(model_detail)
        
        api_key.quota_info["model_details"] = model_details
except Exception as e:
    error_msg = f"Could not parse models information: {str(e)}"
    app_logger.warning(error_msg)
    api_key.quota_info["error"] = error_msg

# Try to get usage information
try:
    usage_url = "https://api.newprovider.com/v1/usage"
    async with session.get(usage_url, headers=headers, timeout=10) as usage_response:
        if usage_response.status == 200:
            usage_data = await usage_response.json()
            
            # Extract usage information
            if "used_tokens" in usage_data:
                api_key.used_tokens = usage_data["used_tokens"]
                api_key.quota_info["account_summary"]["used_tokens"] = f"{api_key.used_tokens} tokens"
            
            if "token_limit" in usage_data:
                api_key.token_limit = usage_data["token_limit"]
                api_key.quota_info["account_summary"]["token_limit"] = f"{api_key.token_limit} tokens"
                
                # Calculate remaining tokens
                if api_key.used_tokens and api_key.token_limit:
                    remaining = int(api_key.token_limit) - int(api_key.used_tokens)
                    api_key.quota_info["account_summary"]["remaining_tokens"] = f"{remaining} tokens"
except Exception as e:
    app_logger.warning(f"Could not get usage information: {str(e)}")
```

## Best Practices

1. **Provide a Comprehensive Account Summary**: The account summary should provide a quick overview of the user's account status and quota information
2. **Include Model Information**: Include information about the models the user has access to
3. **Include Rate Limit Information**: Include information about the user's rate limits
4. **Include Token Limit Information**: Include information about the user's token limits
5. **Handle Missing Information Gracefully**: Not all providers provide all types of quota information, so handle missing information gracefully
6. **Use Consistent Formatting**: Use consistent formatting for similar types of information (e.g., rate limits, token limits)
7. **Add Provider-Specific Information**: Add provider-specific information that is relevant to the user
