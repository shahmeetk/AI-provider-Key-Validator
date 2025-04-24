# Validator Implementation Guide

This document explains how to implement a new validator for the LLM API Key Validator.

## Validator Interface

All validators must implement the `Validator` interface defined in `core/validator.py`:

```python
class Validator(ABC):
    """Abstract base class for all validators."""
    
    @abstractmethod
    async def validate(self, api_key: APIKey) -> Optional[APIKey]:
        """
        Validate an API key and retrieve quota information.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            The updated API key with validation results, or None if validation failed
        """
        pass
    
    @abstractmethod
    def format_results(self, api_key: APIKey) -> Dict[str, Any]:
        """
        Format the validation results for display.
        
        Args:
            api_key: The validated API key
            
        Returns:
            A dictionary with formatted results
        """
        pass
```

## Implementing a New Validator

To implement a new validator for a provider, follow these steps:

1. Create a new file in the `validators/` directory named after the provider (e.g., `validators/newprovider.py`)
2. Define a new class that inherits from `Validator`
3. Implement the `validate` and `format_results` methods
4. Update the `ValidatorFactory` in `core/validator.py` to include your new validator

### Example Implementation

Here's a template for implementing a new validator:

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
                # Provider-specific fields
            })
            
            if "account_summary" in api_key.quota_info:
                results["account_summary"] = api_key.quota_info["account_summary"]
        
        return results
```

## Updating the ValidatorFactory

After implementing your validator, update the `ValidatorFactory` in `core/validator.py`:

```python
@staticmethod
def create_validator(provider_name: str) -> Optional[Validator]:
    """
    Create a validator for the specified provider.
    
    Args:
        provider_name: The name of the provider
        
    Returns:
        A validator instance, or None if the provider is not supported
    """
    # Import validators here to avoid circular imports
    from validators.openai import OpenAIValidator
    from validators.anthropic import AnthropicValidator
    # ... other imports
    from validators.newprovider import NewProviderValidator
    
    validators = {
        "openai": OpenAIValidator,
        "anthropic": AnthropicValidator,
        # ... other validators
        "newprovider": NewProviderValidator,
    }
    
    validator_class = validators.get(provider_name.lower())
    if validator_class:
        return validator_class()
    
    return None
```

## Best Practices for Validator Implementation

1. **Error Handling**: Always handle exceptions and provide meaningful error messages
2. **Logging**: Use the `app_logger` to log important events and errors
3. **Type Checking**: Ensure the API key is of the correct type
4. **Quota Information**: Extract as much quota information as possible
5. **Account Summary**: Provide a concise account summary for display
6. **Model Information**: Include information about available models
7. **Rate Limits**: Include information about rate limits
8. **Token Limits**: Include information about token limits
9. **Timeouts**: Set appropriate timeouts for API calls
10. **Documentation**: Document the validator's behavior and the API endpoints it uses
