"""Bulk validation page for LLM API Key Validator."""

import streamlit as st
import asyncio
from typing import Dict, Any, List

from core.api_key import APIKey
from core.validator import ValidatorFactory
from utils.storage import Storage
from ui.single_key import display_quota_info


def validate_keys_bulk(api_keys: List[APIKey]) -> List[Dict[str, Any]]:
    """
    Validate multiple API keys.

    Args:
        api_keys: The API keys to validate

    Returns:
        A list of dictionaries with validation results
    """
    results = []

    for api_key in api_keys:
        # Get the appropriate validator for this provider
        validator = ValidatorFactory.create_validator(api_key.provider.value)

        if validator:
            # Validate the key
            result = asyncio.run(validator.validate(api_key))

            if result:
                # Save the validation result
                Storage.save_validation_result(result)

                # Add the formatted results
                results.append(validator.format_results(result))
            else:
                results.append({
                    "is_valid": False,
                    "message": api_key.message or "Validation failed",
                    "provider": api_key.provider.value.capitalize(),
                    "api_key": api_key.api_key
                })
        else:
            # For providers without a validator, add a placeholder result
            results.append({
                "is_valid": False,
                "message": f"Validation for {api_key.provider.value} is not yet implemented",
                "provider": api_key.provider.value.capitalize(),
                "api_key": api_key.api_key
            })

    return results


def create_bulk_validation_page():
    """Create the bulk validation page."""
    st.markdown('<h1 class="main-header">Bulk Validation</h1>', unsafe_allow_html=True)

    st.markdown("""
    Upload a CSV file containing API keys to validate multiple keys at once.

    The CSV file should have the following columns:
    - `api_key` (required): The API key to validate
    - `provider` (optional): The provider name (e.g., openai, anthropic)

    If the provider column is not present, the application will try to auto-detect the provider.
    """)

    # File upload
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded_file is not None:
        # Read the CSV file
        csv_data = uploaded_file.read()

        # Validate button
        if st.button("Validate All Keys", use_container_width=True):
            with st.spinner("Validating API keys..."):
                # Process the CSV file
                from utils.csv_utils import CSVProcessor
                api_keys = CSVProcessor.parse_csv(csv_data)

                if not api_keys:
                    st.error("No valid API keys found in the CSV file")
                else:
                    # Validate the keys
                    validation_results = validate_keys_bulk(api_keys)

                    # Store the results in session state
                    st.session_state.bulk_validation_results = validation_results

                    # Create a downloadable CSV file
                    filename, csv_data = CSVProcessor.create_results_csv(api_keys)
                    st.download_button(
                        label="Download Results CSV",
                        data=csv_data,
                        file_name=filename,
                        mime="text/csv"
                    )

        # Display validation results
        if "bulk_validation_results" in st.session_state:
            results = st.session_state.bulk_validation_results

            st.markdown(f"### Validation Results ({len(results)} keys)")

            # Create tabs for valid and invalid keys
            valid_keys = [r for r in results if r["is_valid"]]
            invalid_keys = [r for r in results if not r["is_valid"]]

            tabs = st.tabs([f"Valid Keys ({len(valid_keys)})", f"Invalid Keys ({len(invalid_keys)})"])

            with tabs[0]:
                for result in valid_keys:
                    with st.expander(f"{result['provider']} - {result['api_key'][:10]}..."):
                        display_quota_info(result)

            with tabs[1]:
                for result in invalid_keys:
                    with st.expander(f"{result['provider']} - {result['api_key'][:10]}..."):
                        st.error(result["message"])
