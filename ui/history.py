"""
Validation history page for LLM API Key Validator.
"""

import streamlit as st
from typing import Dict, Any, List

from utils.storage import Storage


def create_history_page():
    """Create the validation history page."""
    st.markdown('<h1 class="main-header">Validation History</h1>', unsafe_allow_html=True)
    
    # Load validation history
    history = Storage.load_history()
    
    if not history:
        st.info("No validation history found")
    else:
        # Group history by provider
        providers = set(record["provider"] for record in history)
        
        # Create tabs for each provider
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
