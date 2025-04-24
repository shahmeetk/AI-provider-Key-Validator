"""
Provider detection utilities for LLM API Key Validator.
"""

import re
from typing import Optional
from core.api_key import Provider, create_api_key, APIKey


class ProviderDetector:
    """Utility class for detecting providers from API keys."""
    
    # Regular expressions for different provider key formats
    OPENAI_REGEX = re.compile(r'(sk-\w{48})')
    ANTHROPIC_REGEX = re.compile(r'sk-ant-api03-\w{93}AA')
    ANTHROPIC_SECONDARY_REGEX = re.compile(r'sk-ant-\w{86}')
    ANTHROPIC_THIRD_REGEX = re.compile(r'sk-\w{86}')
    MISTRAL_REGEX = re.compile(r'\w{32}')
    GROQ_REGEX = re.compile(r'gsk_\w{48}')
    COHERE_REGEX = re.compile(r'\w{40}')
    GOOGLE_REGEX = re.compile(r'AIzaSy\w{33}')
    OPENROUTER_REGEX = re.compile(r'sk-or-v1-\w{64}')
    TOGETHER_REGEX = re.compile(r'\w{40}')
    PERPLEXITY_REGEX = re.compile(r'pplx-\w{40}')
    ANYSCALE_REGEX = re.compile(r'esecret_\w{40}')
    REPLICATE_REGEX = re.compile(r'r8_\w{40}')
    AI21_REGEX = re.compile(r'\w{32}')
    DEEPSEEK_REGEX = re.compile(r'sk-\w{32}')
    ELEVENLABS_REGEX = re.compile(r'\w{32}')
    ELEVENLABS_SECONDARY_REGEX = re.compile(r'sk_\w{48}')
    XAI_REGEX = re.compile(r'xai-\w{80}')
    AWS_REGEX = re.compile(r'^(AKIA\w{16}):(\w{40})$')
    AZURE_REGEX = re.compile(r'^(.+):(\w{32})$')
    
    @classmethod
    def detect_provider(cls, api_key: str) -> Optional[APIKey]:
        """
        Detect the provider from an API key.
        
        Args:
            api_key: The API key to detect
            
        Returns:
            An APIKey instance with the detected provider, or None if detection failed
        """
        # Check for keys with distinctive prefixes first
        if api_key.startswith("sk-ant-"):
            if "ant-api03" in api_key and cls.ANTHROPIC_REGEX.match(api_key):
                return create_api_key(Provider.ANTHROPIC, api_key)
            elif cls.ANTHROPIC_SECONDARY_REGEX.match(api_key):
                return create_api_key(Provider.ANTHROPIC, api_key)
        
        elif api_key.startswith("gsk_") and cls.GROQ_REGEX.match(api_key):
            return create_api_key(Provider.GROQ, api_key)
        
        elif api_key.startswith("AIzaSy") and cls.GOOGLE_REGEX.match(api_key):
            return create_api_key(Provider.GOOGLE, api_key)
        
        elif api_key.startswith("sk-or-v1-") and cls.OPENROUTER_REGEX.match(api_key):
            return create_api_key(Provider.OPENROUTER, api_key)
        
        elif api_key.startswith("pplx-") and cls.PERPLEXITY_REGEX.match(api_key):
            return create_api_key(Provider.PERPLEXITY, api_key)
        
        elif api_key.startswith("esecret_") and cls.ANYSCALE_REGEX.match(api_key):
            return create_api_key(Provider.ANYSCALE, api_key)
        
        elif api_key.startswith("r8_") and cls.REPLICATE_REGEX.match(api_key):
            return create_api_key(Provider.REPLICATE, api_key)
        
        elif api_key.startswith("xai-") and cls.XAI_REGEX.match(api_key):
            return create_api_key(Provider.XAI, api_key)
        
        elif api_key.startswith("sk_") and cls.ELEVENLABS_SECONDARY_REGEX.match(api_key):
            return create_api_key(Provider.ELEVENLABS, api_key)
        
        elif api_key.startswith("sk-"):
            # Could be OpenAI, Deepseek, or Anthropic
            if "T3BlbkFJ" in api_key and cls.OPENAI_REGEX.match(api_key):
                return create_api_key(Provider.OPENAI, api_key)
            elif len(api_key) < 36 and cls.DEEPSEEK_REGEX.match(api_key):
                return create_api_key(Provider.DEEPSEEK, api_key)
            elif len(api_key) > 36 and cls.ANTHROPIC_THIRD_REGEX.match(api_key):
                return create_api_key(Provider.ANTHROPIC, api_key)
        
        # Check for keys with special formats
        if ":" in api_key:
            if "AKIA" in api_key and cls.AWS_REGEX.match(api_key):
                return create_api_key(Provider.AWS, api_key)
            elif cls.AZURE_REGEX.match(api_key):
                return create_api_key(Provider.AZURE, api_key)
        
        # Check for generic keys that need further validation
        if cls.MISTRAL_REGEX.match(api_key) and len(api_key) == 32:
            # Could be Mistral, AI21, or ElevenLabs - we'll try Mistral first
            return create_api_key(Provider.MISTRAL, api_key)
        
        if cls.COHERE_REGEX.match(api_key) and len(api_key) == 40:
            # Could be Cohere or Together - we'll try Cohere first
            return create_api_key(Provider.COHERE, api_key)
        
        # If we can't detect the provider, return None
        return None
