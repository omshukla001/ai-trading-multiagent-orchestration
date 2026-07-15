"""
Test Audit Framework - Verify Instrumentation

This script tests that the audit framework is correctly instrumenting LLM calls.
Uses a mock/minimal test to avoid rate limits.
"""

import os
import sys

# Enable audit mode
os.environ['AUDIT_MODE'] = '1'
os.environ['USE_OPTIMIZED_ANALYSTS'] = '1'
os.environ['USE_OPTIMIZED_RISK'] = '1'

from audit_framework import (
    get_audit_collector,
    reset_audit_collector,
    create_auditing_llm
)


class MockLLM:
    """Mock LLM for testing audit framework"""
    
    def __init__(self, name="mock"):
        self.name = name
        self.model_name = "mock-model-3"
        self.provider = "mock-provider"
    
    def invoke(self, input_data, config=None, **kwargs):
        """Mock invoke that returns a simple response"""
        
        class MockResponse:
            def __init__(self):
                self.content = "This is a mock response from the LLM. " * 10
                self.response_metadata = {
                    'usage': {
                        'prompt_tokens': 150,
                        'completion_tokens': 75
                    }
                }
        
        return MockResponse()


def test_audit_framework():
    """Test that audit framework correctly captures metrics"""
    
    print("=" * 80)
    print("AUDIT FRAMEWORK TEST")
    print("=" * 80)
    
    # Reset collector
    reset_audit_collector()
    collector = get_audit_collector()
    
    # Create mock LLMs for each agent
    agents = [
        ("Bull Researcher", "cerebras", "gpt-oss-120b"),
        ("Bear Researcher", "cerebras", "gpt-oss-120b"),
        ("Research Manager", "openrouter", "qwen3-next-80b"),
        ("Trader", "openrouter", "nemotron-3-super"),
        ("Portfolio Manager", "openrouter", "gpt-oss-120b"),
        ("News Analyst", "groq", "llama-3.3-70b")
    ]
    
    print("\n🔧 Creating instrumented LLM agents...")
    
    for agent_name, provider, model in agents:
        print(f"   - {agent_name}")
        
        # Create mock LLM
        mock_llm = MockLLM(agent_name)
        
        # Wrap with audit
        audited_llm = create_auditing_llm(
            llm=mock_llm,
            agent_name=agent_name,
            provider=provider,
            model=model
        )
        
        # Make a test call
        prompt = f"Test prompt for {agent_name}. " * 20
        audited_llm.invoke(prompt)
    
    print(f"\n✅ All agents instrumented and tested\n")
    
    # Generate report
    print("=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    
    collector.print_summary()
    
    # Save report
    filepath = collector.save_report("test_audit_report.json")
    
    # Verify we collected data
    summary = collector.get_full_summary()
    
    print(f"\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    print(f"\n✅ Total calls recorded: {summary['total_calls']}")
    print(f"✅ Agents instrumented: {len(summary['per_agent'])}")
    print(f"✅ Total tokens: {summary['total_tokens']:,}")
    print(f"✅ Total cost: ${summary['total_cost']:.4f}")
    
    expected_agents = 6
    if summary['total_calls'] == expected_agents:
        print(f"\n✅ SUCCESS: All {expected_agents} agents recorded")
        return True
    else:
        print(f"\n❌ FAILURE: Expected {expected_agents} calls, got {summary['total_calls']}")
        return False


def test_graph_instrumentation():
    """Test that graph setup correctly instruments agents"""
    
    print("\n" + "=" * 80)
    print("GRAPH INSTRUMENTATION TEST")
    print("=" * 80)
    
    print("\n📊 Checking if graph setup has audit support...")
    
    # Check if setup.py has audit code
    setup_path = "tradingagents/graph/setup.py"
    
    try:
        with open(setup_path, 'r') as f:
            content = f.read()
            
            has_audit_check = 'AUDIT_MODE' in content
            has_audit_import = 'audit_framework' in content
            has_audit_wrapper = 'create_auditing_llm' in content
            
            print(f"   AUDIT_MODE check: {'✅' if has_audit_check else '❌'}")
            print(f"   audit_framework import: {'✅' if has_audit_import else '❌'}")
            print(f"   create_auditing_llm usage: {'✅' if has_audit_wrapper else '❌'}")
            
            if has_audit_check and has_audit_import and has_audit_wrapper:
                print(f"\n✅ Graph setup is correctly instrumented!")
                return True
            else:
                print(f"\n⚠️  Graph setup is missing some instrumentation")
                return False
                
    except FileNotFoundError:
        print(f"❌ Could not find {setup_path}")
        return False


def main():
    """Run all tests"""
    
    print("\n" + "=" * 80)
    print("AUDIT FRAMEWORK VERIFICATION")
    print("=" * 80)
    print("\nThis test verifies that:")
    print("1. Audit framework correctly captures LLM metrics")
    print("2. Graph setup is instrumented to use audit framework")
    print("3. Reports are generated correctly")
    
    # Test 1: Framework functionality
    test1_passed = test_audit_framework()
    
    # Test 2: Graph instrumentation
    test2_passed = test_graph_instrumentation()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    print(f"\nFramework Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Graph Instrumentation: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print(f"\n✅ ALL TESTS PASSED")
        print(f"\nNext step: Run audit on real stock")
        print(f"   python run_audit.py")
        return 0
    else:
        print(f"\n❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
