# Provider Information Structure

This document describes the structure of the provider information used in the LLM API Key Validator.

## Provider Categories

Providers are categorized into four groups:

1. **Free Providers**: Providers that offer free access without requiring a credit card
   - Examples: Mistral, Groq, Google AI

2. **Premium Providers**: Providers that require a credit card for access
   - Examples: OpenAI, Anthropic, Azure OpenAI

3. **Freemium Providers**: Providers that offer limited free access with paid tiers
   - Examples: Cohere, Perplexity, Anyscale, DeepSeek, AI21

4. **Credit-Based Providers**: Providers that offer free credits for new users
   - Examples: Together, Replicate, OpenRouter, ElevenLabs, xAI

## Provider Information Schema

Each provider entry in the `provider_info.json` file follows this schema:

```json
{
  "name": "Provider Name",
  "description": "Short description of the provider",
  "website": "https://provider-website.com",
  "signup_url": "https://provider-website.com/signup",
  "pricing_url": "https://provider-website.com/pricing",
  "docs_url": "https://provider-website.com/docs",
  "free_tier": true|false,
  "credit_card_required": true|false,
  "key_format": "Description of API key format",
  "rate_limit": "Description of rate limits",
  "token_limit": "Description of token limits",
  "featured_models": ["model1", "model2", "model3"]
}
```

## Provider-Specific API Key Classes

Each provider has a specific API key class that inherits from the base `APIKey` class. These classes contain provider-specific attributes:

### OpenAIKey
- `model`: The model being used
- `has_quota`: Whether the key has quota
- `default_org`: Default organization
- `organizations`: List of organizations
- `rpm`: Requests per minute
- `tier`: Tier information
- `has_special_models`: Whether the key has access to special models
- `extra_models`: Whether the key has access to extra models
- `extra_model_list`: List of extra models

### AnthropicKey
- `pozzed`: Whether the key is pozzed
- `rate_limited`: Whether the key is rate limited
- `has_quota`: Whether the key has quota
- `tier`: Tier information
- `remaining_tokens`: Remaining tokens

### MistralKey
- `subbed`: Whether the key is subscribed
- `tier`: Tier information
- `rate_limit`: Rate limit information

### GroqKey
- `model`: The model being used
- `rate_limit`: Rate limit information
- `token_limit`: Token limit information

### CohereKey
- `token_limit`: Token limit information
- `used_tokens`: Used tokens
- `monthly_limit`: Monthly limit

### GoogleKey
- `models`: List of models
- `enabled_billing`: Whether billing is enabled

### OpenRouterKey
- `usage`: Usage information
- `credit_limit`: Credit limit
- `rpm`: Requests per minute
- `balance`: Balance
- `limit_reached`: Whether the limit has been reached
- `bought_credits`: Whether credits have been bought

## Validator Implementation

Each provider has a specific validator class that implements the `Validator` interface. These validators handle:

1. API key validation
2. Quota information retrieval
3. Model information retrieval
4. Account information retrieval
5. Formatting results for display

The `ValidatorFactory` creates the appropriate validator based on the provider name.

## Provider Detection

The `ProviderDetector` class in `utils/detection.py` uses regular expressions to detect the provider from the API key format. This allows for automatic provider detection when the user doesn't specify the provider.
