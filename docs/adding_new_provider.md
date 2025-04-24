# Adding a New Provider

This guide explains how to add support for a new LLM provider to the LLM API Key Validator.

## Step 1: Create a Provider-Specific API Key Class

Add a new class to `core/api_key.py` that inherits from the base `APIKey` class:

```python
class NewProviderKey(APIKey):
    """NewProvider-specific API key with additional attributes."""
    
    def __init__(self, api_key: str):
        """Initialize a NewProvider API key."""
        super().__init__(Provider.NEWPROVIDER, api_key)
        # Add provider-specific attributes
        self.attribute1 = ""
        self.attribute2 = 0
        self.attribute3 = False
```

Also, add a new enum value to the `Provider` enum:

```python
class Provider(Enum):
    """Enum representing supported LLM providers."""
    # Existing providers...
    NEWPROVIDER = "newprovider"
```

Finally, update the `create_api_key` factory function:

```python
def create_api_key(provider: Provider, api_key: str) -> APIKey:
    """Factory function to create the appropriate APIKey subclass."""
    key_classes = {
        # Existing providers...
        Provider.NEWPROVIDER: NewProviderKey,
    }
    
    key_class = key_classes.get(provider, APIKey)
    return key_class(api_key)
```

## Step 2: Implement a Provider-Specific Validator

Create a new file in the `validators/` directory named after the provider (e.g., `validators/newprovider.py`):

```python
"""
NewProvider API key validator for LLM API Key Validator.
"""

import aiohttp
import json
from typing import Optional, Dict, Any, List

from core.validator import Validator
from core.api_key import APIKey, NewProviderKey
from utils.logger import app_logger


class NewProviderValidator(Validator):
    """Validator for NewProvider API keys."""
    
    async def validate(self, api_key: APIKey) -> Optional[APIKey]:
        """
        Validate a NewProvider API key and retrieve quota information.
        
        Args:
            api_key: The NewProvider API key to validate
            
        Returns:
            The updated API key with validation results, or None if validation failed
        """
        if not isinstance(api_key, NewProviderKey):
            api_key = NewProviderKey(api_key.api_key)
        
        url = "https://api.newprovider.com/v1/models"  # Replace with actual API endpoint
        headers = {
            "Authorization": f"Bearer {api_key.api_key}",
            "Accept": "application/json"
        }
        
        try:
            app_logger.info(f"Validating NewProvider API key")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    api_key.raw_response = await response.text()
                    
                    if response.status != 200:
                        api_key.is_valid = False
                        if response.status == 401:
                            api_key.message = "Invalid NewProvider API key."
                            app_logger.warning(f"Invalid NewProvider API key: {response.status}")
                        else:
                            api_key.message = f"Unexpected response from NewProvider API: {response.status}"
                            app_logger.warning(f"Unexpected response from NewProvider API: {response.status} - {api_key.raw_response[:200]}")
                        return None
                    
                    # Key is valid
                    api_key.is_valid = True
                    api_key.message = "NewProvider API key is valid."
                    
                    # Add basic account summary information
                    api_key.quota_info["account_summary"] = {
                        "plan": "Free Tier",
                        "status": "Active"
                    }
                    
                    # Parse response data
                    try:
                        data = await response.json()
                        # Extract and store relevant information
                        # ...
                    except Exception as e:
                        error_msg = f"Could not parse response: {str(e)}"
                        app_logger.warning(error_msg)
                        api_key.quota_info["error"] = error_msg
                    
                    return api_key
        
        except aiohttp.ClientError as e:
            error_msg = f"Error connecting to NewProvider API: {str(e)}"
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
        if not isinstance(api_key, NewProviderKey):
            return {"error": "Not a NewProvider API key"}
        
        results = {
            "provider": "NewProvider",
            "is_valid": api_key.is_valid,
            "message": api_key.message,
            "api_key": api_key.api_key
        }
        
        if api_key.is_valid:
            # Add provider-specific information
            results.update({
                "attribute1": api_key.attribute1,
                "attribute2": api_key.attribute2,
                "attribute3": api_key.attribute3,
            })
            
            if "account_summary" in api_key.quota_info:
                results["account_summary"] = api_key.quota_info["account_summary"]
        
        return results
```

## Step 3: Update the ValidatorFactory

Update the `ValidatorFactory` in `core/validator.py` to include your new validator:

```python
@staticmethod
def create_validator(provider_name: str) -> Optional[Validator]:
    """Create a validator for the specified provider."""
    # Import validators here to avoid circular imports
    from validators.openai import OpenAIValidator
    # ... other imports
    from validators.newprovider import NewProviderValidator
    
    validators = {
        "openai": OpenAIValidator,
        # ... other validators
        "newprovider": NewProviderValidator,
    }
    
    validator_class = validators.get(provider_name.lower())
    if validator_class:
        return validator_class()
    
    return None
```

## Step 4: Add Provider Information

Add information about the new provider to `data/provider_info.json`:

```json
"newprovider": {
  "name": "NewProvider",
  "description": "Description of the provider",
  "website": "https://newprovider.com",
  "signup_url": "https://newprovider.com/signup",
  "pricing_url": "https://newprovider.com/pricing",
  "docs_url": "https://newprovider.com/docs",
  "free_tier": true,
  "credit_card_required": false,
  "key_format": "Description of API key format",
  "rate_limit": "Description of rate limits",
  "token_limit": "Description of token limits",
  "featured_models": ["model1", "model2", "model3"]
}
```

Also, add the provider to the appropriate category:

```json
"categories": {
  "free": {
    "name": "Free Providers",
    "description": "Providers that offer free access without requiring a credit card",
    "providers": ["mistral", "groq", "google", "newprovider"]
  },
  // ... other categories
}
```

## Step 5: Update Provider Detection

Update the `ProviderDetector` in `utils/detection.py` to detect the new provider:

```python
# Add a regular expression for the new provider
NEWPROVIDER_REGEX = re.compile(r'pattern-for-newprovider-keys')

@classmethod
def detect_provider(cls, api_key: str) -> Optional[APIKey]:
    """Detect the provider from an API key."""
    # ... existing detection logic
    
    # Add detection for the new provider
    elif cls.NEWPROVIDER_REGEX.match(api_key):
        return create_api_key(Provider.NEWPROVIDER, api_key)
    
    # ... more detection logic
```

## Step 6: Test the New Provider

Test the new provider by:

1. Validating a valid API key
2. Validating an invalid API key
3. Testing auto-detection
4. Testing bulk validation
5. Checking the provider information page

## Best Practices

1. **API Documentation**: Consult the provider's API documentation for the correct endpoints and authentication methods
2. **Error Handling**: Handle all possible error cases gracefully
3. **Logging**: Use the `app_logger` to log important events and errors
4. **Quota Information**: Extract as much quota information as possible
5. **Account Summary**: Provide a concise account summary for display
6. **Model Information**: Include information about available models
7. **Rate Limits**: Include information about rate limits
8. **Token Limits**: Include information about token limits
9. **Timeouts**: Set appropriate timeouts for API calls
10. **Documentation**: Document the validator's behavior and the API endpoints it uses
