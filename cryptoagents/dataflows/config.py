from typing import Dict, Optional
import os

# Import from the main config module
from ..config import CRYPTO_CONFIG as DEFAULT_CONFIG

# Use default config but allow it to be overridden
_config: Optional[Dict] = None
DATA_DIR: Optional[str] = None


def initialize_config():
    """Initialize the configuration with default values."""
    global _config, DATA_DIR
    if _config is None:
        _config = DEFAULT_CONFIG.copy()
        DATA_DIR = _config.get("data_dir", os.path.join(os.path.dirname(__file__), "..", "crypto_data"))


def set_config(config: Dict):
    """Update the configuration with custom values."""
    global _config, DATA_DIR
    if _config is None:
        _config = DEFAULT_CONFIG.copy()
    _config.update(config)
    DATA_DIR = _config.get("data_dir", os.path.join(os.path.dirname(__file__), "..", "crypto_data"))


def get_config() -> Dict:
    """Get the current configuration."""
    if _config is None:
        initialize_config()
    return _config.copy()


# Initialize with default config
initialize_config()
