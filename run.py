#!/usr/bin/env python3
"""LLM API Key Validator - Runner Script

Sets up a virtual environment, installs dependencies, and runs the Streamlit application.
"""

import os
import sys
import subprocess
import platform
import argparse

def is_venv():
    """Check if running inside a virtual environment"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def create_venv(venv_path):
    """Create a virtual environment at the specified path"""
    print(f"Creating virtual environment at {venv_path}...")
    subprocess.check_call([sys.executable, "-m", "venv", venv_path])
    print("Virtual environment created successfully.")

def get_venv_python(venv_path):
    """Get the path to the Python executable in the virtual environment"""
    if platform.system() == "Windows":
        return os.path.join(venv_path, "Scripts", "python.exe")
    else:
        return os.path.join(venv_path, "bin", "python")

def get_venv_pip(venv_path):
    """Get the path to the pip executable in the virtual environment"""
    if platform.system() == "Windows":
        return os.path.join(venv_path, "Scripts", "pip.exe")
    else:
        return os.path.join(venv_path, "bin", "pip")

def install_requirements(venv_path):
    """Install requirements in the virtual environment"""
    pip_path = get_venv_pip(venv_path)
    requirements_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")

    print("Installing requirements...")
    subprocess.check_call([pip_path, "install", "-r", requirements_path])
    print("Requirements installed successfully.")

def run_streamlit(venv_path, port=8501):
    """Run the Streamlit application"""
    main_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")

    print(f"Starting Streamlit server on port {port}...")

    if venv_path:
        # Use the Python from the virtual environment
        python_path = get_venv_python(venv_path)
        subprocess.check_call([
            python_path, "-m", "streamlit", "run", main_path,
            "--server.port", str(port),
            "--server.headless", "true"
        ])
    else:
        # Use the current Python interpreter
        subprocess.check_call([
            sys.executable, "-m", "streamlit", "run", main_path,
            "--server.port", str(port),
            "--server.headless", "true"
        ])

def main():
    """Main function to set up environment and run the app"""
    parser = argparse.ArgumentParser(description="Run the LLM API Key Validator app")
    parser.add_argument("--port", type=int, default=8501, help="Port to run Streamlit on (default: 8501)")
    parser.add_argument("--venv", type=str, default=".venv", help="Path to virtual environment (default: .venv)")
    parser.add_argument("--skip-venv", action="store_true", help="Skip virtual environment setup")
    args = parser.parse_args()

    venv_path = os.path.abspath(args.venv)

    if args.skip_venv:
        print("Skipping virtual environment setup...")
        run_streamlit(None, args.port)
        return

    # Check if we're already in a virtual environment
    if is_venv():
        print("Already running in a virtual environment.")
        run_streamlit(None, args.port)
        return

    # Create virtual environment if it doesn't exist
    if not os.path.exists(venv_path):
        create_venv(venv_path)
        install_requirements(venv_path)
    else:
        print(f"Using existing virtual environment at {venv_path}")

    # Run the Streamlit app
    run_streamlit(venv_path, args.port)

if __name__ == "__main__":
    main()
