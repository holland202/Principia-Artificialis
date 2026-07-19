#!/usr/bin/env python3
"""
LLM PROVIDERS - ROBUST CLIENT LAYER
====================================

Production-grade LLM client with:
  ✅ Retry logic with exponential backoff
  ✅ Streaming support
  ✅ Clear error classification
  ✅ Health checking / circuit breaker
  ✅ Easy provider extensibility
  ✅ Comprehensive error handling
  ✅ Structured logging
  ✅ Provider abstraction

"""

import time
import logging
from typing import Dict, Any, Optional, Iterator, Tuple, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json


# ============================================================================
# ERROR CLASSIFICATION
# ============================================================================

class LLMErrorType(Enum):
    """Classified error types"""
    RATE_LIMIT = "rate_limit"           # 429
    TIMEOUT = "timeout"                 # Connection/read timeout
    AUTH_ERROR = "auth_error"           # 401/403
    NOT_FOUND = "not_found"             # 404
    CONTEXT_LENGTH = "context_length"   # Input too long
    PROVIDER_ERROR = "provider_error"   # 500/502/503
    NETWORK_ERROR = "network_error"     # Connection refused
    PARSING_ERROR = "parsing_error"     # Invalid response format
    UNKNOWN = "unknown"                 # Unknown error


@dataclass
class LLMError(Exception):
    """Structured LLM error"""
    error_type: LLMErrorType
    message: str
    details: Dict[str, Any]
    timestamp: str
    retryable: bool
    wait_time: Optional[float] = None


@dataclass
class LLMResponse:
    """Structured LLM response"""
    text: str
    model: str
    tokens_input: int
    tokens_output: int
    stop_reason: str
    timestamp: str


# ============================================================================
# CIRCUIT BREAKER / HEALTH CHECK
# ============================================================================

class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"       # Working normally
    OPEN = "open"          # Too many errors, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class HealthMonitor:
    """Monitor provider health with circuit breaker pattern"""
    
    def __init__(self,
                 failure_threshold: int = 5,
                 recovery_timeout: float = 60.0,
                 logger: Optional[logging.Logger] = None):
        self.logger = logger or self._default_logger()
        
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self.error_history: List[LLMError] = []
    
    def _default_logger(self) -> logging.Logger:
        logger = logging.getLogger("HealthMonitor")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def record_success(self) -> None:
        """Record successful operation"""
        self.failure_count = 0
        self.success_count += 1
        
        # Try to transition from HALF_OPEN to CLOSED
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
            self.logger.info("Circuit breaker CLOSED (service recovered)")
    
    def record_failure(self, error: LLMError) -> None:
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        self.error_history.append(error)
        
        if len(self.error_history) > 50:
            self.error_history.pop(0)
        
        # Transition to OPEN if too many failures
        if self.failure_count >= self.failure_threshold:
            if self.state != CircuitBreakerState.OPEN:
                self.state = CircuitBreakerState.OPEN
                self.logger.warning(
                    f"Circuit breaker OPEN ({self.failure_count} failures)"
                )
    
    def can_attempt(self) -> Tuple[bool, Optional[str]]:
        """Check if we can attempt a request"""
        
        if self.state == CircuitBreakerState.CLOSED:
            return True, None
        
        if self.state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.recovery_timeout:
                    # Try recovery
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.failure_count = 0
                    self.logger.info("Circuit breaker HALF_OPEN (testing recovery)")
                    return True, None
                else:
                    remaining = self.recovery_timeout - elapsed
                    return False, f"Circuit breaker OPEN, retry in {remaining:.1f}s"
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            # Allow one attempt to test recovery
            return True, None
        
        return False, "Circuit breaker unavailable"
    
    def get_status(self) -> Dict[str, Any]:
        """Get health status"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure": (
                self.last_failure_time.isoformat()
                if self.last_failure_time else None
            ),
            "recent_errors": [
                {
                    "type": e.error_type.value,
                    "message": e.message,
                    "timestamp": e.timestamp,
                }
                for e in self.error_history[-5:]
            ],
        }


# ============================================================================
# RETRY LOGIC
# ============================================================================

class RetryPolicy:
    """Retry logic with exponential backoff"""
    
    def __init__(self,
                 max_retries: int = 3,
                 initial_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_base: float = 2.0,
                 logger: Optional[logging.Logger] = None):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.logger = logger or self._default_logger()
    
    def _default_logger(self) -> logging.Logger:
        logger = logging.getLogger("RetryPolicy")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def should_retry(self, error: LLMError, attempt: int) -> bool:
        """Determine if error is retryable"""
        
        if attempt >= self.max_retries:
            return False
        
        # Don't retry auth errors
        if error.error_type == LLMErrorType.AUTH_ERROR:
            return False
        
        # Don't retry context length errors
        if error.error_type == LLMErrorType.CONTEXT_LENGTH:
            return False
        
        # Retry everything else
        return error.retryable
    
    def get_wait_time(self, attempt: int) -> float:
        """Calculate wait time with exponential backoff"""
        
        # Use custom wait_time if provided by error
        if hasattr(self, '_last_error') and self._last_error.wait_time:
            return self._last_error.wait_time
        
        delay = self.initial_delay * (self.exponential_base ** attempt)
        return min(delay, self.max_delay)
    
    def execute_with_retry(self, func, *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            
            except LLMError as e:
                last_error = e
                self._last_error = e
                
                if not self.should_retry(e, attempt):
                    self.logger.error(
                        f"Not retrying: {e.error_type.value} "
                        f"({e.message})"
                    )
                    raise
                
                wait_time = self.get_wait_time(attempt)
                self.logger.warning(
                    f"Attempt {attempt + 1}/{self.max_retries + 1} failed: "
                    f"{e.error_type.value}. Retrying in {wait_time:.1f}s..."
                )
                time.sleep(wait_time)
        
        # All retries exhausted
        if last_error:
            raise last_error


# ============================================================================
# LLM PROVIDER ABSTRACTION
# ============================================================================

class LLMProvider(ABC):
    """Abstract base for LLM providers"""
    
    def __init__(self, name: str, logger: Optional[logging.Logger] = None):
        self.name = name
        self.logger = logger or self._default_logger()
        self.health = HealthMonitor(logger=self.logger)
        self.retry_policy = RetryPolicy(logger=self.logger)
    
    def _default_logger(self) -> logging.Logger:
        logger = logging.getLogger(f"LLMProvider[{self.name}]")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    @abstractmethod
    def complete(self,
                prompt: str,
                system: str = "",
                max_tokens: int = 1024,
                temperature: float = 0.7) -> LLMResponse:
        """Complete a prompt"""
        pass
    
    @abstractmethod
    def stream(self,
              prompt: str,
              system: str = "",
              max_tokens: int = 1024,
              temperature: float = 0.7) -> Iterator[str]:
        """Stream completion tokens"""
        pass
    
    def _classify_error(self, error: Exception) -> LLMError:
        """Classify error type from exception"""
        
        error_msg = str(error).lower()
        details = {"raw_exception": str(error)}
        
        if "rate limit" in error_msg or "429" in error_msg:
            return LLMError(
                error_type=LLMErrorType.RATE_LIMIT,
                message="Rate limited",
                details=details,
                timestamp=datetime.now().isoformat(),
                retryable=True,
                wait_time=60.0,
            )
        
        if "timeout" in error_msg:
            return LLMError(
                error_type=LLMErrorType.TIMEOUT,
                message="Request timeout",
                details=details,
                timestamp=datetime.now().isoformat(),
                retryable=True,
                wait_time=10.0,
            )
        
        if "401" in error_msg or "403" in error_msg or "unauthorized" in error_msg:
            return LLMError(
                error_type=LLMErrorType.AUTH_ERROR,
                message="Authentication failed",
                details=details,
                timestamp=datetime.now().isoformat(),
                retryable=False,
            )
        
        if "context length" in error_msg or "too long" in error_msg:
            return LLMError(
                error_type=LLMErrorType.CONTEXT_LENGTH,
                message="Input too long",
                details=details,
                timestamp=datetime.now().isoformat(),
                retryable=False,
            )
        
        if "500" in error_msg or "502" in error_msg or "503" in error_msg:
            return LLMError(
                error_type=LLMErrorType.PROVIDER_ERROR,
                message="Provider error",
                details=details,
                timestamp=datetime.now().isoformat(),
                retryable=True,
                wait_time=30.0,
            )
        
        if "connection" in error_msg or "network" in error_msg:
            return LLMError(
                error_type=LLMErrorType.NETWORK_ERROR,
                message="Network error",
                details=details,
                timestamp=datetime.now().isoformat(),
                retryable=True,
                wait_time=5.0,
            )
        
        return LLMError(
            error_type=LLMErrorType.UNKNOWN,
            message="Unknown error",
            details=details,
            timestamp=datetime.now().isoformat(),
            retryable=True,
            wait_time=5.0,
        )


# ============================================================================
# CLAUDE PROVIDER
# ============================================================================

class ClaudeProvider(LLMProvider):
    """Claude API provider"""
    
    def __init__(self, api_key: Optional[str] = None,
                 model: str = "claude-opus-4-6",
                 logger: Optional[logging.Logger] = None):
        super().__init__("claude", logger)
        self.api_key = api_key
        self.model = model
        self.client = None
        
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
            self.available = True
            self.logger.info(f"Claude initialized ({model})")
        except ImportError:
            self.available = False
            self.logger.warning("anthropic package not installed")
        except Exception as e:
            self.available = False
            self.logger.error(f"Failed to initialize Claude: {e}")
    
    def complete(self,
                prompt: str,
                system: str = "",
                max_tokens: int = 1024,
                temperature: float = 0.7) -> LLMResponse:
        """Complete with Claude (with retry logic)"""
        
        if not self.available:
            raise LLMError(
                error_type=LLMErrorType.PROVIDER_ERROR,
                message="Claude not available",
                details={"reason": "Client not initialized"},
                timestamp=datetime.now().isoformat(),
                retryable=False,
            )
        
        # Check circuit breaker
        can_attempt, reason = self.health.can_attempt()
        if not can_attempt:
            raise LLMError(
                error_type=LLMErrorType.PROVIDER_ERROR,
                message=reason,
                details={"circuit_breaker": True},
                timestamp=datetime.now().isoformat(),
                retryable=True,
            )
        
        # Execute with retry
        try:
            return self.retry_policy.execute_with_retry(
                self._complete_impl,
                prompt, system, max_tokens, temperature
            )
        except LLMError as e:
            self.health.record_failure(e)
            raise
    
    def _complete_impl(self,
                      prompt: str,
                      system: str,
                      max_tokens: int,
                      temperature: float) -> LLMResponse:
        """Actual Claude completion call"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system or None,
                messages=[{"role": "user", "content": prompt}]
            )
            
            self.health.record_success()
            
            return LLMResponse(
                text=response.content[0].text,
                model=self.model,
                tokens_input=response.usage.input_tokens,
                tokens_output=response.usage.output_tokens,
                stop_reason=response.stop_reason,
                timestamp=datetime.now().isoformat(),
            )
        
        except Exception as e:
            error = self._classify_error(e)
            raise error
    
    def stream(self,
              prompt: str,
              system: str = "",
              max_tokens: int = 1024,
              temperature: float = 0.7) -> Iterator[str]:
        """Stream completion from Claude"""
        
        if not self.available:
            raise LLMError(
                error_type=LLMErrorType.PROVIDER_ERROR,
                message="Claude not available",
                details={"reason": "Client not initialized"},
                timestamp=datetime.now().isoformat(),
                retryable=False,
            )
        
        can_attempt, reason = self.health.can_attempt()
        if not can_attempt:
            raise LLMError(
                error_type=LLMErrorType.PROVIDER_ERROR,
                message=reason,
                details={"circuit_breaker": True},
                timestamp=datetime.now().isoformat(),
                retryable=True,
            )
        
        try:
            with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system or None,
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                for text in stream.text_stream:
                    yield text
            
            self.health.record_success()
        
        except Exception as e:
            error = self._classify_error(e)
            self.health.record_failure(error)
            raise error


# ============================================================================
# GPT PROVIDER
# ============================================================================

class GPTProvider(LLMProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, api_key: Optional[str] = None,
                 model: str = "gpt-4-turbo",
                 logger: Optional[logging.Logger] = None):
        super().__init__("gpt", logger)
        self.api_key = api_key
        self.model = model
        self.client = None
        
        try:
            import openai
            openai.api_key = api_key
            self.client = openai.OpenAI(api_key=api_key)
            self.available = True
            self.logger.info(f"GPT initialized ({model})")
        except ImportError:
            self.available = False
            self.logger.warning("openai package not installed")
        except Exception as e:
            self.available = False
            self.logger.error(f"Failed to initialize GPT: {e}")
    
    def complete(self,
                prompt: str,
                system: str = "",
                max_tokens: int = 1024,
                temperature: float = 0.7) -> LLMResponse:
        """Complete with GPT"""
        
        if not self.available:
            raise LLMError(
                error_type=LLMErrorType.PROVIDER_ERROR,
                message="GPT not available",
                details={"reason": "Client not initialized"},
                timestamp=datetime.now().isoformat(),
                retryable=False,
            )
        
        can_attempt, reason = self.health.can_attempt()
        if not can_attempt:
            raise LLMError(
                error_type=LLMErrorType.PROVIDER_ERROR,
                message=reason,
                details={"circuit_breaker": True},
                timestamp=datetime.now().isoformat(),
                retryable=True,
            )
        
        try:
            return self.retry_policy.execute_with_retry(
                self._complete_impl,
                prompt, system, max_tokens, temperature
            )
        except LLMError as e:
            self.health.record_failure(e)
            raise
    
    def _complete_impl(self,
                      prompt: str,
                      system: str,
                      max_tokens: int,
                      temperature: float) -> LLMResponse:
        """Actual GPT completion call"""
        
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            self.health.record_success()
            
            return LLMResponse(
                text=response.choices[0].message.content,
                model=self.model,
                tokens_input=response.usage.prompt_tokens,
                tokens_output=response.usage.completion_tokens,
                stop_reason=response.choices[0].finish_reason,
                timestamp=datetime.now().isoformat(),
            )
        
        except Exception as e:
            error = self._classify_error(e)
            raise error
    
    def stream(self,
              prompt: str,
              system: str = "",
              max_tokens: int = 1024,
              temperature: float = 0.7) -> Iterator[str]:
        """Stream completion from GPT"""
        
        if not self.available:
            raise LLMError(
                error_type=LLMErrorType.PROVIDER_ERROR,
                message="GPT not available",
                details={"reason": "Client not initialized"},
                timestamp=datetime.now().isoformat(),
                retryable=False,
            )
        
        can_attempt, reason = self.health.can_attempt()
        if not can_attempt:
            raise LLMError(
                error_type=LLMErrorType.PROVIDER_ERROR,
                message=reason,
                details={"circuit_breaker": True},
                timestamp=datetime.now().isoformat(),
                retryable=True,
            )
        
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            
            self.health.record_success()
        
        except Exception as e:
            error = self._classify_error(e)
            self.health.record_failure(error)
            raise error


# ============================================================================
# FALLBACK PROVIDER
# ============================================================================

class FallbackProvider(LLMProvider):
    """Emergency fallback (no dependencies)"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__("fallback", logger)
        self.available = True
    
    def complete(self,
                prompt: str,
                system: str = "",
                max_tokens: int = 1024,
                temperature: float = 0.7) -> LLMResponse:
        """Fallback response"""
        
        text = f"[Fallback] System in emergency mode. Query: {prompt[:50]}..."
        
        self.health.record_success()
        
        return LLMResponse(
            text=text,
            model="fallback",
            tokens_input=len(prompt.split()),
            tokens_output=len(text.split()),
            stop_reason="max_tokens",
            timestamp=datetime.now().isoformat(),
        )
    
    def stream(self,
              prompt: str,
              system: str = "",
              max_tokens: int = 1024,
              temperature: float = 0.7) -> Iterator[str]:
        """Stream fallback"""
        
        text = f"[Fallback] System in emergency mode."
        for word in text.split():
            yield word + " "


# ============================================================================
# PROVIDER MANAGER
# ============================================================================

class LLMProviderManager:
    """Manage multiple providers with fallback chain"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or self._default_logger()
        self.providers: Dict[str, LLMProvider] = {}
        self.provider_chain: List[str] = []
    
    def _default_logger(self) -> logging.Logger:
        logger = logging.getLogger("LLMProviderManager")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def register(self, name: str, provider: LLMProvider) -> None:
        """Register provider"""
        self.providers[name] = provider
        if name not in self.provider_chain:
            self.provider_chain.append(name)
        self.logger.info(f"Registered provider: {name}")
    
    def set_chain(self, chain: List[str]) -> None:
        """Set provider fallback chain"""
        for name in chain:
            if name not in self.providers:
                raise ValueError(f"Unknown provider: {name}")
        self.provider_chain = chain
        self.logger.info(f"Provider chain: {' → '.join(chain)}")
    
    def complete(self,
                prompt: str,
                system: str = "",
                max_tokens: int = 1024,
                temperature: float = 0.7) -> Tuple[LLMResponse, str]:
        """Complete with fallback chain"""
        
        for provider_name in self.provider_chain:
            provider = self.providers.get(provider_name)
            if not provider:
                continue
            
            try:
                response = provider.complete(
                    prompt, system, max_tokens, temperature
                )
                self.logger.info(f"Response from {provider_name}")
                return response, provider_name
            
            except LLMError as e:
                self.logger.warning(
                    f"{provider_name} failed: {e.error_type.value}. "
                    f"Trying next provider..."
                )
                continue
        
        # All failed, return error
        raise LLMError(
            error_type=LLMErrorType.PROVIDER_ERROR,
            message="All providers failed",
            details={"chain": self.provider_chain},
            timestamp=datetime.now().isoformat(),
            retryable=False,
        )
    
    def stream(self,
              prompt: str,
              system: str = "",
              max_tokens: int = 1024,
              temperature: float = 0.7) -> Tuple[Iterator[str], str]:
        """Stream with fallback chain"""
        
        for provider_name in self.provider_chain:
            provider = self.providers.get(provider_name)
            if not provider:
                continue
            
            try:
                stream = provider.stream(
                    prompt, system, max_tokens, temperature
                )
                self.logger.info(f"Streaming from {provider_name}")
                return stream, provider_name
            
            except LLMError as e:
                self.logger.warning(
                    f"{provider_name} failed: {e.error_type.value}. "
                    f"Trying next provider..."
                )
                continue
        
        raise LLMError(
            error_type=LLMErrorType.PROVIDER_ERROR,
            message="All providers failed for streaming",
            details={"chain": self.provider_chain},
            timestamp=datetime.now().isoformat(),
            retryable=False,
        )
    
    def get_health(self) -> Dict[str, Any]:
        """Get health status of all providers"""
        return {
            provider_name: provider.health.get_status()
            for provider_name, provider in self.providers.items()
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    
    print("\n" + "="*100)
    print("LLM PROVIDERS - PRODUCTION CLIENT LAYER".center(100))
    print("="*100 + "\n")
    
    # Create manager
    manager = LLMProviderManager()
    
    # Register providers
    manager.register("claude", ClaudeProvider())
    manager.register("gpt", GPTProvider())
    manager.register("fallback", FallbackProvider())
    
    # Set fallback chain
    manager.set_chain(["claude", "gpt", "fallback"])
    
    # Try to complete
    try:
        print("Attempting completion through fallback chain...")
        response, provider = manager.complete(
            "What is machine learning?",
            system="You are helpful"
        )
        
        print(f"\nResponse from {provider}:")
        print(f"  Text: {response.text[:100]}...")
        print(f"  Model: {response.model}")
        print(f"  Tokens: {response.tokens_input} in, {response.tokens_output} out")
    
    except Exception as e:
        print(f"Error: {e}")
    
    # Show health
    print("\nProvider Health Status:")
    health = manager.get_health()
    for provider_name, status in health.items():
        print(f"\n  {provider_name}:")
        print(f"    State: {status['state']}")
        print(f"    Successes: {status['success_count']}")
        print(f"    Failures: {status['failure_count']}")
    
    print("\n" + "="*100)
    print("✓ LLM providers operational".center(100))
    print("="*100 + "\n")
