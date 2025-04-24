"""Logging utilities for LLM API Key Validator."""

import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure the logger
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

# Create a logger instance
app_logger = logging.getLogger("llm_api_key_validator")


class LoggerManager:
    """Manager for application logging."""

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Get a logger with the specified name.

        Args:
            name: The name of the logger

        Returns:
            A logger instance
        """
        return logging.getLogger(name)

    @staticmethod
    def set_level(level: int) -> None:
        """
        Set the logging level.

        Args:
            level: The logging level (e.g., logging.INFO, logging.DEBUG)
        """
        app_logger.setLevel(level)
        for handler in app_logger.handlers:
            handler.setLevel(level)

    @staticmethod
    def add_file_handler(filename: str) -> None:
        """
        Add a file handler to the logger.

        Args:
            filename: The name of the log file
        """
        handler = logging.FileHandler(filename)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        app_logger.addHandler(handler)
