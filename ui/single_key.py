"""Single key validation page for LLM API Key Validator."""

import streamlit as st
import asyncio
from typing import Dict, Any

from core.api_key import Provider, create_api_key
from core.validator import ValidatorFactory
from utils.detection import ProviderDetector
from utils.storage import Storage
from utils.logger import app_logger
from ui.history import add_to_history


def validate_key(api_key: str, selected_provider: str) -> Dict[str, Any]:
    """
    Validate a single API key.

    Args:
        api_key: The API key to validate
        selected_provider: The selected provider

    Returns:
        A dictionary with validation results
    """
    try:
        # Create an APIKey instance
        if selected_provider == "Auto Detect":
            api_key_obj = ProviderDetector.detect_provider(api_key)
            if not api_key_obj:
                return {
                    "is_valid": False,
                    "message": "Could not detect provider for this API key",
                    "provider": "Unknown"
                }
        else:
            provider = Provider(selected_provider.lower())
            api_key_obj = create_api_key(provider, api_key)

        # Get the appropriate validator for this provider
        validator = ValidatorFactory.create_validator(api_key_obj.provider.value)

        if validator:
            # Validate the key
            result = asyncio.run(validator.validate(api_key_obj))

            if result:
                # Save the validation result
                Storage.save_validation_result(result)

                # Return the formatted results
                return validator.format_results(result)
            else:
                return {
                    "is_valid": False,
                    "message": api_key_obj.message or "Validation failed",
                    "provider": api_key_obj.provider.value.capitalize()
                }
        else:
            # For providers without a validator, return a placeholder result
            return {
                "is_valid": False,
                "message": f"Validation for {api_key_obj.provider.value} is not yet implemented",
                "provider": api_key_obj.provider.value.capitalize()
            }

    except Exception as e:
        app_logger.error(f"Error validating key: {str(e)}")
        return {
            "is_valid": False,
            "message": f"Error validating key: {str(e)}",
            "provider": "Unknown"
        }


def display_quota_info(result: Dict[str, Any]) -> None:
    """
    Display quota information.

    Args:
        result: The validation result
    """
    # Create expandable section for detailed info
    with st.expander("Quota and Usage Details"):
        # Create tabs for different types of information
        quota_tabs = st.tabs(["Summary", "Models", "Raw Data"])

        with quota_tabs[0]:  # Summary tab
            # Create a clean summary card with the new styling
            st.markdown("""
            <div class="info-card">
            <h4>Account Summary</h4>
            """, unsafe_allow_html=True)

            # Account summary information
            if "account_summary" in result:
                account_summary = result["account_summary"]

                # Display all available account summary information
                for key, value in account_summary.items():
                    # Format the key for display
                    display_key = key.replace("_", " ").title()
                    st.markdown(f"**{display_key}:** {value}")

            st.markdown("</div>", unsafe_allow_html=True)

        with quota_tabs[1]:  # Models tab
            if "model_count" in result:
                st.markdown(f"**Total Models:** {result['model_count']}")

            # Display available models if present
            if "available_models" in result.get("quota_info", {}):
                st.markdown("**Available Models:**")
                for model in result["quota_info"]["available_models"]:
                    st.markdown(f"- {model}")

            # Display model details if present
            if "model_details" in result.get("quota_info", {}):
                st.markdown("**Model Details:**")
                for model in result["quota_info"]["model_details"]:
                    try:
                        # Handle both string models and dictionary models
                        if isinstance(model, dict):
                            # Get model name safely with fallback
                            model_name = str(model.get("id", "Unknown Model"))

                            # Create expander with safe model name
                            with st.expander(model_name):
                                for key, value in model.items():
                                    if key != "id":  # Skip ID since it's already in the expander title
                                        # Format the key for display
                                        display_key = key.replace("_", " ").title()
                                        if isinstance(value, list):
                                            st.markdown(f"**{display_key}:** {', '.join(str(v) for v in value)}")
                                        else:
                                            st.markdown(f"**{display_key}:** {value}")
                        else:
                            # If model is just a string
                            with st.expander(str(model)):
                                st.markdown("Basic model information")
                    except Exception as e:
                        # Log the error and continue with other models
                        st.error(f"Error displaying model information: {str(e)}")
                        continue

            # For backward compatibility
            if "special_models" in result and result["special_models"]:
                st.markdown("**Special Models:**")
                for model in result["special_models"]:
                    st.markdown(f"- {model}")

        with quota_tabs[2]:  # Raw Data tab
            st.json(result)


def create_single_key_page():
    """Create the single key validation page."""
    st.markdown('<h1 class="main-header">Validate a Single API Key</h1>', unsafe_allow_html=True)

    # Add disclaimer
    st.info("**Disclaimer:** API keys are never stored or cached on our servers. All validation is done in your browser session and keys are not retained after validation. This tool is designed with security and privacy in mind.")

    # Create two columns
    col1, col2 = st.columns([1, 1])

    with col1:
        # Provider selection
        st.markdown("### Select API Provider")
        provider_options = ["Auto Detect"] + [p.value.capitalize() for p in Provider if p != Provider.CUSTOM]
        selected_provider = st.selectbox("", provider_options, index=0)

        # API key input
        st.markdown("### Enter your API key")
        api_key = st.text_input("", type="password")

        # Validate button
        if st.button("Validate Key", use_container_width=True):
            if not api_key:
                st.error("Please enter an API key")
            else:
                with st.spinner("Validating API key..."):
                    # Validate the key
                    validation_result = validate_key(api_key, selected_provider)

                    # Store the result in session state
                    st.session_state.validation_result = validation_result

                    # Add to session history
                    add_to_history(validation_result)

    with col2:
        # Display validation results
        st.markdown("### Validation Results")

        if "validation_result" in st.session_state:
            result = st.session_state.validation_result

            if result["is_valid"]:
                st.success(f"{result['provider']} API key is valid.")

                # Display quota information
                display_quota_info(result)
            else:
                st.error(result["message"])
