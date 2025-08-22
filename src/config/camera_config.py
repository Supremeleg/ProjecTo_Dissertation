# -*- coding: utf-8 -*-
"""
Camera Configuration Module
"""

import json
from pathlib import Path

class CameraConfig:
    """Camera configuration class"""
    
    # Default configuration
    DEFAULT_CONFIG = {
        "camera_index": 0,
        "width": 320,
        "height": 240,
        "fps": 30,
        "auto_exposure": False,
        "exposure": -6,
        "brightness": 50,
        "contrast": 50,
        "saturation": 50,
        "buffer_size": 1,
        "flip_horizontal": False,
        "flip_vertical": False,
    }
    
    def __init__(self, config_file=None):
        """Initialize camera configuration"""
        self.config_file = config_file or Path(__file__).parent.parent.parent / "config" / "camera_config.json"
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self.config.update(file_config)
                print(f"Camera configuration loaded: {self.config_file}")
            else:
                print(f"Camera configuration file does not exist, using default configuration: {self.config_file}")
                self.save_config()  # Save default configuration
        except Exception as e:
            print(f"Failed to load camera configuration, using default configuration: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"Camera configuration saved: {self.config_file}")
        except Exception as e:
            print(f"Failed to save camera configuration: {e}")
    
    def get(self, key, default=None):
        """Get configuration item"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration item"""
        self.config[key] = value
    
    def update(self, **kwargs):
        """Batch update configuration"""
        self.config.update(kwargs)
    
    @property
    def camera_index(self):
        return self.config["camera_index"]
    
    @property
    def width(self):
        return self.config["width"]
    
    @property
    def height(self):
        return self.config["height"]
    
    @property
    def fps(self):
        return self.config["fps"]
    
    @property
    def resolution(self):
        return (self.width, self.height)
    
    def print_config(self):
        """Print configuration information"""
        print("=== Camera Configuration ===")
        for key, value in self.config.items():
            print(f"{key}: {value}")
        print("================")
