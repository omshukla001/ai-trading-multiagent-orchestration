# TradingAgents/graph/setup.py

import os
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from tradingagents.agents import (
    create_aggressive_debator,
    create_bear_researcher,
    create_bull_researcher,
    create_conservative_debator,
    create_fundamentals_analyst,
    create_market_analyst,
    create_msg_delete,
    create_neutral_debator,
    create_news_analyst,
    create_portfolio_manager,
    create_research_manager,
    create_sentiment_analyst,
    create_trader,
)
from tradingagents.agents.utils.agent_states import AgentState

from .analyst_execution import build_analyst_execution_plan
from .conditional_logic import ConditionalLogic

# Conditional import for optimized analysts
USE_OPTIMIZED = os.environ.get('USE_OPTIMIZED_ANALYSTS', '0') == '1'

# Conditional import for optimized risk engine
USE_OPTIMIZED_RISK = os.environ.get('USE_OPTIMIZED_RISK', '0') == '1'

if USE_OPTIMIZED:
    print("🚀 Using OPTIMIZED Python-based analysts (0 LLM calls)")
    from tradingagents.agents.analysts.market_analyst_optimized import create_market_analyst_optimized
    from tradingagents.agents.analysts.fundamentals_analyst_optimized import create_fundamentals_analyst_optimized
else:
    print("📊 Using ORIGINAL LLM-based analysts")

if USE_OPTIMIZED_RISK:
    print("⚡ Using OPTIMIZED Python-based Risk Engine (0 LLM calls)")
    from tradingagents.agents.risk_mgmt import create_risk_engine
else:
    print("🎲 Using ORIGINAL LLM-based Risk Debate (3 agents)")


class GraphSetup:
    """Handles the setup and configuration of the agent graph."""

    def __init__(
        self,
        quick_thinking_llm: Any,
        deep_thinking_llm: Any,
        tool_nodes: dict[str, ToolNode],
        conditional_logic: ConditionalLogic,
    ):
        """Initialize with required components."""
        self.quick_thinking_llm = quick_thinking_llm
        self.deep_thinking_llm = deep_thinking_llm
        self.tool_nodes = tool_nodes
        self.conditional_logic = conditional_logic
        
        # Check if multi-provider routing is enabled
        self.multi_provider_enabled = os.environ.get('ENABLE_MULTI_PROVIDER', 'false').lower() == 'true'
    
    def _get_llm_for_agent(self, agent_name: str) -> Any:
        """
        Get LLM for an agent, with optional provider routing.
        
        Args:
            agent_name: Exact agent node name
            
        Returns:
            LLM client (routed if multi-provider enabled, default otherwise)
        """
        if self.multi_provider_enabled:
            from tradingagents.llm_clients.provider_router import get_router, create_routed_llm
            router = get_router()
            
            if router.should_use_routing(agent_name):
                return create_routed_llm(agent_name, router)
        
        # Fallback to default LLM
        return self.quick_thinking_llm

    def setup_graph(
        self, selected_analysts=("market", "social", "news", "fundamentals")
    ):
        """Set up and compile the agent workflow graph.

        Args:
            selected_analysts (list): List of analyst types to include. Options are:
                - "market": Market analyst
                - "social": Social media analyst
                - "news": News analyst
                - "fundamentals": Fundamentals analyst
        """
        plan = build_analyst_execution_plan(selected_analysts)

        # Use optimized analysts if environment variable is set
        if USE_OPTIMIZED:
            analyst_factories = {
                "market": lambda: create_market_analyst_optimized(),
                "social": lambda: create_sentiment_analyst(self.quick_thinking_llm),
                "news": lambda: create_news_analyst(self._get_llm_for_agent("News Analyst")),
                "fundamentals": lambda: create_fundamentals_analyst_optimized(),
            }
        else:
            # Instrument News Analyst if audit mode is enabled
            enable_audit = os.environ.get('AUDIT_MODE', 'false').lower() == 'true'
            
            if enable_audit:
                try:
                    import sys
                    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                    from audit_framework import create_auditing_llm
                    news_llm = create_auditing_llm(
                        self._get_llm_for_agent("News Analyst"),
                        "News Analyst", 
                        "groq", 
                        "llama-3.3-70b"
                    )
                except ImportError:
                    news_llm = self._get_llm_for_agent("News Analyst")
            else:
                news_llm = self._get_llm_for_agent("News Analyst")
            
            analyst_factories = {
                "market": lambda: create_market_analyst(self.quick_thinking_llm),
                "social": lambda: create_sentiment_analyst(self.quick_thinking_llm),
                "news": lambda: create_news_analyst(news_llm),
                "fundamentals": lambda: create_fundamentals_analyst(self.quick_thinking_llm),
            }

        # Create researcher and manager nodes
        # Multi-provider routing support
        enable_routing = os.environ.get('ENABLE_MULTI_PROVIDER', 'false').lower() == 'true'
        enable_audit = os.environ.get('AUDIT_MODE', 'false').lower() == 'true'
        
        # Conditionally import audit framework
        if enable_audit:
            try:
                import sys
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                from audit_framework import create_auditing_llm
                print("🔍 AUDIT MODE ENABLED: Instrumenting LLM agents")
            except ImportError as e:
                print(f"⚠️  Audit framework not found: {e}")
                enable_audit = False
        
        if enable_routing:
            from tradingagents.llm_clients.provider_router import get_router, create_routed_llm
            
            router = get_router()
            
            # Create LLMs with provider routing
            bull_llm_base = create_routed_llm("Bull Researcher", router)
            bear_llm_base = create_routed_llm("Bear Researcher", router)
            manager_llm_base = create_routed_llm("Research Manager", router)
            trader_llm_base = create_routed_llm("Trader", router)
            pm_llm_base = create_routed_llm("Portfolio Manager", router)
            
            # Wrap with audit if enabled
            if enable_audit:
                bull_llm = create_auditing_llm(bull_llm_base, "Bull Researcher", "routed", "routed")
                bear_llm = create_auditing_llm(bear_llm_base, "Bear Researcher", "routed", "routed")
                manager_llm = create_auditing_llm(manager_llm_base, "Research Manager", "routed", "routed")
                trader_llm = create_auditing_llm(trader_llm_base, "Trader", "routed", "routed")
                pm_llm = create_auditing_llm(pm_llm_base, "Portfolio Manager", "routed", "routed")
            else:
                bull_llm = bull_llm_base
                bear_llm = bear_llm_base
                manager_llm = manager_llm_base
                trader_llm = trader_llm_base
                pm_llm = pm_llm_base
            
            bull_researcher_node = create_bull_researcher(bull_llm)
            bear_researcher_node = create_bear_researcher(bear_llm)
            research_manager_node = create_research_manager(manager_llm)
            trader_node = create_trader(trader_llm)
            portfolio_manager_node = create_portfolio_manager(pm_llm)
        else:
            # Original single-provider setup
            quick_llm = self.quick_thinking_llm
            deep_llm = self.deep_thinking_llm
            
            # Wrap with audit if enabled
            if enable_audit:
                bull_llm = create_auditing_llm(quick_llm, "Bull Researcher", "groq", "llama-3.3-70b")
                bear_llm = create_auditing_llm(quick_llm, "Bear Researcher", "groq", "llama-3.3-70b")
                manager_llm = create_auditing_llm(deep_llm, "Research Manager", "groq", "llama-3.3-70b")
                trader_llm = create_auditing_llm(quick_llm, "Trader", "groq", "llama-3.3-70b")
                pm_llm = create_auditing_llm(deep_llm, "Portfolio Manager", "groq", "llama-3.3-70b")
            else:
                bull_llm = quick_llm
                bear_llm = quick_llm
                manager_llm = deep_llm
                trader_llm = quick_llm
                pm_llm = deep_llm
            
            bull_researcher_node = create_bull_researcher(bull_llm)
            bear_researcher_node = create_bear_researcher(bear_llm)
            research_manager_node = create_research_manager(manager_llm)
            trader_node = create_trader(trader_llm)
            portfolio_manager_node = create_portfolio_manager(pm_llm)
        
        # Create risk analysis nodes - use optimized or original
        if USE_OPTIMIZED_RISK:
            risk_engine_node = create_risk_engine()
        else:
            aggressive_analyst = create_aggressive_debator(self.quick_thinking_llm)
            neutral_analyst = create_neutral_debator(self.quick_thinking_llm)
            conservative_analyst = create_conservative_debator(self.quick_thinking_llm)

        # Create workflow
        workflow = StateGraph(AgentState)

        # Add analyst nodes to the graph
        for spec in plan.specs:
            workflow.add_node(spec.agent_node, analyst_factories[spec.key]())
            workflow.add_node(spec.clear_node, create_msg_delete())
            workflow.add_node(spec.tool_node, self.tool_nodes[spec.key])

        # Add other nodes
        workflow.add_node("Bull Researcher", bull_researcher_node)
        workflow.add_node("Bear Researcher", bear_researcher_node)
        workflow.add_node("Research Manager", research_manager_node)
        workflow.add_node("Trader", trader_node)
        
        # Add risk analysis nodes - conditional on optimization
        if USE_OPTIMIZED_RISK:
            workflow.add_node("Risk Engine", risk_engine_node)
        else:
            workflow.add_node("Aggressive Analyst", aggressive_analyst)
            workflow.add_node("Neutral Analyst", neutral_analyst)
            workflow.add_node("Conservative Analyst", conservative_analyst)
        
        workflow.add_node("Portfolio Manager", portfolio_manager_node)

        # Define edges
        # Start with the first analyst
        workflow.add_edge(START, plan.specs[0].agent_node)

        # Connect analysts in sequence
        for i, spec in enumerate(plan.specs):
            current_analyst = spec.agent_node
            current_tools = spec.tool_node
            current_clear = spec.clear_node

            # Add conditional edges for current analyst
            workflow.add_conditional_edges(
                current_analyst,
                getattr(self.conditional_logic, f"should_continue_{spec.key}"),
                [current_tools, current_clear],
            )
            workflow.add_edge(current_tools, current_analyst)

            # Connect to next analyst or to Bull Researcher if this is the last analyst
            if i < len(plan.specs) - 1:
                workflow.add_edge(current_clear, plan.specs[i + 1].agent_node)
            else:
                workflow.add_edge(current_clear, "Bull Researcher")

        # Add remaining edges
        workflow.add_conditional_edges(
            "Bull Researcher",
            self.conditional_logic.should_continue_debate,
            {
                "Bear Researcher": "Bear Researcher",
                "Research Manager": "Research Manager",
            },
        )
        workflow.add_conditional_edges(
            "Bear Researcher",
            self.conditional_logic.should_continue_debate,
            {
                "Bull Researcher": "Bull Researcher",
                "Research Manager": "Research Manager",
            },
        )
        workflow.add_edge("Research Manager", "Trader")
        
        # Add risk analysis edges - conditional on optimization
        if USE_OPTIMIZED_RISK:
            # Direct path: Trader -> Risk Engine -> Portfolio Manager
            workflow.add_edge("Trader", "Risk Engine")
            workflow.add_edge("Risk Engine", "Portfolio Manager")
        else:
            # Original path: Trader -> 3-way debate -> Portfolio Manager
            workflow.add_edge("Trader", "Aggressive Analyst")
            workflow.add_conditional_edges(
                "Aggressive Analyst",
                self.conditional_logic.should_continue_risk_analysis,
                {
                    "Conservative Analyst": "Conservative Analyst",
                    "Portfolio Manager": "Portfolio Manager",
                },
            )
            workflow.add_conditional_edges(
                "Conservative Analyst",
                self.conditional_logic.should_continue_risk_analysis,
                {
                    "Neutral Analyst": "Neutral Analyst",
                    "Portfolio Manager": "Portfolio Manager",
                },
            )
            workflow.add_conditional_edges(
                "Neutral Analyst",
                self.conditional_logic.should_continue_risk_analysis,
                {
                    "Aggressive Analyst": "Aggressive Analyst",
                    "Portfolio Manager": "Portfolio Manager",
                },
            )

        workflow.add_edge("Portfolio Manager", END)

        return workflow
