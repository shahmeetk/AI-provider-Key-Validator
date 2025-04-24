"""
Validation history page for LLM API Key Validator.
"""

import streamlit as st
from typing import Dict, Any, List
import datetime

# Initialize session state for history if it doesn't exist
if "validation_history" not in st.session_state:
    st.session_state.validation_history = []

def add_to_history(validation_result: Dict[str, Any]):
    """Add a validation result to the session history.

    Args:
        validation_result: The validation result to add
    """
    # Add timestamp
    result_with_timestamp = validation_result.copy()
    result_with_timestamp["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Add to session state
    st.session_state.validation_history.append(result_with_timestamp)

def create_history_page():
    """Create the validation history page."""
    st.markdown('<h1 class="main-header">Validation History</h1>', unsafe_allow_html=True)

    # Add disclaimer
    st.info("**Disclaimer:** Validation history is only stored in your current browser session and will be cleared when you close the browser or refresh the page. No data is stored on our servers.")

    # Get history from session state
    history = st.session_state.validation_history

    if not history:
        st.info("No validation history found in current session")
    else:
        # Add clear history button
        if st.button("Clear History"):
            st.session_state.validation_history = []
            st.experimental_rerun()

        # Group history by provider
        providers = set(record["provider"] for record in history)

        # Create tabs for each provider
        if providers:
            tabs = st.tabs([p.capitalize() for p in providers] + ["All"])

            for i, provider in enumerate(list(providers) + ["all"]):
                with tabs[i]:
                    if provider == "all":
                        provider_history = history
                    else:
                        provider_history = [r for r in history if r["provider"] == provider]

                    # Display history
                    for record in provider_history:
                        with st.expander(f"{record['provider'].capitalize()} - {record['timestamp']}"):
                            st.markdown(f"**Status:** {'Valid' if record['is_valid'] else 'Invalid'}")
                            st.markdown(f"**Message:** {record['message']}")

                            if record["is_valid"] and "summary" in record:
                                st.markdown("### Account Summary")
                                for key, value in record["summary"].items():
                                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
