"""Configuration management for the framework"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import yaml

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for the framework"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration from file or environment variables"""
        self.config_path = config_path or Path(__file__).parent.parent.parent / "config.yaml"
        self.config = self._load_config()
        
        # API Keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        
        # Model configurations
        self.codellama_model = os.getenv("CODELLAMA_MODEL", "codellama:13b")
        self.chatgpt_model = os.getenv("CHATGPT_MODEL", "gpt-4")
        
        # LLM Router settings
        self.local_threshold = float(self.config.get("router", {}).get("local_threshold", 0.6))
        self.complexity_threshold = int(self.config.get("router", {}).get("complexity_threshold", 100))
        
        # Refinement settings
        self.max_iterations = int(self.config.get("refinement", {}).get("max_iterations", 5))
        self.convergence_threshold = float(self.config.get("refinement", {}).get("convergence_threshold", 0.95))
        
        # Verification settings
        self.enable_exploit_verification = self.config.get("verification", {}).get("enable_exploit", True)
        self.exploit_timeout = int(self.config.get("verification", {}).get("exploit_timeout", 30))
        
        # Performance settings
        self.parallel_workers = int(self.config.get("performance", {}).get("parallel_workers", 4))
        self.enable_caching = self.config.get("performance", {}).get("enable_caching", True)
        
    def _load_config(self) -> dict:
        """Load configuration from YAML file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value if value is not None else default


# Global configuration instance
config = Config()



