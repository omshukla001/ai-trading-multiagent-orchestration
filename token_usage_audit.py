#!/usr/bin/env python3
"""
Token Usage Audit for TradingAgents Workflow

Measures token usage and runtime for each LLM-dependent agent after optimized analysts.

Optimized (0 LLM calls):
- Market Analyst ✅
- Fundamentals Analyst ✅

Need to measure:
- News Analyst
- Social Media Analyst
- Bull Researcher
- Bear Researcher
- Research Manager
- Trader
- Aggressive Risk Analyst
- Neutral Risk Analyst
- Conservative Risk Analyst
- Portfolio Manager (Final Decision)
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List
from dataclasses import dataclass, field
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Import LangChain callback for token tracking
from langchain_core.callbacks import BaseCallbackHandler


@dataclass
class AgentMetrics:
    """Metrics for a single agent execution"""
    agent_name: str
    runtime_seconds: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    llm_calls: int = 0
    
    def add_tokens(self, input_tokens: int, output_tokens: int):
        """Add token counts from a single LLM call"""
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.total_tokens += (input_tokens + output_tokens)
        self.llm_calls += 1


class TokenTrackingCallback(BaseCallbackHandler):
    """Callback handler to track token usage per agent"""
    
    def __init__(self):
        self.metrics: Dict[str, AgentMetrics] = {}
        self.current_agent: str = None
        self.agent_start_time: float = None
        
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs):
        """Track when an agent/chain starts"""
        # Try to identify agent from metadata or node name
        run_name = kwargs.get('name', '')
        tags = kwargs.get('tags', [])
        
        # Common agent names
        agent_names = [
            'Market Analyst', 'News Analyst', 'Social Media Analyst',
            'Fundamentals Analyst', 'Bull Researcher', 'Bear Researcher',
            'Research Manager', 'Trader', 'Aggressive Analyst',
            'Neutral Analyst', 'Conservative Analyst', 'Portfolio Manager'
        ]
        
        for agent_name in agent_names:
            if agent_name.lower() in run_name.lower() or any(agent_name.lower() in tag.lower() for tag in tags):
                self.current_agent = agent_name
                self.agent_start_time = time.time()
                if agent_name not in self.metrics:
                    self.metrics[agent_name] = AgentMetrics(agent_name=agent_name)
                break
    
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs):
        """Track when an agent/chain ends"""
        if self.current_agent and self.agent_start_time:
            agent = self.metrics.get(self.current_agent)
            if agent:
                elapsed = time.time() - self.agent_start_time
                agent.runtime_seconds += elapsed
            self.current_agent = None
            self.agent_start_time = None
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs):
        """Track LLM call start"""
        pass
    
    def on_llm_end(self, response, **kwargs):
        """Track LLM call end and extract token usage"""
        if not self.current_agent:
            return
        
        agent = self.metrics.get(self.current_agent)
        if not agent:
            return
        
        # Extract token usage from response metadata
        try:
            # For OpenAI-compatible APIs
            if hasattr(response, 'llm_output') and response.llm_output:
                token_usage = response.llm_output.get('token_usage', {})
                input_tokens = token_usage.get('prompt_tokens', 0)
                output_tokens = token_usage.get('completion_tokens', 0)
                agent.add_tokens(input_tokens, output_tokens)
            
            # For other providers that might store differently
            elif hasattr(response, 'generations') and response.generations:
                for generation in response.generations:
                    for gen in generation:
                        if hasattr(gen, 'generation_info') and gen.generation_info:
                            usage = gen.generation_info.get('usage', {})
                            input_tokens = usage.get('input_tokens', 0) or usage.get('prompt_tokens', 0)
                            output_tokens = usage.get('output_tokens', 0) or usage.get('completion_tokens', 0)
                            if input_tokens or output_tokens:
                                agent.add_tokens(input_tokens, output_tokens)
        except Exception as e:
            print(f"⚠️  Warning: Could not extract token usage for {self.current_agent}: {e}")


class TokenUsageAuditor:
    """Audits token usage for TradingAgents workflow"""
    
    def __init__(self):
        self.test_stock = "HDFCBANK.NS"
        self.callback = TokenTrackingCallback()
        self.total_runtime = 0.0
        self.workflow_success = False
        self.error = None
        
    def run_audit(self, use_optimized: bool = True) -> Dict[str, Any]:
        """Run a single stock analysis with token tracking"""
        
        mode = "OPTIMIZED" if use_optimized else "ORIGINAL"
        print(f"\n{'='*80}")
        print(f"TOKEN USAGE AUDIT - {mode} Analysts")
        print(f"{'='*80}")
        print(f"\nStock: {self.test_stock}")
        print(f"Mode: {mode}")
        
        # Set environment variable for optimized analysts
        os.environ['USE_OPTIMIZED_ANALYSTS'] = '1' if use_optimized else '0'
        
        # Clear module cache
        for module in list(sys.modules.keys()):
            if 'tradingagents' in module:
                del sys.modules[module]
        
        try:
            from tradingagents.graph.trading_graph import TradingAgentsGraph
            from tradingagents.default_config import DEFAULT_CONFIG
            
            # Configure with Groq
            config = DEFAULT_CONFIG.copy()
            config["llm_provider"] = "groq"
            config["deep_think_llm"] = "llama-3.3-70b-versatile"
            config["quick_think_llm"] = "llama-3.3-70b-versatile"
            config["max_debate_rounds"] = 1
            config["max_risk_rounds"] = 1
            
            # Analysis date
            analysis_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
            
            print(f"\n🔄 Creating TradingAgentsGraph...")
            print(f"   Provider: {config['llm_provider']}")
            print(f"   Model: {config['deep_think_llm']}")
            print(f"   Analysis Date: {analysis_date}")
            
            # Create graph with callback
            ta = TradingAgentsGraph(debug=False, config=config, callbacks=[self.callback])
            
            print(f"\n🚀 Executing workflow with token tracking...")
            
            start_time = time.time()
            
            # Run the analysis
            final_state, decision = ta.propagate(self.test_stock, analysis_date)
            
            self.total_runtime = time.time() - start_time
            self.workflow_success = True
            
            print(f"\n✅ Workflow completed successfully in {self.total_runtime:.2f}s")
            
            if decision:
                print(f"\n📊 Decision:")
                print(f"   Action: {decision.get('action', 'N/A')}")
                print(f"   Confidence: {decision.get('confidence', 0):.2f}")
            
        except Exception as e:
            self.total_runtime = time.time() - start_time if 'start_time' in locals() else 0
            self.workflow_success = False
            self.error = str(e)
            print(f"\n❌ Workflow failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive token usage report"""
        
        print(f"\n{'='*80}")
        print("TOKEN USAGE REPORT")
        print(f"{'='*80}")
        
        # Sort agents by appearance in workflow
        agent_order = [
            'Market Analyst',
            'News Analyst',
            'Social Media Analyst',
            'Fundamentals Analyst',
            'Bull Researcher',
            'Bear Researcher',
            'Research Manager',
            'Trader',
            'Aggressive Analyst',
            'Neutral Analyst',
            'Conservative Analyst',
            'Portfolio Manager',
        ]
        
        # Create report table
        print(f"\n{'Agent':<30} {'Runtime':>10} {'Input':>12} {'Output':>12} {'Total':>12} {'Calls':>8}")
        print(f"{'-'*30} {'-'*10} {'-'*12} {'-'*12} {'-'*12} {'-'*8}")
        
        total_input = 0
        total_output = 0
        total_tokens = 0
        total_calls = 0
        
        report_data = []
        
        for agent_name in agent_order:
            metrics = self.callback.metrics.get(agent_name)
            if metrics:
                print(f"{agent_name:<30} {metrics.runtime_seconds:>9.2f}s "
                      f"{metrics.input_tokens:>12,} {metrics.output_tokens:>12,} "
                      f"{metrics.total_tokens:>12,} {metrics.llm_calls:>8}")
                
                total_input += metrics.input_tokens
                total_output += metrics.output_tokens
                total_tokens += metrics.total_tokens
                total_calls += metrics.llm_calls
                
                report_data.append({
                    'agent': agent_name,
                    'runtime': metrics.runtime_seconds,
                    'input_tokens': metrics.input_tokens,
                    'output_tokens': metrics.output_tokens,
                    'total_tokens': metrics.total_tokens,
                    'llm_calls': metrics.llm_calls,
                })
        
        print(f"{'-'*30} {'-'*10} {'-'*12} {'-'*12} {'-'*12} {'-'*8}")
        print(f"{'TOTAL':<30} {self.total_runtime:>9.2f}s "
              f"{total_input:>12,} {total_output:>12,} "
              f"{total_tokens:>12,} {total_calls:>8}")
        
        # Success criteria check
        print(f"\n{'='*80}")
        print("SUCCESS CRITERIA CHECK")
        print(f"{'='*80}")
        
        max_agent_input = max([m.input_tokens for m in self.callback.metrics.values()]) if self.callback.metrics else 0
        
        criteria = [
            ("Workflow completed", self.workflow_success),
            ("No agent exceeds 3k input tokens", max_agent_input < 3000),
            ("Total tokens under 10k", total_tokens < 10000),
            ("Total runtime acceptable (<120s)", self.total_runtime < 120),
        ]
        
        all_passed = True
        for criterion, passed in criteria:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status}: {criterion}")
            if not passed:
                all_passed = False
                if "input tokens" in criterion:
                    print(f"      → Max agent input: {max_agent_input:,} tokens")
                elif "Total tokens" in criterion:
                    print(f"      → Actual total: {total_tokens:,} tokens")
                elif "runtime" in criterion:
                    print(f"      → Actual runtime: {self.total_runtime:.2f}s")
        
        if all_passed:
            print(f"\n🎉 All success criteria passed!")
        else:
            print(f"\n⚠️  Some criteria failed - review needed")
        
        # Cost estimation (approximate for Groq)
        # Groq pricing: https://groq.com/pricing/
        # llama-3.3-70b: ~$0.59/M input tokens, ~$0.79/M output tokens
        input_cost = (total_input / 1_000_000) * 0.59
        output_cost = (total_output / 1_000_000) * 0.79
        total_cost = input_cost + output_cost
        
        print(f"\n{'='*80}")
        print("COST ESTIMATION (Groq Pricing)")
        print(f"{'='*80}")
        print(f"   Input cost:  ${input_cost:.4f} ({total_input:,} tokens)")
        print(f"   Output cost: ${output_cost:.4f} ({total_output:,} tokens)")
        print(f"   Total cost:  ${total_cost:.4f}")
        print(f"   Per stock:   ${total_cost:.4f}")
        print(f"   Per 100 stocks: ${total_cost * 100:.2f}")
        print(f"   Per 1000 stocks: ${total_cost * 1000:.2f}")
        
        return {
            'success': self.workflow_success,
            'error': self.error,
            'total_runtime': self.total_runtime,
            'total_input_tokens': total_input,
            'total_output_tokens': total_output,
            'total_tokens': total_tokens,
            'total_llm_calls': total_calls,
            'agents': report_data,
            'cost_estimate': {
                'input_cost': input_cost,
                'output_cost': output_cost,
                'total_cost': total_cost,
            },
            'criteria_passed': all_passed,
        }


def main():
    """Main execution"""
    
    print("\n" + "="*80)
    print("TRADINGAGENTS TOKEN USAGE AUDIT")
    print("="*80)
    print("\nPurpose: Measure token usage and runtime for remaining LLM-dependent agents")
    print("after optimizing Market and Fundamentals analysts.")
    print("\nTest Configuration:")
    print("   Stock: HDFCBANK.NS")
    print("   Provider: Groq (llama-3.3-70b-versatile)")
    print("   Debate Rounds: 1")
    print("   Risk Rounds: 1")
    print("="*80)
    
    # Check API key
    if not os.environ.get('GROQ_API_KEY'):
        print("\n❌ GROQ_API_KEY not found in environment")
        print("Please ensure .env file contains GROQ_API_KEY")
        sys.exit(1)
    
    auditor = TokenUsageAuditor()
    
    # Run audit with optimized analysts
    result = auditor.run_audit(use_optimized=True)
    
    # Save report
    output_dir = Path("token_usage_audit_results")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"token_audit_{timestamp}.json"
    
    import json
    with open(report_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Report saved to: {report_file}")
    
    print(f"\n{'='*80}")
    print("AUDIT COMPLETE")
    print(f"{'='*80}")
    
    if result['success']:
        print("\n✅ Token usage audit completed successfully")
        print(f"\nKey Metrics:")
        print(f"   Total tokens: {result['total_tokens']:,}")
        print(f"   Total runtime: {result['total_runtime']:.2f}s")
        print(f"   Cost per stock: ${result['cost_estimate']['total_cost']:.4f}")
        
        if result['criteria_passed']:
            print(f"\n🎉 Ready for 3-stock integration tests")
        else:
            print(f"\n⚠️  Review criteria failures before proceeding")
    else:
        print(f"\n❌ Audit failed: {result['error']}")
        print(f"Review error details and retry")
    
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
