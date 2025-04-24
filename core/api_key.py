"""
Base APIKey class and provider-specific subclasses for the LLM API Key Validator.
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Set


class Provider(Enum):
    """Enum representing supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MISTRAL = "mistral"
    GROQ = "groq"
    COHERE = "cohere"
    GOOGLE = "google"
    OPENROUTER = "openrouter"
    TOGETHER = "together"
    PERPLEXITY = "perplexity"
    ANYSCALE = "anyscale"
    REPLICATE = "replicate"
    AI21 = "ai21"
    DEEPSEEK = "deepseek"
    ELEVENLABS = "elevenlabs"
    XAI = "xai"
    VERTEXAI = "vertexai"
    AZURE = "azure"
    AWS = "aws"
    CUSTOM = "custom"


class APIKey:
    """Base class for API keys with common attributes and methods."""

    def __init__(self, provider: Provider, api_key: str):
        """
        Initialize a new APIKey instance.

        Args:
            provider: The provider enum value
            api_key: The API key string
        """
        self.provider = provider
        self.api_key = api_key
        self.is_valid = False
        self.message = ""
        self.error = None
        self.raw_response = None
        self.quota_info = {}
        
    def clone(self) -> 'APIKey':
        """Create a copy of this APIKey instance."""
        cloned_key = APIKey(self.provider, self.api_key)
        cloned_key.__dict__ = self.__dict__.copy()
        return cloned_key


class OpenAIKey(APIKey):
    """OpenAI-specific API key with additional attributes."""
    
    def __init__(self, api_key: str):
        """Initialize an OpenAI API key."""
        super().__init__(Provider.OPENAI, api_key)
        self.model = ""
        self.has_quota = False
        self.default_org = ""
        self.organizations = []
        self.rpm = 0
        self.tier = ""
        self.has_special_models = False
        self.extra_models = False
        self.extra_model_list = set()


class AnthropicKey(APIKey):
    """Anthropic-specific API key with additional attributes."""
    
    def __init__(self, api_key: str):
        """Initialize an Anthropic API key."""
        super().__init__(Provider.ANTHROPIC, api_key)
        self.pozzed = False
        self.rate_limited = False
        self.has_quota = True
        self.tier = ""
        self.remaining_tokens = 0


class MistralKey(APIKey):
    """Mistral-specific API key with additional attributes."""
    
    def __init__(self, api_key: str):
        """Initialize a Mistral API key."""
        super().__init__(Provider.MISTRAL, api_key)
        self.subbed = False
        self.tier = ""
        self.rate_limit = ""


class GroqKey(APIKey):
    """Groq-specific API key with additional attributes."""
    
    def __init__(self, api_key: str):
        """Initialize a Groq API key."""
        super().__init__(Provider.GROQ, api_key)
        self.model = ""
        self.rate_limit = ""
        self.token_limit = ""


class CohereKey(APIKey):
    """Cohere-specific API key with additional attributes."""
    
    def __init__(self, api_key: str):
        """Initialize a Cohere API key."""
        super().__init__(Provider.COHERE, api_key)
        self.token_limit = ""
        self.used_tokens = ""
        self.monthly_limit = ""


class GoogleKey(APIKey):
    """Google-specific API key with additional attributes."""
    
    def __init__(self, api_key: str):
        """Initialize a Google API key."""
        super().__init__(Provider.GOOGLE, api_key)
        self.models = []
        self.enabled_billing = False


class OpenRouterKey(APIKey):
    """OpenRouter-specific API key with additional attributes."""
    
    def __init__(self, api_key: str):
        """Initialize an OpenRouter API key."""
        super().__init__(Provider.OPENROUTER, api_key)
        self.usage = 0
        self.credit_limit = 0
        self.rpm = 0
        self.balance = 0
        self.limit_reached = False
        self.bought_credits = False


class TogetherKey(APIKey):
    """Together-specific API key with additional attributes."""
    
    def __init__(self, api_key: str):
        """Initialize a Together API key."""
        super().__init__(Provider.TOGETHER, api_key)
        self.remaining_credits = ""
        self.initial_credits = ""
        self.credits_expire = ""


class PerplexityKey(APIKey):
    """Perplexity-specific API key with additional attributes."""
    
    def __init__(self, api_key: str):
        """Initialize a Perplexity API key."""
        super().__init__(Provider.PERPLEXITY, api_key)
        self.token_limit = ""


class AnyscaleKey(APIKey):
    """Anyscale-specific API key with additional attributes."""
    
    def __init__(self, api_key: str):
        """Initialize an Anyscale API key."""
        super().__init__(Provider.ANYSCALE, api_key)
        self.token_limit = ""


class ReplicateKey(APIKey):
    """Replicate-specific API key with additional attributes."""
    
    def __init__(self, api_key: str):
        """Initialize a Replicate API key."""
        super().__init__(Provider.REPLICATE, api_key)
        self.username = ""
        self.name = ""
        self.credits = ""
        self.expiration = ""


class AI21Key(APIKey):
    """AI21-specific API key with additional attributes."""
    
    def __init__(self, api_key: str):
        """Initialize an AI21 API key."""
        super().__init__(Provider.AI21, api_key)
        self.trial_elapsed = False


class DeepseekKey(APIKey):
    """Deepseek-specific API key with additional attributes."""
    
    def __init__(self, api_key: str):
        """Initialize a Deepseek API key."""
        super().__init__(Provider.DEEPSEEK, api_key)
        self.balance = "$0.0 USD"
        self.available = False
        self.rate_limited = False


class ElevenLabsKey(APIKey):
    """ElevenLabs-specific API key with additional attributes."""
    
    def __init__(self, api_key: str):
        """Initialize an ElevenLabs API key."""
        super().__init__(Provider.ELEVENLABS, api_key)
        self.characters_left = 0
        self.usage = ""
        self.tier = ""
        self.unlimited = False
        self.pro_voice_limit = 0


class XAIKey(APIKey):
    """XAI-specific API key with additional attributes."""
    
    def __init__(self, api_key: str):
        """Initialize an XAI API key."""
        super().__init__(Provider.XAI, api_key)
        self.blocked = True
        self.subbed = False


class VertexAIKey(APIKey):
    """VertexAI-specific API key with additional attributes."""
    
    def __init__(self, api_key: str):
        """Initialize a VertexAI API key."""
        super().__init__(Provider.VERTEXAI, api_key)
        self.project_id = ""
        self.has_opus = False


class AzureKey(APIKey):
    """Azure-specific API key with additional attributes."""
    
    def __init__(self, api_key: str):
        """Initialize an Azure API key."""
        super().__init__(Provider.AZURE, api_key)
        self.endpoint = ""
        self.best_deployment = ""
        self.model = ""
        self.deployments = []
        self.unfiltered = False
        self.dalle_deployments = ""
        self.has_gpt4_turbo = []


class AWSKey(APIKey):
    """AWS-specific API key with additional attributes."""
    
    def __init__(self, api_key: str):
        """Initialize an AWS API key."""
        super().__init__(Provider.AWS, api_key)
        self.username = ""
        self.useless = True
        self.admin_priv = False
        self.bedrock_enabled = False
        self.region = ""
        self.alt_regions = []
        self.useless_reasons = []
        self.logged = False
        self.models = {}


def create_api_key(provider: Provider, api_key: str) -> APIKey:
    """
    Factory function to create the appropriate APIKey subclass.
    
    Args:
        provider: The provider enum value
        api_key: The API key string
        
    Returns:
        An instance of the appropriate APIKey subclass
    """
    key_classes = {
        Provider.OPENAI: OpenAIKey,
        Provider.ANTHROPIC: AnthropicKey,
        Provider.MISTRAL: MistralKey,
        Provider.GROQ: GroqKey,
        Provider.COHERE: CohereKey,
        Provider.GOOGLE: GoogleKey,
        Provider.OPENROUTER: OpenRouterKey,
        Provider.TOGETHER: TogetherKey,
        Provider.PERPLEXITY: PerplexityKey,
        Provider.ANYSCALE: AnyscaleKey,
        Provider.REPLICATE: ReplicateKey,
        Provider.AI21: AI21Key,
        Provider.DEEPSEEK: DeepseekKey,
        Provider.ELEVENLABS: ElevenLabsKey,
        Provider.XAI: XAIKey,
        Provider.VERTEXAI: VertexAIKey,
        Provider.AZURE: AzureKey,
        Provider.AWS: AWSKey,
    }
    
    key_class = key_classes.get(provider, APIKey)
    return key_class(api_key)
