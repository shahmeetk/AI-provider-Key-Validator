# Modular Structure for LLM API Key Validator

The LLM API Key Validator follows a modular architecture that separates concerns and makes the codebase more maintainable.

## Directory Structure

```bash
llm-api-key-validator/
├── main.py                  # Main entry point
├── run.py                   # Runner script with virtual environment support
├── run.sh                   # Shell script for Unix/Linux
├── run.bat                  # Batch script for Windows
├── requirements.txt         # Dependencies
├── README.md                # Documentation
├── LICENSE                  # License file
├── .gitignore               # Git ignore file
├── core/                    # Core functionality
│   ├── __init__.py
│   ├── api_key.py           # Base APIKey class and subclasses
│   └── validator.py         # Base Validator interface and factory
├── validators/              # Provider-specific validators
│   ├── __init__.py
│   ├── openai.py            # OpenAI validator
│   ├── anthropic.py         # Anthropic validator
│   ├── mistral.py           # Mistral validator
│   ├── groq.py              # Groq validator
│   ├── cohere.py            # Cohere validator
│   ├── google.py            # Google validator
│   ├── openrouter.py        # OpenRouter validator
│   ├── together.py          # Together validator
│   ├── perplexity.py        # Perplexity validator
│   ├── anyscale.py          # Anyscale validator
│   ├── replicate.py         # Replicate validator
│   ├── ai21.py              # AI21 validator
│   ├── deepseek.py          # DeepSeek validator
│   ├── elevenlabs.py        # ElevenLabs validator
│   ├── xai.py               # xAI validator
│   ├── vertexai.py          # VertexAI validator
│   └── azure.py             # Azure validator
├── ui/                      # UI components
│   ├── __init__.py
│   ├── main_app.py          # Main Streamlit app
│   ├── single_key.py        # Single key validation UI
│   ├── bulk_validation.py   # Bulk validation UI
│   ├── history.py           # History UI
│   └── provider_info.py     # Provider info UI
├── utils/                   # Utility modules
│   ├── __init__.py
│   ├── detection.py         # Provider detection utilities
│   ├── storage.py           # Storage utilities
│   ├── csv_utils.py         # CSV utilities
│   └── logger.py            # Logging utilities
├── data/                    # Data files
│   ├── provider_info.json   # Provider information
│   └── history.json         # Validation history
├── docs/                    # Documentation
│   ├── architecture_diagram.txt
│   ├── data_flow_diagram.txt
│   ├── provider_info_structure.md
│   ├── validator_implementation.md
│   └── modular_structure.md
└── logs/                    # Log files
    └── app_YYYYMMDD.log     # Daily log files
```

## Module Responsibilities

### Core Module

The `core` module contains the base classes and interfaces that define the core functionality of the application:

- **api_key.py**: Defines the base `APIKey` class and provider-specific subclasses
  - Each subclass contains provider-specific attributes
  - The `create_api_key` factory function creates the appropriate subclass

- **validator.py**: Defines the `Validator` interface and factory
  - The `Validator` abstract base class defines the interface for all validators
  - The `ValidatorFactory` creates the appropriate validator for a provider

### Validators Module

The `validators` module contains provider-specific validators that implement the `Validator` interface:

- Each validator is in a separate file named after the provider
- Each validator handles API calls and response parsing for a specific provider
- Each validator extracts quota information, model information, and account details

### UI Module

The `ui` module contains Streamlit components for different parts of the application:

- **main_app.py**: Main Streamlit application class
  - Sets up the page configuration
  - Creates the sidebar
  - Manages navigation between tabs

- **single_key.py**: Single key validation page
  - Handles single key validation
  - Displays validation results

- **bulk_validation.py**: Bulk validation page
  - Handles CSV uploads
  - Processes multiple keys
  - Displays validation results

- **history.py**: Validation history page
  - Displays validation history
  - Groups history by provider

- **provider_info.py**: Provider information page
  - Displays provider information
  - Groups providers by category

### Utils Module

The `utils` module contains utility functions used across the application:

- **detection.py**: Provider detection utilities
  - Detects the provider from the API key format
  - Uses regular expressions for pattern matching

- **storage.py**: Storage utilities
  - Manages validation history
  - Loads and saves provider information

- **csv_utils.py**: CSV utilities
  - Parses CSV files for bulk validation
  - Creates CSV files with validation results

- **logger.py**: Logging utilities
  - Configures logging
  - Provides a logger instance for the application

### Data Module

The `data` module contains data files used by the application:

- **provider_info.json**: Provider information
  - Contains metadata about providers
  - Grouped by category (Free, Premium, Freemium, Credit-based)

- **history.json**: Validation history
  - Contains records of validation results
  - Used to display validation history

## Flow of Control

1. The user runs `main.py` (directly or via `run.py`, `run.sh`, or `run.bat`)
2. The `MainApp` class in `ui/main_app.py` is instantiated
3. The user interacts with the UI to validate API keys
4. The UI calls the appropriate validator via the `ValidatorFactory`
5. The validator calls the provider's API to validate the key
6. The validator extracts quota information and other details
7. The results are displayed in the UI and stored in the history

## Adding New Features

### Adding a New Provider

To add a new provider:

1. Add a new subclass to `core/api_key.py`
2. Create a new validator in `validators/`
3. Update the `ValidatorFactory` in `core/validator.py`
4. Add provider information to `data/provider_info.json`
5. Update the provider detection in `utils/detection.py`

### Adding a New UI Feature

To add a new UI feature:

1. Create a new file in `ui/`
2. Update `ui/main_app.py` to include the new feature
3. Update the navigation in the sidebar

### Adding a New Utility

To add a new utility:

1. Create a new file in `utils/`
2. Import and use the utility where needed
