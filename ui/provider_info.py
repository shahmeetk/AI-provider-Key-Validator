"""
Provider information page for LLM API Key Validator.
"""

import streamlit as st
from typing import Dict, Any

from utils.storage import ProviderInfo


def display_provider_info():
    """Display provider information."""
    st.markdown('<h1 class="main-header">Provider Information</h1>', unsafe_allow_html=True)
    
    # Load provider info
    provider_info = ProviderInfo.load_provider_info()
    
    # Create tabs for each category
    categories = provider_info["categories"]
    tabs = st.tabs([categories[c]["name"] for c in categories])
    
    for i, category_key in enumerate(categories):
        category = categories[category_key]
        
        with tabs[i]:
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


def create_provider_info_page():
    """Create the provider info page."""
    display_provider_info()
