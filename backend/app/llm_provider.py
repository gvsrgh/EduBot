"""
Multi-Provider LLM Configuration Module

This module handles dynamic model selection between:
- OpenAI GPT-4
- Google Gemini
- Gemma (via Ollama local)

Selection is controlled via AI_PROVIDER environment variable.
"""

import os
from typing import Optional, Literal
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel
from app.config import (
    AI_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    GOOGLE_API_KEY,
    GEMINI_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)

ProviderType = Literal["openai", "gemini", "ollama", "auto"]


class LLMProvider:
    """Manages dynamic LLM provider selection and fallback."""
    
    def __init__(self):
        self.current_provider: str = AI_PROVIDER
        
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
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured")
        
        return ChatOpenAI(
            model=OPENAI_MODEL,
            temperature=temperature,
            max_retries=max_retries,
            openai_api_key=OPENAI_API_KEY,
        )
    
    def _get_gemini(self, temperature: float, max_retries: int) -> ChatGoogleGenerativeAI:
        """Get Google Gemini model."""
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not configured")
        
        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            temperature=temperature,
            max_retries=max_retries,
            google_api_key=GOOGLE_API_KEY,
        )
    
    def _get_ollama(self, temperature: float, max_retries: int) -> ChatOllama:
        """Get Ollama local model (Gemma)."""
        return ChatOllama(
            model=OLLAMA_MODEL,
            temperature=temperature,
            max_retries=max_retries,
            base_url=OLLAMA_BASE_URL,
        )
    
    def _get_auto_provider(self, temperature: float, max_retries: int) -> BaseChatModel:
        """
        Auto-select provider with fallback priority:
        1. OpenAI (if API key exists)
        2. Gemini (if API key exists)
        3. Ollama (local fallback)
        """
        # Try OpenAI first
        if OPENAI_API_KEY:
            try:
                return self._get_openai(temperature, max_retries)
            except Exception as e:
                print(f"OpenAI failed: {e}, trying Gemini...")
        
        # Try Gemini next
        if GOOGLE_API_KEY:
            try:
                return self._get_gemini(temperature, max_retries)
            except Exception as e:
                print(f"Gemini failed: {e}, trying Ollama...")
        
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
    
    def get_available_providers(self) -> dict[str, bool]:
        """Check which providers are available based on configuration."""
        return {
            "openai": bool(OPENAI_API_KEY),
            "gemini": bool(GOOGLE_API_KEY),
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
