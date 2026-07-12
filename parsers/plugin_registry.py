"""
Plugin Registry & Auto-Discovery
==================================
Automatically discovers all language plugins in the parsers/ directory.
Implements the Factory Pattern for plugin instantiation.

Design Pattern: Registry + Factory
"""

import os
import importlib
import inspect
from typing import Optional
from loguru import logger

from parsers.base_plugin import BaseLanguagePlugin


class PluginRegistry:
    """
    Singleton registry that auto-discovers and manages language plugins.
    
    Discovery mechanism:
    - Scans parsers/<language>/ subdirectories
    - Imports plugin.py from each
    - Registers classes that inherit from BaseLanguagePlugin
    """
    
    _instance: Optional['PluginRegistry'] = None
    
    def __init__(self):
        self._plugins: dict[str, BaseLanguagePlugin] = {}  # language → plugin instance
        self._ext_map: dict[str, str] = {}                  # extension → language
    
    @classmethod
    def get_instance(cls) -> 'PluginRegistry':
        """Return the singleton registry instance."""
        if cls._instance is None:
            cls._instance = cls()
            cls._instance.discover_plugins()
        return cls._instance
    
    def discover_plugins(self) -> None:
        """
        Scan parsers/ subdirectories and load all language plugins.
        Called once at startup.
        """
        parsers_dir = os.path.dirname(os.path.abspath(__file__))
        logger.info(f"Discovering plugins in: {parsers_dir}")
        
        for entry in os.scandir(parsers_dir):
            if not entry.is_dir():
                continue
            plugin_file = os.path.join(entry.path, 'plugin.py')
            if not os.path.isfile(plugin_file):
                continue
            
            try:
                self._load_plugin_from_dir(entry.name, entry.path)
            except Exception as e:
                logger.warning(f"Failed to load plugin from {entry.path}: {e}")
        
        logger.info(f"Loaded {len(self._plugins)} language plugins: {list(self._plugins.keys())}")
    
    def _load_plugin_from_dir(self, dir_name: str, dir_path: str) -> None:
        """Import plugin.py from a plugin directory and register its plugin class."""
        # Build module path relative to project root
        module_path = f"parsers.{dir_name}.plugin"
        
        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            logger.warning(f"Could not import {module_path}: {e}")
            return
        
        # Find BaseLanguagePlugin subclasses in the module
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (issubclass(obj, BaseLanguagePlugin) 
                and obj is not BaseLanguagePlugin
                and not inspect.isabstract(obj)):
                try:
                    instance = obj()
                    self.register(instance)
                    logger.debug(f"Registered plugin: {instance.language} ({name})")
                except Exception as e:
                    logger.warning(f"Could not instantiate {name}: {e}")
    
    def register(self, plugin: BaseLanguagePlugin) -> None:
        """Manually register a plugin instance."""
        lang = plugin.language
        self._plugins[lang] = plugin
        for ext in plugin.file_extensions:
            self._ext_map[ext.lower()] = lang
    
    def get_plugin(self, language: str) -> Optional[BaseLanguagePlugin]:
        """Get plugin by language name (case-insensitive)."""
        # Try exact match
        plugin = self._plugins.get(language)
        if plugin:
            return plugin
        # Try case-insensitive
        for lang, p in self._plugins.items():
            if lang.lower() == language.lower():
                return p
        return None
    
    def get_plugin_for_file(self, file_path: str) -> Optional[BaseLanguagePlugin]:
        """Get appropriate plugin for a file based on extension."""
        ext = os.path.splitext(file_path)[1].lower()
        lang = self._ext_map.get(ext)
        if lang:
            return self._plugins.get(lang)
        return None
    
    def get_all_languages(self) -> list[str]:
        """Return list of all registered language names."""
        return list(self._plugins.keys())
    
    def get_all_plugins(self) -> list[BaseLanguagePlugin]:
        """Return list of all registered plugin instances."""
        return list(self._plugins.values())
    
    def get_plugin_count(self) -> int:
        """Return number of registered plugins."""
        return len(self._plugins)
    
    def has_plugin(self, language: str) -> bool:
        """Check if a plugin is registered for the given language."""
        return self.get_plugin(language) is not None


class PluginFactory:
    """
    Factory for creating plugin instances on demand.
    Uses the PluginRegistry as the underlying source.
    """
    
    @staticmethod
    def create(language: str) -> Optional[BaseLanguagePlugin]:
        """
        Create (or return cached) plugin instance for a language.
        
        Args:
            language: Language name (e.g., 'Python', 'Java')
        
        Returns:
            Plugin instance or None if unsupported.
        """
        registry = PluginRegistry.get_instance()
        return registry.get_plugin(language)
    
    @staticmethod
    def create_for_file(file_path: str) -> Optional[BaseLanguagePlugin]:
        """Create plugin based on file extension."""
        registry = PluginRegistry.get_instance()
        return registry.get_plugin_for_file(file_path)
    
    @staticmethod
    def get_supported_languages() -> list[str]:
        """Return all supported language names."""
        return PluginRegistry.get_instance().get_all_languages()
