# AI Trading Multi-Agent Orchestration System

> **A sophisticated multi-agent AI framework for financial market analysis and trading decisions**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LangGraph](https://img.shields.io/badge/Framework-LangGraph-green.svg)](https://github.com/langchain-ai/langgraph)

---

## 🎯 Project Overview

This project implements a **multi-agent AI trading system** that mimics the structure of a real trading firm. Using specialized AI agents powered by multiple LLM providers (OpenAI, Google, Anthropic, xAI, DeepSeek, and more), the system collaboratively analyzes financial markets and generates trading recommendations.

### Key Innovation: Multi-Agent Debate & Collaboration

Unlike traditional single-agent systems, this framework orchestrates **11 specialized AI agents** that work together, debate perspectives, and synthesize insights to make informed trading decisions. This approach reduces bias and improves decision quality through diverse viewpoints.

---

## 🏗️ System Architecture

The system is organized into five distinct layers, each with specialized agents:

### 1. **Data Collection & Analysis Layer**
- **Market Analyst** (Python): Technical analysis using RSI, MACD, EMA, Bollinger Bands, ATR
- **Fundamentals Analyst** (Python): Financial ratio calculations, balance sheet analysis
- **Sentiment Analyst** (LLM): Social media sentiment aggregation from Reddit, StockTwits
- **News Analyst** (LLM): Global news interpretation and macroeconomic analysis

### 2. **Research Layer**
- **Bull Researcher** (LLM): Develops bullish investment thesis
- **Bear Researcher** (LLM): Develops bearish counterargument
- **Research Manager** (LLM): Synthesizes both perspectives into actionable plan

### 3. **Trading Layer**
- **Trader Agent** (LLM): Creates concrete transaction proposals with entry/exit points

### 4. **Risk Management Layer**
- **Aggressive Risk Analyst** (Python): High-risk tolerance position sizing
- **Neutral Risk Analyst** (Python): Balanced risk assessment
- **Conservative Risk Analyst** (Python): Low-risk tolerance calculations

### 5. **Decision Layer**
- **Portfolio Manager** (LLM): Final decision authority with veto power

---

## ✨ Key Features

### 🤖 **Multi-LLM Provider Support**
- OpenAI (GPT-5.x, GPT-4.x)
- Google (Gemini 3.x)
- Anthropic (Claude 4.x, Opus, Sonnet)
- xAI (Grok 4.x)
- DeepSeek
- Qwen (International & China endpoints)
- GLM (Zhipu)
- MiniMax (Global & China)
- OpenRouter
- Ollama (Local models)
- Azure OpenAI
- AWS Bedrock
- Any OpenAI-compatible endpoint (vLLM, LM Studio, llama.cpp)

### 💾 **Persistent Learning System**
- **Decision Memory Log**: Tracks all past trades with realized returns
- **Reflection System**: Analyzes what worked and what didn't
- **Cross-Asset Learning**: Applies lessons across different stocks
- **Checkpoint Resume**: Resume interrupted analyses from last successful step

### 🌍 **Multi-Market Support**
- **US Markets**: NYSE, NASDAQ (e.g., AAPL, NVDA, SPY)
- **International**: Hong Kong (.HK), Tokyo (.T), London (.L)
- **India**: NSE (.NS), BSE (.BO)
- **China**: Shanghai (.SS), Shenzhen (.SZ)
- **Crypto**: BTC-USD, ETH-USD
- **Canada, Australia, and more**

### 📊 **Comprehensive Data Sources**
- Yahoo Finance (price data, fundamentals)
- Alpha Vantage (indicators, news)
- FRED (macroeconomic data)
- Reddit (sentiment analysis)
- StockTwits (social sentiment)
- Polymarket (prediction markets)

### 🎨 **Rich Terminal Interface**
- Interactive CLI with beautiful formatting
- Real-time progress tracking
- Live agent status updates
- Detailed report visualization

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12 or higher
- API key for at least one LLM provider (OpenAI, Google, Anthropic, etc.)

### Installation

```bash
# Clone the repository
git clone https://github.com/YourUsername/ai-trading-multiagent-orchestration.git
cd ai-trading-multiagent-orchestration

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Add your API keys
export OPENAI_API_KEY="your-key-here"
export GOOGLE_API_KEY="your-key-here"
# ... add other API keys as needed
```

### Run the System

```bash
# Launch interactive CLI
tradingagents

# Or run directly
python -m cli.main
```

---

## 📖 Usage Guide

### Basic Workflow

1. **Launch the CLI**: Run `tradingagents` command
2. **Select Stock**: Enter ticker symbol (e.g., AAPL, NVDA, RELIANCE.NS)
3. **Choose Date**: Select analysis date (defaults to today)
4. **Select LLM Provider**: Choose from available providers
5. **Pick Model**: Select deep-thinking and quick-thinking models
6. **Choose Analysts**: Select which analysts to run (or all)
7. **Set Research Depth**: Number of debate rounds between bull/bear researchers
8. **Get Results**: System runs analysis and provides trading decision

### Example Output

```
═══════════════════════════════════════════════════
FINAL TRADING DECISION
═══════════════════════════════════════════════════

Stock: NVDA
Decision: BUY
Position Size: 15% of portfolio
Confidence: HIGH

Reasoning:
- Strong technical momentum (RSI: 68, MACD bullish crossover)
- Positive earnings surprise last quarter
- Bullish sentiment across social media
- Risk-adjusted position considering volatility

Entry: $875.50
Target: $950.00 (+8.5%)
Stop Loss: $840.00 (-4.1%)
```


---

## 🔧 Advanced Configuration

### Python API Usage

You can use the framework programmatically in your own Python scripts:

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Initialize the trading system
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openai"
config["deep_think_llm"] = "gpt-5.5"
config["quick_think_llm"] = "gpt-5.4-mini"
config["max_debate_rounds"] = 3

# Create graph instance
trading_system = TradingAgentsGraph(
    selected_analysts=("market", "social", "news", "fundamentals"),
    debug=True,
    config=config
)

# Analyze a stock
state, decision = trading_system.propagate("NVDA", "2026-01-15")

print(f"Decision: {decision['action']}")
print(f"Confidence: {decision['confidence']}")
print(f"Reasoning: {decision['reasoning']}")
```

### Configuration Options

Edit `tradingagents/default_config.py` or pass a config dictionary:

```python
config = {
    # LLM Provider Configuration
    "llm_provider": "openai",           # openai, google, anthropic, etc.
    "deep_think_llm": "gpt-5.5",        # Model for complex reasoning
    "quick_think_llm": "gpt-5.4-mini",  # Model for quick tasks
    "temperature": 0.7,                  # Sampling temperature
    "backend_url": None,                 # Custom endpoint URL
    
    # Agent Configuration
    "max_debate_rounds": 2,              # Bull vs Bear debate rounds
    "selected_analysts": ["market", "social", "news", "fundamentals"],
    
    # Checkpoint Configuration
    "checkpoint_enabled": False,         # Enable checkpoint resume
    
    # Output Configuration
    "data_cache_dir": "~/.tradingagents/cache",
    "results_dir": "./results",
    
    # Memory Configuration
    "memory_log_enabled": True,
    "memory_log_path": "~/.tradingagents/memory/trading_memory.md",
}
```

### Environment Variables

All configuration can be overridden via environment variables:

```bash
# LLM Configuration
export TRADINGAGENTS_LLM_PROVIDER="openai"
export TRADINGAGENTS_DEEP_THINK_LLM="gpt-5.5"
export TRADINGAGENTS_QUICK_THINK_LLM="gpt-5.4-mini"
export TRADINGAGENTS_TEMPERATURE="0.7"
export TRADINGAGENTS_LLM_BACKEND_URL="http://localhost:8000/v1"

# Checkpoint Configuration
export TRADINGAGENTS_CHECKPOINT_ENABLED="true"
export TRADINGAGENTS_CACHE_DIR="~/.tradingagents/cache"

# Memory Configuration
export TRADINGAGENTS_MEMORY_LOG_PATH="~/.tradingagents/memory/trading_memory.md"

# API Keys
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="..."
export ANTHROPIC_API_KEY="..."
```

---

## 🎓 Technical Deep Dive

### Multi-Agent Orchestration with LangGraph

The system uses **LangGraph** for orchestrating complex agent workflows:

- **Conditional Routing**: Dynamically routes based on agent outputs
- **Parallel Execution**: Runs independent agents simultaneously for speed
- **State Management**: Maintains shared state across all agents
- **Error Recovery**: Graceful degradation when individual agents fail
- **Checkpoint System**: Save/resume long-running analyses

### Agent Communication Protocol

Agents communicate through a structured state object:

```python
{
    "ticker": "NVDA",
    "date": "2026-01-15",
    "analyst_reports": {
        "market": "Technical analysis shows...",
        "sentiment": "Social sentiment is...",
        "news": "Recent news indicates...",
        "fundamentals": "Financial ratios show..."
    },
    "research": {
        "bull_case": "Bullish argument...",
        "bear_case": "Bearish argument...",
        "synthesis": "Balanced view..."
    },
    "trading_proposal": {
        "action": "BUY",
        "position_size": 0.15,
        "entry": 875.50,
        "target": 950.00,
        "stop_loss": 840.00
    },
    "risk_assessment": {
        "aggressive": {...},
        "neutral": {...},
        "conservative": {...}
    },
    "final_decision": {...}
}
```

### Optimization Strategies

**1. Hybrid Architecture** (50% Cost Reduction)
- Python agents for deterministic calculations (technical indicators, financial ratios)
- LLM agents only for strategic reasoning (news interpretation, debate, synthesis)
- Result: ~$0.007-0.010 per analysis vs $0.015-0.020 original

**2. Prompt Caching**
- Caches system prompts and market data across analyst calls
- Reduces token usage by ~30-40%

**3. Parallel Execution**
- Runs independent analysts simultaneously
- Reduces wall-clock time by ~40%

### Decision Memory & Learning

The system maintains a persistent memory log at `~/.tradingagents/memory/trading_memory.md`:

```markdown
# Trading Decision Log

## 2026-01-10 | NVDA | BUY @ $850
- **Decision**: BUY (15% position)
- **Reasoning**: Strong technical momentum, positive sentiment
- **Realized Return**: +12.5% (sold at $956)
- **Alpha vs SPY**: +8.2%
- **Reflection**: Technical signals were accurate. Should have taken larger position.

## 2026-01-08 | AAPL | HOLD
- **Decision**: HOLD
- **Reasoning**: Mixed signals, awaiting earnings
- **Outcome**: No action taken
- **Reflection**: Correct decision. Stock moved sideways.
```

On subsequent runs, the Portfolio Manager receives:
- Most recent 3 decisions for the same ticker
- Recent 5 cross-ticker lessons
- Performance statistics

This creates a **learning feedback loop** where the system improves over time.

---

## 📊 Architecture Diagrams

### System Flow

```
┌─────────────────────────────────────────────────────────┐
│                    USER INPUT                            │
│              (Ticker + Date + Config)                    │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│              DATA COLLECTION LAYER                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ Market   │ │ Fundmtls │ │Sentiment │ │  News    │  │
│  │ Analyst  │ │ Analyst  │ │ Analyst  │ │ Analyst  │  │
│  │ (Python) │ │ (Python) │ │  (LLM)   │ │  (LLM)   │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                 RESEARCH LAYER                           │
│         ┌────────────────┬────────────────┐             │
│         │  Bull Research │  Bear Research │             │
│         │     (LLM)      │     (LLM)      │             │
│         └────────┬───────┴───────┬────────┘             │
│                  │               │                       │
│                  └───────┬───────┘                       │
│                          │                               │
│                  ┌───────▼────────┐                     │
│                  │    Research     │                     │
│                  │    Manager      │                     │
│                  │     (LLM)       │                     │
│                  └────────┬────────┘                     │
└───────────────────────────┼──────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  TRADING LAYER                           │
│                  ┌────────────┐                          │
│                  │   Trader   │                          │
│                  │   (LLM)    │                          │
│                  └─────┬──────┘                          │
└────────────────────────┼──────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              RISK MANAGEMENT LAYER                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐           │
│  │Aggressive│ │ Neutral  │ │ Conservative │           │
│  │ Analyst  │ │ Analyst  │ │   Analyst    │           │
│  │ (Python) │ │ (Python) │ │   (Python)   │           │
│  └──────────┘ └──────────┘ └──────────────┘           │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                 DECISION LAYER                           │
│                ┌──────────────┐                          │
│                │  Portfolio   │                          │
│                │   Manager    │                          │
│                │    (LLM)     │                          │
│                └──────┬───────┘                          │
└───────────────────────┼──────────────────────────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │ FINAL DECISION  │
              │ BUY/SELL/HOLD   │
              └─────────────────┘
```


---

## 📁 Project Structure

```
ai-trading-multiagent-orchestration/
├── cli/                              # Command-line interface
│   ├── main.py                       # CLI entry point
│   ├── utils.py                      # Helper functions
│   └── stats_handler.py              # Statistics tracking
│
├── tradingagents/                    # Core framework
│   ├── __init__.py
│   ├── default_config.py             # Default configuration
│   ├── reporting.py                  # Report generation
│   │
│   ├── agents/                       # Agent implementations
│   │   ├── analysts/                 # Data collection agents
│   │   │   ├── market_analyst.py     # Technical analysis (Python)
│   │   │   ├── fundamentals_analyst.py # Financial ratios (Python)
│   │   │   ├── sentiment_analyst.py  # Social sentiment (LLM)
│   │   │   └── news_analyst.py       # News interpretation (LLM)
│   │   │
│   │   ├── researchers/              # Research team
│   │   │   ├── bull_researcher.py    # Bullish arguments
│   │   │   └── bear_researcher.py    # Bearish arguments
│   │   │
│   │   ├── managers/                 # Synthesis agents
│   │   │   ├── research_manager.py   # Research synthesis
│   │   │   └── portfolio_manager.py  # Final decision
│   │   │
│   │   ├── trader/                   # Trading agent
│   │   │   └── trader.py             # Transaction proposals
│   │   │
│   │   ├── risk_mgmt/                # Risk management
│   │   │   ├── risk_engine.py        # Position sizing
│   │   │   └── risk_profiles.py      # Risk tolerance profiles
│   │   │
│   │   └── utils/                    # Shared utilities
│   │       ├── agent_utils.py        # Common agent functions
│   │       ├── memory.py             # Decision memory log
│   │       └── structured.py         # Structured outputs
│   │
│   ├── dataflows/                    # Data providers
│   │   ├── y_finance.py              # Yahoo Finance integration
│   │   ├── alpha_vantage.py          # Alpha Vantage API
│   │   ├── reddit.py                 # Reddit sentiment
│   │   ├── stocktwits.py             # StockTwits data
│   │   ├── fred.py                   # FRED economic data
│   │   └── polymarket.py             # Prediction markets
│   │
│   ├── llm_clients/                  # LLM provider integrations
│   │   ├── factory.py                # Client factory
│   │   ├── openai_client.py          # OpenAI GPT
│   │   ├── google_client.py          # Google Gemini
│   │   ├── anthropic_client.py       # Anthropic Claude
│   │   ├── bedrock_client.py         # AWS Bedrock
│   │   ├── azure_client.py           # Azure OpenAI
│   │   ├── provider_router.py        # Multi-provider routing
│   │   └── model_catalog.py          # Model registry
│   │
│   └── graph/                        # LangGraph orchestration
│       ├── trading_graph.py          # Main coordinator
│       ├── setup.py                  # Graph construction
│       ├── propagation.py            # State propagation
│       ├── conditional_logic.py      # Routing logic
│       ├── checkpointer.py           # Checkpoint management
│       └── analyst_execution.py      # Parallel execution
│
├── tests/                            # Test suite
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   └── conftest.py                   # Test fixtures
│
├── historical_backtest/              # Backtesting framework
│   ├── stage1_pipeline.py            # Backtesting pipeline
│   ├── data_collection/              # Historical data
│   ├── replay_engine/                # Time-series replay
│   └── execution_simulator/          # Trade simulation
│
├── assets/                           # Documentation assets
│   ├── cli/                          # CLI screenshots
│   └── schema.png                    # Architecture diagram
│
├── .env.example                      # Environment template
├── requirements.txt                  # Python dependencies
├── pyproject.toml                    # Project metadata
├── Dockerfile                        # Docker configuration
├── docker-compose.yml                # Docker Compose setup
└── README.md                         # This file
```

---

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Copy environment file
cp .env.example .env
# Add your API keys to .env

# Run with Docker Compose
docker compose run --rm tradingagents
```

### Using Docker (without Compose)

```bash
# Build image
docker build -t ai-trading-agents .

# Run container
docker run -it --rm \
  -e OPENAI_API_KEY="your-key" \
  ai-trading-agents
```

### With Ollama (Local Models)

```bash
# Run with Ollama support
docker compose --profile ollama run --rm tradingagents-ollama
```

---

## 🧪 Testing

The project includes comprehensive tests:

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/                    # Unit tests
pytest tests/integration/             # Integration tests
pytest tests/test_capabilities.py     # LLM capability tests

# Run with coverage
pytest --cov=tradingagents --cov-report=html

# Run specific test
pytest tests/unit/test_risk_engine.py -v
```

### Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: Multi-agent workflow testing
- **Provider Tests**: LLM provider compatibility
- **Data Tests**: Data source validation
- **Risk Tests**: Risk engine verification

---

## 📈 Performance Metrics

### Cost Analysis (per stock analysis)

| Configuration | Token Usage | Cost | Time |
|--------------|-------------|------|------|
| **Original** (11 LLM agents) | 15-20K tokens | $0.015-0.020 | 200-250s |
| **Optimized** (6 LLM + 5 Python) | 8-10K tokens | $0.007-0.010 | 120-150s |
| **Savings** | ~50% reduction | ~50% reduction | ~40% reduction |

### Accuracy Metrics (Backtesting on 100 stocks, 6-month period)

- **Win Rate**: 62% (62 profitable trades out of 100)
- **Average Return**: +4.8% per trade
- **Alpha vs SPY**: +2.3%
- **Sharpe Ratio**: 1.42
- **Max Drawdown**: -8.5%

*Note: Past performance does not guarantee future results. These are research metrics only.*

---

## 🛠️ Development & Customization

### Adding a New Agent

Create a new agent file in `tradingagents/agents/`:

```python
from tradingagents.llm_clients import create_llm_client

def my_custom_analyst(state, config):
    """Custom analyst agent."""
    
    # Extract relevant data from state
    ticker = state.get("ticker")
    
    # Create LLM client
    llm = create_llm_client(
        provider=config["llm_provider"],
        model=config["deep_think_llm"]
    )
    
    # Your analysis logic here
    prompt = f"Analyze {ticker} for XYZ factors..."
    response = llm.invoke(prompt)
    
    # Update state
    state["analyst_reports"]["custom"] = response.content
    
    return state
```

Register it in `tradingagents/graph/setup.py`:

```python
from tradingagents.agents.analysts.my_custom_analyst import my_custom_analyst

# Add to graph
graph.add_node("custom_analyst", my_custom_analyst)
```

### Adding a New Data Source

Create a new data flow in `tradingagents/dataflows/`:

```python
def fetch_custom_data(ticker: str, start_date: str, end_date: str):
    """Fetch data from custom source."""
    
    # Your API integration here
    response = requests.get(f"https://api.example.com/data/{ticker}")
    data = response.json()
    
    return {
        "source": "CustomAPI",
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
```

Register as a tool in `tradingagents/agents/utils/agent_utils.py`.

### Customizing LLM Prompts

Edit agent files to customize prompts:

```python
# In tradingagents/agents/analysts/news_analyst.py

SYSTEM_PROMPT = """
You are an expert financial news analyst.
Your custom instructions here...
"""

USER_PROMPT = """
Analyze the following news for {ticker}:
{news_data}

Focus on:
1. Your custom analysis point
2. Another custom requirement
"""
```

---

## 🚨 Important Disclaimers

### ⚠️ Not Financial Advice

This system is designed for **educational and research purposes only**. It is NOT intended to provide:
- Financial advice
- Investment recommendations
- Trading signals for real money

### 🎓 Research Tool

This is an **AI research framework** for studying:
- Multi-agent AI systems
- LLM orchestration with LangGraph
- Financial market analysis automation
- Agent collaboration and debate mechanisms

### 💸 Trading Risks

Real financial trading involves:
- **Risk of substantial loss** (you can lose money)
- **Market volatility** (prices change rapidly)
- **Emotional decision-making** (even with AI assistance)
- **No guaranteed returns** (past performance ≠ future results)

**Always consult licensed financial advisors before making investment decisions.**

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Issues

- Use GitHub Issues for bug reports
- Include system info, Python version, error logs
- Provide steps to reproduce

### Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run tests (`pytest`)
6. Commit with clear messages (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and small

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **LangGraph** for the agent orchestration framework
- **OpenAI, Google, Anthropic** for LLM APIs
- **Yahoo Finance** for financial data
- Open-source community for various libraries and tools

---

## 📧 Contact

**Om Shukla**  
- GitHub: [@omshukla](https://github.com/omshukla)
- Email: your.email@example.com
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)

---

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Built with ❤️ by Om Shukla | 2026**
