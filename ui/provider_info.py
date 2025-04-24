"""
Provider information page for LLM API Key Validator.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List

from utils.storage import ProviderInfo


def display_provider_info():
    """Display provider information."""
    st.markdown('<h1 class="main-header">Provider Information</h1>', unsafe_allow_html=True)

    # Add disclaimer
    st.info("**Disclaimer:** This information is provided for reference only. API keys are never stored or cached on our servers. All validation is done in your browser session and keys are not retained after validation.")

    # Load provider info
    provider_info = ProviderInfo.load_provider_info()

    # Create tabs for different views
    tabs = st.tabs(["By Category", "Comparison Table", "Detailed View"])

    # Tab 1: By Category
    with tabs[0]:
        # Create tabs for each category
        categories = provider_info["categories"]
        category_tabs = st.tabs([categories[c]["name"] for c in categories])

        for i, category_key in enumerate(categories):
            category = categories[category_key]

            with category_tabs[i]:
                st.markdown(f"### {category['name']}")
                st.markdown(category["description"])

                # Display providers in this category
                for provider_key in category["providers"]:
                    if provider_key in provider_info["providers"]:
                        provider = provider_info["providers"][provider_key]

                        with st.expander(provider["name"]):
                            # Create two columns
                            col1, col2 = st.columns([2, 1])

                            with col1:
                                st.markdown(f"**Description:** {provider['description']}")
                                st.markdown(f"**Free Tier:** {'Yes' if provider['free_tier'] else 'No'}")
                                st.markdown(f"**Credit Card Required:** {'Yes' if provider['credit_card_required'] else 'No'}")
                                st.markdown(f"**Key Format:** {provider['key_format']}")
                                st.markdown(f"**Rate Limit:** {provider['rate_limit']}")
                                st.markdown(f"**Token Limit:** {provider['token_limit']}")

                                if "featured_models" in provider:
                                    st.markdown("**Featured Models:**")
                                    for model in provider["featured_models"]:
                                        st.markdown(f"- {model}")

                            with col2:
                                st.markdown("**Links:**")
                                st.markdown(f"[Website]({provider['website']})")
                                st.markdown(f"[Sign Up]({provider['signup_url']})")
                                st.markdown(f"[Pricing]({provider['pricing_url']})")
                                st.markdown(f"[Documentation]({provider['docs_url']})")

    # Tab 2: Comparison Table
    with tabs[1]:
        st.markdown("### Provider Comparison")
        st.markdown("Compare features across different LLM providers")

        # Create comparison dataframe
        comparison_data = []

        for provider_key, provider in provider_info["providers"].items():
            comparison_data.append({
                "Provider": provider["name"],
                "Free Tier": "✅" if provider["free_tier"] else "❌",
                "Credit Card Required": "Yes" if provider["credit_card_required"] else "No",
                "Rate Limit": provider["rate_limit"],
                "Token Limit": provider["token_limit"],
                "Key Format": provider["key_format"],
                "Featured Models": ", ".join(provider.get("featured_models", [])[:2]) + ("..." if len(provider.get("featured_models", [])) > 2 else "")
            })

        # Convert to dataframe and display
        df = pd.DataFrame(comparison_data)

        # Add filtering options
        st.markdown("#### Filter Providers")
        col1, col2 = st.columns(2)
        with col1:
            show_free_only = st.checkbox("Show Free Tier Only")
        with col2:
            show_no_cc_only = st.checkbox("Show No Credit Card Required Only")

        # Apply filters
        filtered_df = df
        if show_free_only:
            filtered_df = filtered_df[filtered_df["Free Tier"] == "✅"]
        if show_no_cc_only:
            filtered_df = filtered_df[filtered_df["Credit Card Required"] == "No"]

        # Display the table
        st.dataframe(filtered_df, use_container_width=True)

    # Tab 3: Detailed View
    with tabs[2]:
        st.markdown("### Detailed Provider Information")

        # Create a selectbox to choose a provider
        provider_names = [provider_info["providers"][p]["name"] for p in provider_info["providers"]]
        provider_keys = list(provider_info["providers"].keys())
        selected_provider_name = st.selectbox("Select a provider", provider_names)

        # Get the selected provider
        selected_provider_idx = provider_names.index(selected_provider_name)
        selected_provider_key = provider_keys[selected_provider_idx]
        provider = provider_info["providers"][selected_provider_key]

        # Display provider details
        st.markdown(f"## {provider['name']}")
        st.markdown(f"**Description:** {provider['description']}")

        # Create columns for details
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### Features")
            st.markdown(f"**Free Tier:** {'Yes' if provider['free_tier'] else 'No'}")
            st.markdown(f"**Credit Card Required:** {'Yes' if provider['credit_card_required'] else 'No'}")
            st.markdown(f"**Key Format:** {provider['key_format']}")
            st.markdown(f"**Rate Limit:** {provider['rate_limit']}")
            st.markdown(f"**Token Limit:** {provider['token_limit']}")

        with col2:
            st.markdown("### Links")
            st.markdown(f"[Website]({provider['website']})")
            st.markdown(f"[Sign Up]({provider['signup_url']})")
            st.markdown(f"[Pricing]({provider['pricing_url']})")
            st.markdown(f"[Documentation]({provider['docs_url']})")

        # Display featured models
        if "featured_models" in provider:
            st.markdown("### Featured Models")
            for model in provider["featured_models"]:
                st.markdown(f"- {model}")

        # Display how to get API key
        st.markdown("### How to Get API Key")
        if provider["free_tier"]:
            st.markdown(f"""
            1. Visit the [Sign Up]({provider['signup_url']}) page
            2. Create an account (no credit card required)
            3. Navigate to the API section or dashboard
            4. Generate a new API key
            """)
        else:
            st.markdown(f"""
            1. Visit the [Sign Up]({provider['signup_url']}) page
            2. Create an account (credit card required)
            3. Select a payment plan
            4. Navigate to the API section or dashboard
            5. Generate a new API key
            """)


def create_provider_info_page():
    """Create the provider info page."""
    display_provider_info()
