# API Key Detection

The LLM API Key Validator can automatically detect the provider from the API key format. This document explains how the detection logic works.

## Detection Process

The detection process is implemented in the `ProviderDetector` class in `utils/detection.py`. It uses regular expressions to match the key patterns for each provider.

The detection process follows these steps:

1. Check for keys with distinctive prefixes first (e.g., "sk-ant-" for Anthropic)
2. Check for keys with special formats (e.g., keys containing ":" for AWS and Azure)
3. Check for generic keys that need further validation (e.g., 32-character strings)

## Provider Key Formats

Here are the key formats for each provider:

| Provider | Key Format | Example |
|----------|------------|---------|
| OpenAI | `sk-` followed by 48 characters | `sk-abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKL` |
| Anthropic | `sk-ant-` followed by 86-93 characters | `sk-ant-api03-abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyzAA` |
| Mistral | 32-character string | `abcdefghijklmnopqrstuvwxyz123456` |
| Groq | `gsk_` followed by 48 characters | `gsk_abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKL` |
| Cohere | 40-character string | `abcdefghijklmnopqrstuvwxyz1234567890ABCD` |
| Google | `AIzaSy` followed by 33 characters | `AIzaSyabcdefghijklmnopqrstuvwxyz123456` |
| OpenRouter | `sk-or-v1-` followed by 64 characters | `sk-or-v1-abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ1234` |
| Together | 40-character string | `abcdefghijklmnopqrstuvwxyz1234567890ABCD` |
| Perplexity | `pplx-` followed by 40 characters | `pplx-abcdefghijklmnopqrstuvwxyz1234567890ABCD` |
| Anyscale | `esecret_` followed by 40 characters | `esecret_abcdefghijklmnopqrstuvwxyz1234567890ABCD` |
| Replicate | `r8_` followed by 40 characters | `r8_abcdefghijklmnopqrstuvwxyz1234567890ABCD` |
| AI21 | 32-character string | `abcdefghijklmnopqrstuvwxyz123456` |
| DeepSeek | `sk-` followed by 32 characters | `sk-abcdefghijklmnopqrstuvwxyz123456` |
| ElevenLabs | 32-character string or `sk_` followed by 48 characters | `abcdefghijklmnopqrstuvwxyz123456` or `sk_abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKL` |
| xAI | `xai-` followed by 80 characters | `xai-abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmn` |
| AWS | `AKIA` followed by 16 characters, then `:`, then 40 characters | `AKIAABCDEFGHIJKLMN:abcdefghijklmnopqrstuvwxyz1234567890ABCD` |
| Azure | Any string, then `:`, then 32 characters | `endpoint:abcdefghijklmnopqrstuvwxyz123456` |

## Regular Expressions

The `ProviderDetector` class uses regular expressions to match these key patterns:

```python
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
```

## Ambiguous Key Formats

Some providers use similar key formats, which can make detection ambiguous. For example, Mistral, AI21, and ElevenLabs all use 32-character strings.

In these cases, the `ProviderDetector` makes a best guess based on the key format and returns the most likely provider. The validator will then attempt to validate the key against that provider's API. If validation fails, the user can manually select the correct provider.

## Adding a New Provider

To add detection for a new provider:

1. Analyze the key format for the new provider
2. Create a regular expression that matches the key format
3. Add the regular expression to the `ProviderDetector` class
4. Update the `detect_provider` method to check for the new provider

For example, to add detection for a new provider with keys that start with "np-" followed by 32 characters:

```python
# Add a regular expression for the new provider
NEWPROVIDER_REGEX = re.compile(r'np-\w{32}')

@classmethod
def detect_provider(cls, api_key: str) -> Optional[APIKey]:
    """Detect the provider from an API key."""
    # ... existing detection logic
    
    # Add detection for the new provider
    elif api_key.startswith("np-") and cls.NEWPROVIDER_REGEX.match(api_key):
        return create_api_key(Provider.NEWPROVIDER, api_key)
    
    # ... more detection logic
```

## Best Practices

1. **Check Distinctive Prefixes First**: Keys with distinctive prefixes (e.g., "sk-ant-" for Anthropic) are easier to detect
2. **Handle Ambiguous Formats**: For ambiguous formats, make a best guess and let the validator confirm
3. **Update Documentation**: Keep this document updated with new provider key formats
4. **Test Detection**: Test detection with both valid and invalid keys
5. **Handle Edge Cases**: Consider edge cases like keys with special characters or unusual lengths
