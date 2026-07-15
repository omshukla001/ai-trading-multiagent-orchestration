"""
Multi-Provider Router for TradingAgents

Routes LLM agents to appropriate providers with fallback support.

DOES NOT MODIFY:
- Architecture
- Workflow
- Agent logic
- Prompts
- Business logic

ONLY PROVIDES:
- Provider routing
- Model selection
- Fallback handling
- Monitoring hooks
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProviderConfig:
    """Configuration for a provider"""
    provider: str
    model: str
    base_url: str
    
    def __repr__(self):
        """Safe repr that doesn't expose API keys"""
        return f"ProviderConfig(provider={self.provider}, model={self.model})"


# Provider routing map using EXACT runtime node names
# Extracted from graph/setup.py: workflow.add_node() calls

# VALIDATION MODE: Set to True to use Cerebras for all agents (testing only)
VALIDATION_MODE = os.environ.get('VALIDATION_MODE', 'false').lower() == 'true'

if VALIDATION_MODE:
    logger.warning("⚠️  VALIDATION MODE: All agents using Cerebras (temporary testing)")
    
    # All agents use Cerebras in validation mode
    _cerebras_config = {
        "primary": ProviderConfig(
            provider="openai_compatible",
            model="gpt-oss-120b",
            base_url="https://api.cerebras.ai/v1"
        ),
        "backup": None  # No backup in validation mode
    }
    
    AGENT_ROUTING_MAP: Dict[str, Dict[str, ProviderConfig]] = {
        "News Analyst": _cerebras_config,
        "Bull Researcher": _cerebras_config,
        "Bear Researcher": _cerebras_config,
        "Research Manager": _cerebras_config,
        "Trader": _cerebras_config,
        "Portfolio Manager": _cerebras_config
    }
else:
    # Production multi-provider routing
    AGENT_ROUTING_MAP: Dict[str, Dict[str, ProviderConfig]] = {
        # ====================================================
        # CEREBRAS - Heavy Reasoning (Bull/Bear debate)
        # ====================================================
        "Bull Researcher": {
            "primary": ProviderConfig(
                provider="openai_compatible",
                model="gpt-oss-120b",
                base_url="https://api.cerebras.ai/v1"
            ),
            "backup": ProviderConfig(
                provider="openrouter",
                model="openai/gpt-oss-120b:free",
                base_url="https://openrouter.ai/api/v1"
            )
        },
        
        "Bear Researcher": {
            "primary": ProviderConfig(
                provider="openai_compatible",
                model="gpt-oss-120b",
                base_url="https://api.cerebras.ai/v1"
            ),
            "backup": ProviderConfig(
                provider="openrouter",
                model="openai/gpt-oss-120b:free",
                base_url="https://openrouter.ai/api/v1"
            )
        },
        
        # ====================================================
        # OPENROUTER - Summarization & Decisions
        # ====================================================
        "News Analyst": {
            "primary": ProviderConfig(
                provider="openrouter",
                model="qwen/qwen3-next-80b-a3b-instruct:free",
                base_url="https://openrouter.ai/api/v1"
            ),
            "backup": ProviderConfig(
                provider="openai_compatible",
                model="gpt-oss-120b",
                base_url="https://api.cerebras.ai/v1"
            )
        },
        
        "Research Manager": {
            "primary": ProviderConfig(
                provider="openrouter",
                model="nvidia/nemotron-3-super:free",
                base_url="https://openrouter.ai/api/v1"
            ),
            "backup": ProviderConfig(
                provider="openai_compatible",
                model="gpt-oss-120b",
                base_url="https://api.cerebras.ai/v1"
            )
        },
        
        "Trader": {
            "primary": ProviderConfig(
                provider="openrouter",
                model="openai/gpt-oss-120b:free",
                base_url="https://openrouter.ai/api/v1"
            ),
            "backup": ProviderConfig(
                provider="openai_compatible",
                model="gpt-oss-120b",
                base_url="https://api.cerebras.ai/v1"
            )
        },
        
        "Portfolio Manager": {
            "primary": ProviderConfig(
                provider="openrouter",
                model="openai/gpt-oss-120b:free",
                base_url="https://openrouter.ai/api/v1"
            ),
            "backup": ProviderConfig(
                provider="openai_compatible",
                model="gpt-oss-120b",
                base_url="https://api.cerebras.ai/v1"
            )
        }
    }


class ProviderRouter:
    """
    Routes agents to appropriate providers.
    
    Thread-safe, stateless router that only provides configuration.
    Does not modify agent logic or workflow.
    """
    
    def __init__(self, enable_multi_provider: bool = None):
        """
        Initialize router.
        
        Args:
            enable_multi_provider: Enable multi-provider routing.
                                  If None, reads from environment.
        """
        if enable_multi_provider is None:
            enable_multi_provider = os.environ.get('ENABLE_MULTI_PROVIDER', 'false').lower() == 'true'
        
        self.enabled = enable_multi_provider
        
        if self.enabled:
            logger.info("Multi-provider routing ENABLED")
        else:
            logger.info("Multi-provider routing DISABLED (using default provider)")
    
    def get_provider_config(
        self,
        agent_name: str,
        prefer_backup: bool = False
    ) -> Optional[ProviderConfig]:
        """
        Get provider configuration for an agent.
        
        Args:
            agent_name: Exact agent node name (e.g., "Bull Researcher")
            prefer_backup: If True, return backup provider
        
        Returns:
            ProviderConfig or None if not found
        """
        if not self.enabled:
            return None
        
        routing = AGENT_ROUTING_MAP.get(agent_name)
        
        if not routing:
            logger.warning(f"No routing config for agent: {agent_name}")
            return None
        
        config_key = "backup" if prefer_backup else "primary"
        config = routing.get(config_key)
        
        if config:
            logger.debug(f"{agent_name} -> {config.provider}/{config.model} ({config_key})")
        
        return config
    
    def get_api_key(self, provider_config: ProviderConfig) -> Optional[str]:
        """
        Get API key for provider.
        
        SECURITY: Never logs or exposes API keys.
        
        Args:
            provider_config: Provider configuration
            
        Returns:
            API key from environment
        """
        if provider_config.provider == "openai_compatible":
            # Cerebras uses CEREBRAS_API_KEY or OPENAI_COMPATIBLE_API_KEY
            key = os.environ.get('CEREBRAS_API_KEY') or os.environ.get('OPENAI_COMPATIBLE_API_KEY')
        elif provider_config.provider == "openrouter":
            key = os.environ.get('OPENROUTER_API_KEY')
        else:
            # Fallback to provider-specific key
            key_env = f"{provider_config.provider.upper()}_API_KEY"
            key = os.environ.get(key_env)
        
        if not key:
            logger.error(f"API key not found for provider: {provider_config.provider}")
            return None
        
        # SECURITY: Only log last 4 chars
        logger.debug(f"API key found for {provider_config.provider} (ends with ...{key[-4:]})")
        
        return key
    
    def should_use_routing(self, agent_name: str) -> bool:
        """
        Check if agent should use multi-provider routing.
        
        Args:
            agent_name: Agent node name
            
        Returns:
            True if routing should be used
        """
        return self.enabled and agent_name in AGENT_ROUTING_MAP
    
    def get_all_routed_agents(self) -> list[str]:
        """Get list of all agents with routing configured"""
        return list(AGENT_ROUTING_MAP.keys())


def create_routed_llm(
    agent_name: str,
    router: ProviderRouter,
    prefer_backup: bool = False
):
    """
    Create LLM client with provider routing and automatic fallback.
    
    Implements TWO layers of fallback:
    1. Client creation fallback (if provider fails to initialize)
    2. Runtime invoke fallback (if provider fails during execution)
    
    Args:
        agent_name: Exact agent node name
        router: ProviderRouter instance
        prefer_backup: Use backup provider
        
    Returns:
        Configured LLM client with fallback wrapper
    """
    from .factory import create_llm_client
    from .provider_monitor import get_monitor
    
    monitor = get_monitor()
    
    # Get provider configs
    primary_config = router.get_provider_config(agent_name, prefer_backup=False)
    backup_config = router.get_provider_config(agent_name, prefer_backup=True)
    
    if not primary_config:
        raise ValueError(f"No provider config found for agent: {agent_name}")
    
    # LAYER 1: Client Creation Fallback
    primary_llm = None
    primary_failed = False
    
    try:
        # Try to create primary LLM client
        logger.info(f"{agent_name}: Creating primary LLM client "
                   f"({primary_config.provider}/{primary_config.model})")
        
        api_key = router.get_api_key(primary_config)
        if not api_key:
            raise ValueError(f"API key not found for provider: {primary_config.provider}")
        
        # Set API key in environment
        if primary_config.provider == "openai_compatible":
            os.environ['OPENAI_COMPATIBLE_API_KEY'] = api_key
        elif primary_config.provider == "openrouter":
            os.environ['OPENROUTER_API_KEY'] = api_key
        
        primary_client = create_llm_client(
            provider=primary_config.provider,
            model=primary_config.model,
            base_url=primary_config.base_url
        )
        
        primary_llm = primary_client.get_llm()
        
        logger.info(f"{agent_name}: Primary LLM client created successfully")
        
    except Exception as e:
        primary_failed = True
        error_msg = str(e)
        
        logger.warning(f"{agent_name}: Primary LLM client creation failed: {error_msg[:100]}")
        
        # Record client creation failure
        monitor.record_request(
            agent_name=agent_name,
            provider=primary_config.provider,
            model=primary_config.model,
            success=False,
            is_fallback=False,
            error=error_msg
        )
        
        if not backup_config:
            logger.error(f"{agent_name}: No backup provider configured, cannot recover")
            raise
        
        # Try backup provider
        logger.info(f"{agent_name}: Falling back to backup provider during client creation "
                   f"({backup_config.provider}/{backup_config.model})")
        
        try:
            backup_key = router.get_api_key(backup_config)
            if not backup_key:
                raise ValueError(f"API key not found for backup provider: {backup_config.provider}")
            
            # Set backup API key
            if backup_config.provider == "openai_compatible":
                os.environ['OPENAI_COMPATIBLE_API_KEY'] = backup_key
            elif backup_config.provider == "openrouter":
                os.environ['OPENROUTER_API_KEY'] = backup_key
            
            backup_client = create_llm_client(
                provider=backup_config.provider,
                model=backup_config.model,
                base_url=backup_config.base_url
            )
            
            primary_llm = backup_client.get_llm()
            
            logger.info(f"{agent_name}: Backup LLM client created successfully")
            
            # Record backup success during creation
            monitor.record_request(
                agent_name=agent_name,
                provider=backup_config.provider,
                model=backup_config.model,
                success=True,
                is_fallback=True
            )
            
            # Since we fell back during creation, use backup as primary for this session
            primary_config = backup_config
            backup_config = None  # No further fallback available
            
        except Exception as backup_error:
            logger.error(f"{agent_name}: Backup LLM client creation also failed: {str(backup_error)[:100]}")
            
            monitor.record_request(
                agent_name=agent_name,
                provider=backup_config.provider,
                model=backup_config.model,
                success=False,
                is_fallback=True,
                error=str(backup_error)
            )
            
            raise Exception(f"{agent_name}: Both primary and backup LLM client creation failed. "
                          f"Primary: {error_msg}, Backup: {str(backup_error)}")
    
    # If no backup available or we already fell back during creation, return without runtime wrapper
    if not backup_config:
        return primary_llm
    
    # LAYER 2: Runtime Invoke Fallback Wrapper
    class FallbackLLM:
        """LLM wrapper with automatic fallback to backup provider during invoke()"""
        
        def __init__(self):
            self.agent_name = agent_name
            self.primary_llm = primary_llm
            self.primary_config = primary_config
            self.backup_config = backup_config
            self.router = router
            self.monitor = monitor
            self._backup_llm = None
        
        def _get_backup_llm(self):
            """Lazy-create backup LLM"""
            if self._backup_llm is None:
                backup_key = self.router.get_api_key(self.backup_config)
                
                if self.backup_config.provider == "openai_compatible":
                    os.environ['OPENAI_COMPATIBLE_API_KEY'] = backup_key
                elif self.backup_config.provider == "openrouter":
                    os.environ['OPENROUTER_API_KEY'] = backup_key
                
                logger.info(f"{self.agent_name}: Creating backup LLM for runtime fallback: "
                           f"{self.backup_config.provider}/{self.backup_config.model}")
                
                backup_client = create_llm_client(
                    provider=self.backup_config.provider,
                    model=self.backup_config.model,
                    base_url=self.backup_config.base_url
                )
                
                self._backup_llm = backup_client.get_llm()
            
            return self._backup_llm
        
        def invoke(self, input, config=None, **kwargs):
            """Invoke with automatic fallback on failure"""
            import time
            
            # Try primary provider
            start_time = time.time()
            
            try:
                logger.debug(f"{self.agent_name}: Invoking primary provider "
                           f"({self.primary_config.provider})")
                
                response = self.primary_llm.invoke(input, config, **kwargs)
                
                runtime = time.time() - start_time
                
                # Estimate tokens (rough)
                tokens = len(str(input)) // 4 + len(str(response.content)) // 4
                
                # Record success
                self.monitor.record_request(
                    agent_name=self.agent_name,
                    provider=self.primary_config.provider,
                    model=self.primary_config.model,
                    success=True,
                    tokens=tokens,
                    runtime=runtime,
                    is_fallback=False
                )
                
                logger.debug(f"{self.agent_name}: Primary provider succeeded "
                           f"({runtime:.1f}s, ~{tokens} tokens)")
                
                return response
                
            except Exception as e:
                runtime = time.time() - start_time
                error_msg = str(e)
                
                # Check if this is a fallback-triggering error
                should_fallback = any(err in error_msg.lower() for err in [
                    'rate limit',
                    'rate_limit',
                    '429',
                    'timeout',
                    'timed out',
                    'unavailable',
                    'not found',
                    '503',
                    '502',
                    '500',
                    'auth',
                    'invalid'
                ])
                
                if should_fallback:
                    logger.warning(f"{self.agent_name}: Primary provider runtime error "
                                 f"({self.primary_config.provider}): {error_msg[:100]}")
                    
                    # Record primary failure
                    self.monitor.record_request(
                        agent_name=self.agent_name,
                        provider=self.primary_config.provider,
                        model=self.primary_config.model,
                        success=False,
                        runtime=runtime,
                        is_fallback=False,
                        error=error_msg
                    )
                    
                    # Try backup provider
                    logger.info(f"{self.agent_name}: Switching to backup provider "
                              f"({self.backup_config.provider})")
                    
                    backup_start = time.time()
                    
                    try:
                        backup_llm = self._get_backup_llm()
                        response = backup_llm.invoke(input, config, **kwargs)
                        
                        backup_runtime = time.time() - backup_start
                        tokens = len(str(input)) // 4 + len(str(response.content)) // 4
                        
                        # Record backup success
                        self.monitor.record_request(
                            agent_name=self.agent_name,
                            provider=self.backup_config.provider,
                            model=self.backup_config.model,
                            success=True,
                            tokens=tokens,
                            runtime=backup_runtime,
                            is_fallback=True
                        )
                        
                        logger.info(f"{self.agent_name}: Backup provider succeeded "
                                  f"({backup_runtime:.1f}s, ~{tokens} tokens)")
                        
                        return response
                        
                    except Exception as backup_error:
                        backup_runtime = time.time() - backup_start
                        
                        # Record backup failure
                        self.monitor.record_request(
                            agent_name=self.agent_name,
                            provider=self.backup_config.provider,
                            model=self.backup_config.model,
                            success=False,
                            runtime=backup_runtime,
                            is_fallback=True,
                            error=str(backup_error)
                        )
                        
                        logger.error(f"{self.agent_name}: Backup provider also failed: "
                                   f"{str(backup_error)[:100]}")
                        
                        raise Exception(f"Both providers failed. Primary: {error_msg}, "
                                      f"Backup: {str(backup_error)}")
                else:
                    # Not a fallback-triggering error, re-raise
                    logger.error(f"{self.agent_name}: Non-recoverable error: {error_msg[:100]}")
                    raise
        
        def __getattr__(self, name):
            """Proxy other methods to primary LLM"""
            return getattr(self.primary_llm, name)
    
    return FallbackLLM()


# Singleton router instance
_router: Optional[ProviderRouter] = None


def get_router() -> ProviderRouter:
    """Get or create singleton router instance"""
    global _router
    if _router is None:
        _router = ProviderRouter()
    return _router


def reset_router():
    """Reset router (for testing)"""
    global _router
    _router = None
