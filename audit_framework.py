"""
LLM Agent Audit Framework

Instruments LLM calls to measure:
- Input tokens
- Output tokens  
- Runtime
- Estimated cost

Non-intrusive wrapper that logs all LLM interactions.
"""

import time
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class LLMCallMetrics:
    """Metrics for a single LLM call"""
    agent_name: str
    timestamp: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    runtime_seconds: float
    model: str
    provider: str
    estimated_cost_usd: float
    prompt_preview: str  # First 100 chars
    response_preview: str  # First 100 chars


class TokenCounter:
    """Estimates token counts (rough approximation)"""
    
    @staticmethod
    def count_tokens(text: str) -> int:
        """
        Rough token estimation: ~4 chars per token
        More accurate than word count for API usage
        """
        if not text:
            return 0
        return len(text) // 4
    
    @staticmethod
    def extract_from_response(response: Any) -> tuple[int, int]:
        """
        Extract token counts from LLM response if available
        Falls back to estimation if not provided
        """
        input_tokens = 0
        output_tokens = 0
        
        # Try to extract from response metadata
        if hasattr(response, 'usage'):
            usage = response.usage
            input_tokens = getattr(usage, 'prompt_tokens', 0)
            output_tokens = getattr(usage, 'completion_tokens', 0)
        elif hasattr(response, 'response_metadata'):
            metadata = response.response_metadata
            if 'usage' in metadata:
                input_tokens = metadata['usage'].get('prompt_tokens', 0)
                output_tokens = metadata['usage'].get('completion_tokens', 0)
        
        return input_tokens, output_tokens


class CostEstimator:
    """Estimates cost based on provider and model"""
    
    # Cost per 1M tokens (input / output)
    PRICING = {
        'cerebras': {
            'gpt-oss-120b': (0.60, 0.60),  # $0.60 per 1M tokens
        },
        'openrouter': {
            'qwen/qwen3-next-80b-a3b-instruct:free': (0.0, 0.0),  # Free
            'nvidia/nemotron-3-super:free': (0.0, 0.0),  # Free
            'openai/gpt-oss-120b:free': (0.0, 0.0),  # Free
            'qwen/qwen3-next-80b': (0.30, 0.30),  # Paid tier estimate
            'nvidia/nemotron-3-super': (0.40, 0.40),  # Paid tier estimate
        },
        'groq': {
            'llama-3.3-70b-versatile': (0.59, 0.79),
            'llama-3.1-70b-versatile': (0.59, 0.79),
        },
        'openai': {
            'gpt-4': (30.0, 60.0),
            'gpt-4-turbo': (10.0, 30.0),
            'gpt-3.5-turbo': (0.5, 1.5),
        }
    }
    
    @staticmethod
    def estimate_cost(provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate estimated cost in USD"""
        provider_lower = provider.lower()
        
        # Get pricing
        if provider_lower in CostEstimator.PRICING:
            model_pricing = CostEstimator.PRICING[provider_lower]
            
            # Find matching model
            for model_key, (input_price, output_price) in model_pricing.items():
                if model_key in model.lower():
                    input_cost = (input_tokens / 1_000_000) * input_price
                    output_cost = (output_tokens / 1_000_000) * output_price
                    return input_cost + output_cost
        
        # Default fallback: assume $0.60 per 1M tokens
        return ((input_tokens + output_tokens) / 1_000_000) * 0.60


class LLMAuditCollector:
    """Collects and aggregates LLM audit metrics"""
    
    def __init__(self):
        self.calls: List[LLMCallMetrics] = []
        self.per_agent: Dict[str, List[LLMCallMetrics]] = defaultdict(list)
        
    def record_call(self, metrics: LLMCallMetrics):
        """Record a single LLM call"""
        self.calls.append(metrics)
        self.per_agent[metrics.agent_name].append(metrics)
    
    def get_agent_summary(self, agent_name: str) -> Dict[str, Any]:
        """Get summary stats for a specific agent"""
        calls = self.per_agent.get(agent_name, [])
        
        if not calls:
            return {
                'agent_name': agent_name,
                'total_calls': 0,
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'total_tokens': 0,
                'total_runtime': 0.0,
                'total_cost': 0.0,
                'avg_tokens_per_call': 0,
                'avg_runtime_per_call': 0.0,
                'avg_cost_per_call': 0.0
            }
        
        total_input = sum(c.input_tokens for c in calls)
        total_output = sum(c.output_tokens for c in calls)
        total_tokens = sum(c.total_tokens for c in calls)
        total_runtime = sum(c.runtime_seconds for c in calls)
        total_cost = sum(c.estimated_cost_usd for c in calls)
        
        return {
            'agent_name': agent_name,
            'total_calls': len(calls),
            'total_input_tokens': total_input,
            'total_output_tokens': total_output,
            'total_tokens': total_tokens,
            'total_runtime': round(total_runtime, 2),
            'total_cost': round(total_cost, 4),
            'avg_tokens_per_call': round(total_tokens / len(calls), 0),
            'avg_runtime_per_call': round(total_runtime / len(calls), 2),
            'avg_cost_per_call': round(total_cost / len(calls), 4),
            'models_used': list(set(c.model for c in calls)),
            'providers_used': list(set(c.provider for c in calls))
        }
    
    def get_full_summary(self) -> Dict[str, Any]:
        """Get complete audit summary"""
        agent_summaries = {}
        
        for agent_name in self.per_agent.keys():
            agent_summaries[agent_name] = self.get_agent_summary(agent_name)
        
        # Sort agents by total cost
        sorted_agents = sorted(
            agent_summaries.items(),
            key=lambda x: x[1]['total_cost'],
            reverse=True
        )
        
        total_cost = sum(s['total_cost'] for s in agent_summaries.values())
        total_tokens = sum(s['total_tokens'] for s in agent_summaries.values())
        total_runtime = sum(s['total_runtime'] for s in agent_summaries.values())
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_calls': len(self.calls),
            'total_tokens': total_tokens,
            'total_runtime': round(total_runtime, 2),
            'total_cost': round(total_cost, 4),
            'per_agent': dict(sorted_agents),
            'ranked_by_cost': [
                {
                    'agent': agent,
                    'cost': summary['total_cost'],
                    'tokens': summary['total_tokens'],
                    'percentage_of_total_cost': round(
                        (summary['total_cost'] / total_cost * 100) if total_cost > 0 else 0,
                        1
                    )
                }
                for agent, summary in sorted_agents
            ],
            'ranked_by_tokens': sorted(
                [
                    {
                        'agent': agent,
                        'tokens': summary['total_tokens'],
                        'percentage_of_total_tokens': round(
                            (summary['total_tokens'] / total_tokens * 100) if total_tokens > 0 else 0,
                            1
                        )
                    }
                    for agent, summary in agent_summaries.items()
                ],
                key=lambda x: x['tokens'],
                reverse=True
            ),
            'ranked_by_runtime': sorted(
                [
                    {
                        'agent': agent,
                        'runtime': summary['total_runtime'],
                        'percentage_of_total_runtime': round(
                            (summary['total_runtime'] / total_runtime * 100) if total_runtime > 0 else 0,
                            1
                        )
                    }
                    for agent, summary in agent_summaries.items()
                ],
                key=lambda x: x['runtime'],
                reverse=True
            )
        }
    
    def print_summary(self):
        """Print human-readable summary"""
        summary = self.get_full_summary()
        
        print("\n" + "=" * 80)
        print("LLM AGENT AUDIT SUMMARY")
        print("=" * 80)
        
        print(f"\n📊 Overall Metrics:")
        print(f"   Total Calls: {summary['total_calls']}")
        print(f"   Total Tokens: {summary['total_tokens']:,}")
        print(f"   Total Runtime: {summary['total_runtime']:.2f}s")
        print(f"   Total Cost: ${summary['total_cost']:.4f}")
        
        print(f"\n💰 Ranked by Cost:")
        for item in summary['ranked_by_cost']:
            print(f"   {item['agent']:25} ${item['cost']:.4f} ({item['percentage_of_total_cost']}%)")
        
        print(f"\n🎫 Ranked by Tokens:")
        for item in summary['ranked_by_tokens']:
            print(f"   {item['agent']:25} {item['tokens']:,} tokens ({item['percentage_of_total_tokens']}%)")
        
        print(f"\n⏱️  Ranked by Runtime:")
        for item in summary['ranked_by_runtime']:
            print(f"   {item['agent']:25} {item['runtime']:.2f}s ({item['percentage_of_total_runtime']}%)")
        
        print(f"\n📋 Per-Agent Breakdown:")
        for agent_name, stats in summary['per_agent'].items():
            print(f"\n   {agent_name}:")
            print(f"      Calls: {stats['total_calls']}")
            print(f"      Input tokens: {stats['total_input_tokens']:,}")
            print(f"      Output tokens: {stats['total_output_tokens']:,}")
            print(f"      Total tokens: {stats['total_tokens']:,}")
            print(f"      Runtime: {stats['total_runtime']:.2f}s")
            print(f"      Cost: ${stats['total_cost']:.4f}")
            print(f"      Models: {', '.join(stats['models_used'])}")
    
    def save_report(self, filename: str = None):
        """Save detailed report to JSON"""
        if filename is None:
            filename = f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        os.makedirs('audit_results', exist_ok=True)
        filepath = f'audit_results/{filename}'
        
        summary = self.get_full_summary()
        
        # Add detailed call logs
        summary['detailed_calls'] = [asdict(call) for call in self.calls]
        
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📁 Detailed audit report saved to: {filepath}")
        return filepath


class AuditingLLMWrapper:
    """
    Wrapper that intercepts LLM calls and records metrics
    Non-intrusive - just observes and logs
    """
    
    def __init__(self, llm: Any, agent_name: str, collector: LLMAuditCollector,
                 provider: str = "unknown", model: str = "unknown"):
        self.llm = llm
        self.agent_name = agent_name
        self.collector = collector
        self.provider = provider
        self.model = model
        
        # Try to extract model/provider from LLM if not provided
        if hasattr(llm, 'model_name'):
            self.model = llm.model_name
        if hasattr(llm, 'provider'):
            self.provider = llm.provider
    
    def invoke(self, input_data: Any, config: Any = None, **kwargs) -> Any:
        """Intercept invoke call and record metrics"""
        
        # Extract prompt text
        if isinstance(input_data, str):
            prompt_text = input_data
        elif isinstance(input_data, dict) and 'input' in input_data:
            prompt_text = str(input_data['input'])
        elif isinstance(input_data, list):
            prompt_text = str(input_data)
        else:
            prompt_text = str(input_data)
        
        # Estimate input tokens
        estimated_input_tokens = TokenCounter.count_tokens(prompt_text)
        
        # Time the call
        start_time = time.time()
        
        # Make the actual LLM call
        response = self.llm.invoke(input_data, config, **kwargs)
        
        runtime = time.time() - start_time
        
        # Extract response text
        if hasattr(response, 'content'):
            response_text = response.content
        elif isinstance(response, str):
            response_text = response
        else:
            response_text = str(response)
        
        # Get token counts
        input_tokens, output_tokens = TokenCounter.extract_from_response(response)
        
        # Fall back to estimation if not provided
        if input_tokens == 0:
            input_tokens = estimated_input_tokens
        if output_tokens == 0:
            output_tokens = TokenCounter.count_tokens(response_text)
        
        total_tokens = input_tokens + output_tokens
        
        # Estimate cost
        cost = CostEstimator.estimate_cost(
            self.provider,
            self.model,
            input_tokens,
            output_tokens
        )
        
        # Record metrics
        metrics = LLMCallMetrics(
            agent_name=self.agent_name,
            timestamp=datetime.now().isoformat(),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            runtime_seconds=round(runtime, 3),
            model=self.model,
            provider=self.provider,
            estimated_cost_usd=cost,
            prompt_preview=prompt_text[:100] if prompt_text else "",
            response_preview=response_text[:100] if response_text else ""
        )
        
        self.collector.record_call(metrics)
        
        return response
    
    def __getattr__(self, name):
        """Forward all other attributes to wrapped LLM"""
        return getattr(self.llm, name)


# Global collector instance
_global_collector = None

def get_audit_collector() -> LLMAuditCollector:
    """Get or create global audit collector"""
    global _global_collector
    if _global_collector is None:
        _global_collector = LLMAuditCollector()
    return _global_collector


def reset_audit_collector():
    """Reset global collector (for testing)"""
    global _global_collector
    _global_collector = LLMAuditCollector()


def create_auditing_llm(llm: Any, agent_name: str, 
                        provider: str = "unknown", 
                        model: str = "unknown") -> AuditingLLMWrapper:
    """
    Create an auditing wrapper for an LLM
    
    Args:
        llm: The LLM instance to wrap
        agent_name: Name of the agent using this LLM
        provider: Provider name (cerebras, openrouter, etc.)
        model: Model name
    
    Returns:
        Wrapped LLM that logs all calls
    """
    collector = get_audit_collector()
    return AuditingLLMWrapper(llm, agent_name, collector, provider, model)
