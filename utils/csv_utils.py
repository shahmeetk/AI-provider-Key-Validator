"""
CSV utilities for LLM API Key Validator.
"""

import csv
import io
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple

from core.api_key import APIKey, Provider, create_api_key
from utils.detection import ProviderDetector
from utils.logger import app_logger


class CSVProcessor:
    """Processor for CSV files containing API keys."""
    
    @staticmethod
    def parse_csv(csv_data: bytes) -> List[APIKey]:
        """
        Parse a CSV file containing API keys.
        
        Args:
            csv_data: The CSV file data
            
        Returns:
            A list of APIKey instances
        """
        try:
            # Convert bytes to string
            csv_string = csv_data.decode("utf-8")
            
            # Read the CSV data
            df = pd.read_csv(io.StringIO(csv_string))
            
            # Check if the required columns exist
            if "api_key" not in df.columns:
                if len(df.columns) >= 1:
                    # Assume the first column contains API keys
                    df = df.rename(columns={df.columns[0]: "api_key"})
                else:
                    app_logger.error("CSV file does not contain any columns")
                    return []
            
            # Check if the provider column exists
            has_provider_column = "provider" in df.columns
            
            # Create APIKey instances
            api_keys = []
            for _, row in df.iterrows():
                api_key_str = row["api_key"].strip()
                
                if not api_key_str:
                    continue
                
                if has_provider_column and row["provider"]:
                    # Use the specified provider
                    try:
                        provider = Provider(row["provider"].lower())
                        api_key = create_api_key(provider, api_key_str)
                    except ValueError:
                        # Invalid provider, try to detect
                        api_key = ProviderDetector.detect_provider(api_key_str)
                else:
                    # Try to detect the provider
                    api_key = ProviderDetector.detect_provider(api_key_str)
                
                if api_key:
                    api_keys.append(api_key)
            
            return api_keys
        
        except Exception as e:
            app_logger.error(f"Error parsing CSV: {str(e)}")
            return []
    
    @staticmethod
    def create_results_csv(api_keys: List[APIKey]) -> Tuple[str, bytes]:
        """
        Create a CSV file with validation results.
        
        Args:
            api_keys: The validated API keys
            
        Returns:
            A tuple containing the filename and CSV data
        """
        try:
            # Create a list of dictionaries for the results
            results = []
            for api_key in api_keys:
                result = {
                    "provider": api_key.provider.value,
                    "api_key": api_key.api_key,
                    "is_valid": api_key.is_valid,
                    "message": api_key.message,
                }
                
                # Add provider-specific information
                if api_key.is_valid and api_key.quota_info:
                    if "account_summary" in api_key.quota_info:
                        for key, value in api_key.quota_info["account_summary"].items():
                            result[f"summary_{key}"] = value
                    
                    if "model_count" in api_key.quota_info:
                        result["model_count"] = api_key.quota_info["model_count"]
                
                results.append(result)
            
            # Create a DataFrame from the results
            df = pd.DataFrame(results)
            
            # Convert the DataFrame to CSV
            csv_data = df.to_csv(index=False).encode("utf-8")
            
            # Create a filename with timestamp
            filename = f"validation_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            return filename, csv_data
        
        except Exception as e:
            app_logger.error(f"Error creating results CSV: {str(e)}")
            return "error.csv", b"Error creating results CSV"
