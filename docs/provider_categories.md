# Provider Categories

The LLM API Key Validator categorizes providers into four groups based on their pricing model and access requirements.

## 1. Free Providers

These providers offer free access without requiring a credit card:

| Provider | Description | Free Tier Details |
|----------|-------------|-------------------|
| Mistral AI | Provider of Mistral and Mixtral models | Free tier with 5 RPM limit |
| Groq | Ultra-fast LLM inference | Free tier with 30 RPM limit |
| Google AI | Provider of Gemini models | Free tier with 60 RPM limit |

### Key Benefits
- No credit card required
- Immediate access
- Suitable for testing and learning
- Good for low-volume applications

## 2. Premium Providers

These providers require a credit card for access:

| Provider | Description | Key Models |
|----------|-------------|------------|
| OpenAI | Provider of GPT models | GPT-3.5, GPT-4, GPT-4 Turbo |
| Anthropic | Provider of Claude models | Claude 3 Opus, Sonnet, Haiku |
| Azure OpenAI | Microsoft's Azure-hosted OpenAI models | GPT-4, GPT-3.5 Turbo |
| AWS Bedrock | AWS's foundation model service | Claude, Llama, Titan |

### Key Benefits
- Access to state-of-the-art models
- Higher rate limits
- Better reliability and uptime
- Enterprise-grade support options

## 3. Freemium Providers

These providers offer limited free access with paid tiers:

| Provider | Description | Free Tier Limits |
|----------|-------------|------------------|
| Cohere | Provider of Command models | 100K tokens/month |
| Perplexity | Online LLMs with web search | Limited usage |
| Anyscale | Provider of open-source models | Limited usage |
| DeepSeek | Provider of DeepSeek models | Limited usage |
| AI21 Labs | Provider of Jurassic models | Limited usage |

### Key Benefits
- Try before you buy
- Gradual scaling options
- Often specialized in certain domains
- Good for growing applications

## 4. Credit-Based Providers

These providers offer free credits for new users:

| Provider | Description | Initial Credits |
|----------|-------------|-----------------|
| Together AI | Provider of open-source models | $25 credit |
| Replicate | Platform for running open-source models | $5 credit |
| OpenRouter | Unified API for multiple LLM providers | $1 credit |
| ElevenLabs | Text-to-speech models | Limited characters |
| xAI | Provider of Grok models | Limited usage |

### Key Benefits
- Explore premium features without commitment
- Good for short-term projects
- Access to multiple models through one API
- Often includes specialized models

## Choosing the Right Provider

When selecting a provider, consider:

1. **Budget**: Free providers for testing, premium for production
2. **Use Case**: Different providers excel at different tasks
3. **Rate Limits**: Consider your application's throughput needs
4. **Model Availability**: Check which models you need access to
5. **Integration**: Some providers offer easier integration with specific platforms
6. **Specialization**: Some providers focus on specific domains (code, speech, etc.)

## Provider Detection

The LLM API Key Validator can automatically detect the provider from the API key format. This is done using regular expressions that match the key patterns for each provider.

For example:
- OpenAI keys start with "sk-" and are 48 characters long
- Anthropic keys start with "sk-ant-" and follow a specific pattern
- Groq keys start with "gsk_" and are 48 characters long
- Google AI keys start with "AIzaSy" and follow a specific pattern

This auto-detection feature makes it easy to validate keys without having to manually select the provider.
