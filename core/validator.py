"""
Base Validator interface for LLM API Key Validator.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from core.api_key import APIKey


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


class ValidatorFactory:
    """Factory for creating validators."""

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
        from validators.mistral import MistralValidator
        from validators.groq import GroqValidator
        from validators.cohere import CohereValidator
        from validators.google import GoogleValidator
        from validators.openrouter import OpenRouterValidator

        validators = {
            "openai": OpenAIValidator,
            "anthropic": AnthropicValidator,
            "mistral": MistralValidator,
            "groq": GroqValidator,
            "cohere": CohereValidator,
            "google": GoogleValidator,
            "openrouter": OpenRouterValidator,
        }

        validator_class = validators.get(provider_name.lower())
        if validator_class:
            return validator_class()

        return None
