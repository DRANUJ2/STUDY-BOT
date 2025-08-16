import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dotenv import load_dotenv

class ConfigParser:
    """Configuration parser for multiple file formats"""
    
    def __init__(self, config_dir: str = "."):
        """
        Initialize config parser
        
        Args:
            config_dir (str): Directory containing config files
        """
        self.config_dir = Path(config_dir)
        self.config_cache = {}
        self.env_loaded = False
    
    def load_env(self, env_file: str = ".env") -> bool:
        """
        Load environment variables from .env file
        
        Args:
            env_file (str): Environment file name
            
        Returns:
            bool: True if loaded successfully
        """
        env_path = self.config_dir / env_file
        
        if env_path.exists():
            load_dotenv(env_path)
            self.env_loaded = True
            return True
        
        return False
    
    def get_env(self, key: str, default: Any = None) -> Any:
        """
        Get environment variable
        
        Args:
            key (str): Environment variable name
            default (Any): Default value if not found
            
        Returns:
            Any: Environment variable value
        """
        return os.getenv(key, default)
    
    def load_json(self, filename: str) -> Dict[str, Any]:
        """
        Load JSON configuration file
        
        Args:
            filename (str): JSON file name
            
        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        file_path = self.config_dir / filename
        
        if not file_path.exists():
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.config_cache[filename] = config
                return config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading JSON config {filename}: {e}")
            return {}
    
    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """
        Load YAML configuration file
        
        Args:
            filename (str): YAML file name
            
        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        file_path = self.config_dir / filename
        
        if not file_path.exists():
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self.config_cache[filename] = config
                return config
        except (yaml.YAMLError, IOError) as e:
            print(f"Error loading YAML config {filename}: {e}")
            return {}
    
    def load_config(self, filename: str) -> Dict[str, Any]:
        """
        Load configuration file based on extension
        
        Args:
            filename (str): Configuration file name
            
        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        # Check cache first
        if filename in self.config_cache:
            return self.config_cache[filename]
        
        file_path = Path(filename)
        extension = file_path.suffix.lower()
        
        if extension == '.json':
            return self.load_json(filename)
        elif extension in ['.yml', '.yaml']:
            return self.load_yaml(filename)
        else:
            # Try to determine format by content
            return self._auto_detect_format(filename)
    
    def _auto_detect_format(self, filename: str) -> Dict[str, Any]:
        """
        Auto-detect configuration file format
        
        Args:
            filename (str): Configuration file name
            
        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        file_path = self.config_dir / filename
        
        if not file_path.exists():
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
                # Try JSON first
                try:
                    config = json.loads(content)
                    self.config_cache[filename] = config
                    return config
                except json.JSONDecodeError:
                    pass
                
                # Try YAML
                try:
                    config = yaml.safe_load(content)
                    self.config_cache[filename] = config
                    return config
                except yaml.YAMLError:
                    pass
                
                # Try as key-value pairs
                return self._parse_key_value(content)
                
        except IOError as e:
            print(f"Error reading config file {filename}: {e}")
            return {}
    
    def _parse_key_value(self, content: str) -> Dict[str, Any]:
        """
        Parse key-value configuration format
        
        Args:
            content (str): Configuration content
            
        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        config = {}
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse key=value format
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                
                # Try to convert value types
                if value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                elif value.replace('.', '').isdigit() and value.count('.') == 1:
                    value = float(value)
                
                config[key] = value
        
        return config
    
    def get(self, key: str, default: Any = None, config_file: Optional[str] = None) -> Any:
        """
        Get configuration value
        
        Args:
            key (str): Configuration key
            default (Any): Default value if not found
            config_file (str, optional): Specific config file to search
            
        Returns:
            Any: Configuration value
        """
        # Try environment variables first
        env_value = self.get_env(key)
        if env_value is not None:
            return env_value
        
        # Try specific config file
        if config_file:
            config = self.load_config(config_file)
            return config.get(key, default)
        
        # Try all cached configs
        for config in self.config_cache.values():
            if key in config:
                return config[key]
        
        return default
    
    def get_nested(self, key_path: str, default: Any = None, config_file: Optional[str] = None) -> Any:
        """
        Get nested configuration value using dot notation
        
        Args:
            key_path (str): Dot-separated key path (e.g., 'database.host')
            default (Any): Default value if not found
            config_file (str, optional): Specific config file to search
            
        Returns:
            Any: Configuration value
        """
        keys = key_path.split('.')
        
        # Try environment variables first
        env_key = key_path.upper().replace('.', '_')
        env_value = self.get_env(env_key)
        if env_value is not None:
            return env_value
        
        # Try specific config file
        if config_file:
            config = self.load_config(config_file)
            value = config
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            return value
        
        # Try all cached configs
        for config in self.config_cache.values():
            value = config
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    break
            else:
                return value
        
        return default
    
    def set(self, key: str, value: Any, config_file: str) -> bool:
        """
        Set configuration value
        
        Args:
            key (str): Configuration key
            value (Any): Configuration value
            config_file (str): Config file to update
            
        Returns:
            bool: True if updated successfully
        """
        try:
            config = self.load_config(config_file)
            config[key] = value
            
            file_path = self.config_dir / config_file
            extension = file_path.suffix.lower()
            
            if extension == '.json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
            elif extension in ['.yml', '.yaml']:
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            else:
                # Update cache only for unsupported formats
                self.config_cache[config_file] = config
            
            return True
            
        except Exception as e:
            print(f"Error setting config value: {e}")
            return False
    
    def reload(self, config_file: Optional[str] = None) -> bool:
        """
        Reload configuration files
        
        Args:
            config_file (str, optional): Specific config file to reload
            
        Returns:
            bool: True if reloaded successfully
        """
        try:
            if config_file:
                if config_file in self.config_cache:
                    del self.config_cache[config_file]
                self.load_config(config_file)
            else:
                self.config_cache.clear()
                # Reload all config files in directory
                for file_path in self.config_dir.glob("*"):
                    if file_path.suffix.lower() in ['.json', '.yml', '.yaml', '.env']:
                        if file_path.name == '.env':
                            self.load_env()
                        else:
                            self.load_config(file_path.name)
            
            return True
            
        except Exception as e:
            print(f"Error reloading config: {e}")
            return False
    
    def list_configs(self) -> list:
        """
        List available configuration files
        
        Returns:
            list: List of configuration file names
        """
        configs = []
        for file_path in self.config_dir.glob("*"):
            if file_path.suffix.lower() in ['.json', '.yml', '.yaml', '.env']:
                configs.append(file_path.name)
        return configs
    
    def validate_config(self, config_file: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration against schema
        
        Args:
            config_file (str): Configuration file name
            schema (Dict[str, Any]): Validation schema
            
        Returns:
            Dict[str, Any]: Validation results
        """
        config = self.load_config(config_file)
        errors = []
        warnings = []
        
        def validate_section(config_section, schema_section, path=""):
            for key, schema_info in schema_section.items():
                current_path = f"{path}.{key}" if path else key
                
                if key not in config_section:
                    if schema_info.get('required', False):
                        errors.append(f"Missing required key: {current_path}")
                    continue
                
                value = config_section[key]
                expected_type = schema_info.get('type')
                
                if expected_type and not isinstance(value, expected_type):
                    errors.append(f"Invalid type for {current_path}: expected {expected_type.__name__}, got {type(value).__name__}")
                
                if 'min' in schema_info and value < schema_info['min']:
                    errors.append(f"Value too small for {current_path}: {value} < {schema_info['min']}")
                
                if 'max' in schema_info and value > schema_info['max']:
                    errors.append(f"Value too large for {current_path}: {value} > {schema_info['max']}")
                
                if 'choices' in schema_info and value not in schema_info['choices']:
                    errors.append(f"Invalid value for {current_path}: {value} not in {schema_info['choices']}")
                
                if 'nested' in schema_info and isinstance(value, dict):
                    validate_section(value, schema_info['nested'], current_path)
        
        validate_section(config, schema)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

# Global config parser instance
config_parser = ConfigParser()

def get_config(key: str, default: Any = None) -> Any:
    """
    Convenience function to get configuration value
    
    Args:
        key (str): Configuration key
        default (Any): Default value if not found
        
    Returns:
        Any: Configuration value
    """
    return config_parser.get(key, default)

def get_nested_config(key_path: str, default: Any = None) -> Any:
    """
    Convenience function to get nested configuration value
    
    Args:
        key_path (str): Dot-separated key path
        default (Any): Default value if not found
        
    Returns:
        Any: Configuration value
    """
    return config_parser.get_nested(key_path, default)

def load_config_file(filename: str) -> Dict[str, Any]:
    """
    Convenience function to load configuration file
    
    Args:
        filename (str): Configuration file name
        
    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    return config_parser.load_config(filename)
