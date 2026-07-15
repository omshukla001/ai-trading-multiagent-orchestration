# Contributing to AI Trading Multi-Agent Orchestration

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- Git
- Virtual environment tool (venv, conda, etc.)

### Development Setup

1. **Fork and Clone**
```bash
git clone https://github.com/YourUsername/ai-trading-multiagent-orchestration.git
cd ai-trading-multiagent-orchestration
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -e ".[dev]"
```

4. **Run Tests**
```bash
pytest
```

## 🐛 Reporting Bugs

When reporting bugs, please include:
- **Python version** (`python --version`)
- **Operating system** (Windows, macOS, Linux)
- **Steps to reproduce** the issue
- **Expected behavior**
- **Actual behavior**
- **Error messages** and stack traces
- **Configuration** (LLM provider, model, etc.)

## 💡 Suggesting Features

Feature requests are welcome! Please:
- Check existing issues to avoid duplicates
- Clearly describe the feature and its use case
- Explain why this feature would be useful
- Provide examples if possible

## 🔧 Development Guidelines

### Code Style
- Follow **PEP 8** style guide
- Use **type hints** where appropriate
- Write **docstrings** for all public functions and classes
- Keep functions focused and under 50 lines when possible
- Use meaningful variable and function names

### Testing
- Write tests for new features
- Maintain or improve code coverage
- Run full test suite before submitting PR
- Include both unit tests and integration tests

### Commits
- Use clear, descriptive commit messages
- Follow conventional commit format:
  - `feat:` new feature
  - `fix:` bug fix
  - `docs:` documentation changes
  - `refactor:` code refactoring
  - `test:` adding or updating tests
  - `chore:` maintenance tasks

Example:
```
feat: add support for Gemini 3.5 model
fix: resolve checkpoint resume issue for long sessions
docs: update README with Docker deployment guide
```

## 📥 Pull Request Process

1. **Create a Branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Make Your Changes**
- Write clean, documented code
- Add tests for new functionality
- Update documentation as needed

3. **Test Your Changes**
```bash
# Run tests
pytest

# Check code style
flake8 tradingagents/
black --check tradingagents/

# Type checking (optional)
mypy tradingagents/
```

4. **Commit and Push**
```bash
git add .
git commit -m "feat: your feature description"
git push origin feature/your-feature-name
```

5. **Open Pull Request**
- Provide a clear title and description
- Reference any related issues
- Explain what changed and why
- Include screenshots for UI changes

### PR Checklist
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No unnecessary files included
- [ ] Branch is up to date with main

## 🏗️ Project Structure

```
tradingagents/
├── agents/          # AI agents (analysts, researchers, traders)
├── dataflows/       # Data source integrations
├── llm_clients/     # LLM provider clients
└── graph/           # LangGraph orchestration
```

## 📝 Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add examples for new features
- Keep architecture diagrams current

## 🤝 Code of Conduct

### Our Standards
- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

### Unacceptable Behavior
- Harassment or discrimination
- Trolling or insulting comments
- Publishing private information
- Unprofessional conduct

## ❓ Questions?

Feel free to:
- Open an issue for questions
- Start a discussion on GitHub
- Reach out via email

Thank you for contributing! 🎉
