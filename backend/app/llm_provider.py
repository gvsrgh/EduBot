"""
Multi-Provider LLM Configuration Module

This module handles dynamic model selection between:
- OpenAI GPT-4
- Google Gemini
- Local Ollama models

Selection is controlled via user settings stored in localStorage.
"""

import os
from typing import Optional, Literal
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel

ProviderType = Literal["openai", "gemini", "ollama", "auto"]


class LLMProvider:
    """Manages dynamic LLM provider selection and fallback."""
    
    def __init__(self):
        self.current_provider: str = "ollama"  # Default to local
        self._api_keys = {
            'openai': None,
            'openai_model': 'gpt-4',
            'gemini': None,
            'gemini_model': 'gemini-2.0-flash-exp',
            'ollama_url': 'http://localhost:11434',
            'ollama_model': 'llama3.1:8b'
        }
    
    def set_api_keys(
        self, 
        openai_key: str = None, 
        openai_model: str = None,
        gemini_key: str = None,
        gemini_model: str = None,
        ollama_url: str = None,
        ollama_model: str = None
    ):
        """Set API keys and models dynamically from user settings."""
        if openai_key:
            self._api_keys['openai'] = openai_key
        if openai_model:
            self._api_keys['openai_model'] = openai_model
        if gemini_key:
            self._api_keys['gemini'] = gemini_key
        if gemini_model:
            self._api_keys['gemini_model'] = gemini_model
        if ollama_url:
            self._api_keys['ollama_url'] = ollama_url
        if ollama_model:
            self._api_keys['ollama_model'] = ollama_model
    
    def get_api_keys(self) -> dict:
        """Get current API keys."""
        return self._api_keys.copy()
        
    def get_llm(
        self,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_retries: int = 2
    ) -> BaseChatModel:
        """
        Get the LLM instance based on provider selection.
        
        Args:
            provider: Override the default AI_PROVIDER setting
            temperature: Model temperature (0.0 - 1.0)
            max_retries: Number of retry attempts on failure
            
        Returns:
            BaseChatModel: Configured LLM instance
            
        Raises:
            ValueError: If provider is invalid or credentials missing
        """
        provider = (provider or self.current_provider).lower()
        
        if provider == "auto":
            return self._get_auto_provider(temperature, max_retries)
        elif provider == "openai":
            return self._get_openai(temperature, max_retries)
        elif provider == "gemini":
            return self._get_gemini(temperature, max_retries)
        elif provider == "ollama":
            return self._get_ollama(temperature, max_retries)
        else:
            raise ValueError(
                f"Invalid AI provider: {provider}. "
                f"Must be one of: openai, gemini, ollama, auto"
            )
    
    def _get_openai(self, temperature: float, max_retries: int) -> ChatOpenAI:
        """Get OpenAI GPT-4 model."""
        api_key = self._api_keys.get('openai') or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not configured")
        
        model = self._api_keys.get('openai_model') or 'gpt-4'
        
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            max_retries=max_retries,
            openai_api_key=api_key,
        )
    
    def _get_gemini(self, temperature: float, max_retries: int) -> ChatGoogleGenerativeAI:
        """Get Google Gemini model."""
        api_key = self._api_keys.get('gemini') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not configured")
        
        model = self._api_keys.get('gemini_model') or 'gemini-2.0-flash-exp'
        
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            max_retries=max_retries,
            google_api_key=api_key,
        )
    
    def _get_ollama(self, temperature: float, max_retries: int) -> ChatOllama:
        """Get Ollama local model."""
        base_url = self._api_keys.get('ollama_url') or 'http://localhost:11434'
        model = self._api_keys.get('ollama_model') or 'llama3.1:8b'
        
        return ChatOllama(
            model=model,
            temperature=temperature,
            max_retries=max_retries,
            base_url=base_url,
        )
    
    def _get_auto_provider(self, temperature: float, max_retries: int) -> BaseChatModel:
        """
        Auto-select provider with fallback priority:
        1. University-provided API (from .env)
        2. User-provided API keys (from settings)
        3. Ollama (local fallback)
        """
        # Try university-provided OpenAI first
        env_openai = os.getenv('OPENAI_API_KEY')
        if env_openai:
            try:
                return self._get_openai(temperature, max_retries)
            except Exception as e:
                print(f"University OpenAI failed: {e}, trying other providers...")
        
        # Try user-provided OpenAI
        if self._api_keys.get('openai'):
            try:
                return self._get_openai(temperature, max_retries)
            except Exception as e:
                print(f"User OpenAI failed: {e}, trying Gemini...")
        
        # Try university-provided Gemini
        env_gemini = os.getenv('GOOGLE_API_KEY')
        if env_gemini:
            try:
                return self._get_gemini(temperature, max_retries)
            except Exception as e:
                print(f"University Gemini failed: {e}, trying other providers...")
        
        # Try user-provided Gemini
        if self._api_keys.get('gemini'):
            try:
                return self._get_gemini(temperature, max_retries)
            except Exception as e:
                print(f"User Gemini failed: {e}, trying Ollama...")
        
        # Fallback to Ollama (local)
        return self._get_ollama(temperature, max_retries)
    
    def set_provider(self, provider: str):
        """Update the current provider setting."""
        if provider.lower() not in ["openai", "gemini", "ollama", "auto"]:
            raise ValueError(f"Invalid provider: {provider}")
        self.current_provider = provider.lower()
    
    def get_current_provider(self) -> str:
        """Get the currently active provider."""
        return self.current_provider
    
    def supports_tools(self) -> bool:
        """Check if the current model supports tool/function calling."""
        provider = self.current_provider.lower()
        
        if provider == "openai":
            return True
        elif provider == "gemini":
            return True
        elif provider == "ollama":
            # Some Ollama models don't support tools
            model = self._api_keys.get('ollama_model', '').lower()
            # Known models without tool support
            non_tool_models = ['gemma', 'phi', 'tinyllama', 'stablelm']
            return not any(nm in model for nm in non_tool_models)
        elif provider == "auto":
            # Check the actual provider that would be selected
            return True  # Assume auto will pick a tool-capable model
        return False
    
    def get_available_providers(self) -> dict[str, bool]:
        """Check which providers are available based on configuration."""
        return {
            "openai": bool(self._api_keys.get('openai') or os.getenv('OPENAI_API_KEY')),
            "gemini": bool(self._api_keys.get('gemini') or os.getenv('GOOGLE_API_KEY')),
            "ollama": True,  # Always available if Ollama is running
        }


# Global provider instance
llm_provider = LLMProvider()


def get_current_llm(temperature: float = 0.7, max_retries: int = 2) -> BaseChatModel:
    """
    Convenience function to get the currently configured LLM.
    
    Usage:
        llm = get_current_llm()
        response = llm.invoke("Hello!")
    """
    return llm_provider.get_llm(temperature=temperature, max_retries=max_retries)
