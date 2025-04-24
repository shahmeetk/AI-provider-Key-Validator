#!/bin/bash
# LLM API Key Validator - Runner Script

# Default values
PORT=8501
VENV_PATH=".venv"
SKIP_VENV=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --port)
      PORT="$2"
      shift 2
      ;;
    --venv)
      VENV_PATH="$2"
      shift 2
      ;;
    --skip-venv)
      SKIP_VENV=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Make the script executable
chmod +x run.py

# Run the Python script with the parsed arguments
if [ "$SKIP_VENV" = true ]; then
  ./run.py --port "$PORT" --skip-venv
else
  ./run.py --port "$PORT" --venv "$VENV_PATH"
fi
