"""Main Streamlit application for LLM API Key Validator."""

import streamlit as st

from utils.storage import Storage, ProviderInfo
from ui.single_key import create_single_key_page
from ui.bulk_validation import create_bulk_validation_page
from ui.history import create_history_page
from ui.provider_info import create_provider_info_page


class MainApp:
    """Main Streamlit application class."""

    def __init__(self):
        """Initialize the application."""
        self.setup_page()
        self.load_data()
        self.create_sidebar()
        self.create_main_content()

    def setup_page(self):
        """Set up the page configuration."""
        st.set_page_config(
            page_title="LLM API Key Validator",
            page_icon="🔑",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Add custom CSS for a modern, tech-friendly UI
        st.markdown("""
        <style>
        /* Base styles */
        .stApp {
            background-color: #f8f9fa;
            color: #212529;
        }
        .main .block-container {
            padding-top: 2rem;
        }

        /* Typography */
        h1, h2, h3 {
            color: #0d6efd;
            font-weight: 600;
        }
        .main-header {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            color: #0d6efd;
        }
        .sub-header {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #0d6efd;
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #e9ecef;
            border-radius: 4px 4px 0 0;
            padding: 10px 20px;
            border: none;
        }
        .stTabs [aria-selected="true"] {
            background-color: #ffffff;
            border-bottom: 2px solid #0d6efd;
        }

        /* Button styling */
        .stButton>button {
            background-color: #0d6efd;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            transition: all 0.2s ease;
        }
        .stButton>button:hover {
            background-color: #0b5ed7;
            box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
        }

        /* Card styling */
        .info-card {
            background-color: #ffffff;
            border-radius: 0.5rem;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
            border-left: 4px solid #0d6efd;
        }
        .info-card h4 {
            color: #0d6efd;
            margin-top: 0;
        }

        /* Provider info styling */
        .provider-info {
            background-color: #e9ecef;
            border-radius: 0.5rem;
            padding: 1rem;
        }

        /* Text colors */
        .success-text {
            color: #28a745;
        }
        .error-text {
            color: #dc3545;
        }
        .warning-text {
            color: #ffc107;
        }

        /* Sidebar styling */
        .css-1d391kg {
            background-color: #ffffff;
            border-right: 1px solid #e9ecef;
        }

        /* Input fields */
        .stTextInput>div>div>input {
            border-radius: 4px;
            border: 1px solid #ced4da;
        }
        .stTextInput>div>div>input:focus {
            border-color: #0d6efd;
            box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
        }

        /* File uploader */
        .stFileUploader>div>button {
            background-color: #0d6efd;
            color: white;
        }

        /* Expander */
        .streamlit-expanderHeader {
            font-weight: 600;
            color: #0d6efd;
        }
        </style>
        """, unsafe_allow_html=True)

    def load_data(self):
        """Load application data."""
        # Initialize session state
        if "validation_history" not in st.session_state:
            st.session_state.validation_history = Storage.load_history()

        if "provider_info" not in st.session_state:
            st.session_state.provider_info = ProviderInfo.load_provider_info()

        if "current_tab" not in st.session_state:
            st.session_state.current_tab = "single"

    def create_sidebar(self):
        """Create the sidebar."""
        with st.sidebar:
            # Use our custom logo
            try:
                st.image("static/logo.svg", width=150)
            except Exception:
                # Fallback to emoji if logo file is not found
                st.markdown("# 🔑")
            st.markdown("## LLM API Key Validator")
            st.markdown("Validate and manage your LLM API keys")

            # Navigation
            st.markdown("### Navigation")
            if st.button("Single Key Validation", use_container_width=True):
                st.session_state.current_tab = "single"
                st.rerun()

            if st.button("Bulk Validation", use_container_width=True):
                st.session_state.current_tab = "bulk"
                st.rerun()

            if st.button("Validation History", use_container_width=True):
                st.session_state.current_tab = "history"
                st.rerun()

            if st.button("Provider Info", use_container_width=True):
                st.session_state.current_tab = "info"
                st.rerun()

            # Settings
            st.markdown("### Settings")
            if st.button("Clear History", use_container_width=True):
                Storage.clear_history()
                st.session_state.validation_history = []
                st.success("Validation history cleared")

            # About
            st.markdown("### About")
            st.markdown("""
            LLM API Key Validator is an open-source tool for validating and managing API keys for various LLM providers.

            [GitHub Repository](https://github.com/yourusername/llm-api-key-validator)
            """)

    def create_main_content(self):
        """Create the main content based on the current tab."""
        if st.session_state.current_tab == "single":
            create_single_key_page()
        elif st.session_state.current_tab == "bulk":
            create_bulk_validation_page()
        elif st.session_state.current_tab == "history":
            create_history_page()
        elif st.session_state.current_tab == "info":
            create_provider_info_page()


def main():
    """Main entry point for the application."""
    MainApp()


if __name__ == "__main__":
    main()
