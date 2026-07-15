"""
Provider Monitor - Track multi-provider usage metrics

Tracks:
- Requests per provider
- Tokens per provider
- Runtime per provider
- Failures per provider
- Fallback usage

Does NOT modify agent logic or workflow.
"""

import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class ProviderMetrics:
    """Metrics for a single provider"""
    provider_name: str
    requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_runtime_seconds: float = 0.0
    fallback_triggered: int = 0
    
    def add_request(
        self,
        success: bool,
        tokens: int = 0,
        runtime: float = 0.0,
        is_fallback: bool = False
    ):
        """Record a request"""
        self.requests += 1
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        self.total_tokens += tokens
        self.total_runtime_seconds += runtime
        
        if is_fallback:
            self.fallback_triggered += 1
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.requests == 0:
            return 0.0
        return (self.successful_requests / self.requests) * 100
    
    @property
    def avg_runtime(self) -> float:
        """Calculate average runtime"""
        if self.requests == 0:
            return 0.0
        return self.total_runtime_seconds / self.requests


class ProviderMonitor:
    """Monitor multi-provider usage"""
    
    def __init__(self, output_dir: str = "provider_metrics"):
        """
        Initialize monitor.
        
        Args:
            output_dir: Directory to save metrics
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Metrics by provider
        self.metrics: Dict[str, ProviderMetrics] = {}
        
        # Metrics by agent
        self.agent_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Session start time
        self.session_start = datetime.now()
    
    def record_request(
        self,
        agent_name: str,
        provider: str,
        model: str,
        success: bool,
        tokens: int = 0,
        runtime: float = 0.0,
        is_fallback: bool = False,
        error: Optional[str] = None
    ):
        """
        Record a provider request.
        
        Args:
            agent_name: Agent making the request
            provider: Provider used
            model: Model used
            success: Whether request succeeded
            tokens: Tokens used
            runtime: Request runtime in seconds
            is_fallback: Whether this was a fallback request
            error: Error message if failed
        """
        # Update provider metrics
        if provider not in self.metrics:
            self.metrics[provider] = ProviderMetrics(provider_name=provider)
        
        self.metrics[provider].add_request(
            success=success,
            tokens=tokens,
            runtime=runtime,
            is_fallback=is_fallback
        )
        
        # Update agent metrics
        if agent_name not in self.agent_metrics:
            self.agent_metrics[agent_name] = {
                'requests': 0,
                'providers_used': {},
                'fallback_count': 0,
                'total_tokens': 0,
                'total_runtime': 0.0,
                'failures': 0
            }
        
        agent_stats = self.agent_metrics[agent_name]
        agent_stats['requests'] += 1
        agent_stats['total_tokens'] += tokens
        agent_stats['total_runtime'] += runtime
        
        if not success:
            agent_stats['failures'] += 1
        
        if is_fallback:
            agent_stats['fallback_count'] += 1
        
        # Track provider usage per agent
        provider_key = f"{provider}/{model}"
        if provider_key not in agent_stats['providers_used']:
            agent_stats['providers_used'][provider_key] = 0
        agent_stats['providers_used'][provider_key] += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        total_requests = sum(m.requests for m in self.metrics.values())
        total_tokens = sum(m.total_tokens for m in self.metrics.values())
        total_failures = sum(m.failed_requests for m in self.metrics.values())
        total_fallbacks = sum(m.fallback_triggered for m in self.metrics.values())
        
        return {
            'session_duration': str(datetime.now() - self.session_start),
            'total_requests': total_requests,
            'total_tokens': total_tokens,
            'total_failures': total_failures,
            'total_fallbacks': total_fallbacks,
            'providers': {
                name: {
                    'requests': m.requests,
                    'success_rate': f"{m.success_rate:.1f}%",
                    'tokens': m.total_tokens,
                    'avg_runtime': f"{m.avg_runtime:.2f}s",
                    'fallback_triggered': m.fallback_triggered
                }
                for name, m in self.metrics.items()
            },
            'agents': dict(self.agent_metrics)
        }
    
    def print_summary(self):
        """Print metrics summary to console"""
        print("\n" + "=" * 80)
        print("MULTI-PROVIDER METRICS SUMMARY")
        print("=" * 80)
        
        summary = self.get_summary()
        
        print(f"\nSession Duration: {summary['session_duration']}")
        print(f"Total Requests: {summary['total_requests']}")
        print(f"Total Tokens: {summary['total_tokens']:,}")
        print(f"Total Failures: {summary['total_failures']}")
        print(f"Total Fallbacks: {summary['total_fallbacks']}")
        
        print("\n" + "-" * 80)
        print("PER-PROVIDER METRICS")
        print("-" * 80)
        
        for provider_name, metrics in summary['providers'].items():
            print(f"\n{provider_name.upper()}:")
            print(f"  Requests: {metrics['requests']}")
            print(f"  Success Rate: {metrics['success_rate']}")
            print(f"  Tokens: {metrics['tokens']:,}")
            print(f"  Avg Runtime: {metrics['avg_runtime']}")
            print(f"  Fallbacks: {metrics['fallback_triggered']}")
        
        print("\n" + "-" * 80)
        print("PER-AGENT METRICS")
        print("-" * 80)
        
        for agent_name, metrics in summary['agents'].items():
            print(f"\n{agent_name}:")
            print(f"  Requests: {metrics['requests']}")
            print(f"  Tokens: {metrics['total_tokens']:,}")
            print(f"  Runtime: {metrics['total_runtime']:.2f}s")
            print(f"  Failures: {metrics['failures']}")
            print(f"  Fallbacks: {metrics['fallback_count']}")
            print(f"  Providers Used:")
            for provider, count in metrics['providers_used'].items():
                print(f"    {provider}: {count}")
    
    def save_metrics(self, filename: Optional[str] = None):
        """Save metrics to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"provider_metrics_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        summary = self.get_summary()
        
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📁 Metrics saved to: {filepath}")
        
        return filepath


# Singleton monitor instance
_monitor: Optional[ProviderMonitor] = None


def get_monitor() -> ProviderMonitor:
    """Get or create singleton monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = ProviderMonitor()
    return _monitor


def reset_monitor():
    """Reset monitor (for testing)"""
    global _monitor
    _monitor = None
