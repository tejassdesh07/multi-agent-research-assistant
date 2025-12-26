# Multi-Agent Research Assistant

An AI-powered research assistant that uses multiple agents to search the web, gather information, and create executive summaries. Built with LangChain and CrewAI.

## What It Does

This system has two AI agents that work together:
- **Research Agent**: Searches the web, extracts information, and stores it in memory
- **Summary Agent**: Takes all the research and creates a clear executive summary with insights

The agents use RAG (Retrieval-Augmented Generation) with ChromaDB to remember information across sessions, so they get smarter over time.

## Tech Stack

- LangChain & CrewAI for agent orchestration
- OpenAI GPT-3.5 for intelligence
- ChromaDB for vector storage and memory
- DuckDuckGo for web search
- Built-in safety controls and rate limiting

## Quick Start

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Set up your API key**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Get one from https://platform.openai.com/api-keys
```

3. **Run the assistant**
```bash
python main.py
```

The system will ask what you want to research, then the agents will get to work. Results are saved in `data/research/`.

## How It Works

1. You give it a research topic
2. Research Agent searches the web and collects information
3. All findings are stored in a vector database for semantic search
4. Summary Agent retrieves relevant info and creates an executive summary
5. Both agents can access shared memory for better collaboration

## Project Structure

```
src/
├── agents/          Research and Summary agents
├── tools/           Web search, memory, and file tools
├── guardrails/      Safety and validation
└── orchestrator.py  Coordinates the agents

tests/               Unit tests for everything
data/research/       Your research results go here
```

## Safety Features

Built with multiple layers of protection:

- **Content Filtering**: Blocks malicious/harmful terms and requests
- **Rate Limiting**: 10 requests per minute to prevent abuse
- **Input Sanitization**: Removes special characters and validates queries
- **Path Traversal Protection**: Prevents unauthorized file access
- **Output Validation**: Checks response quality and format
- **Token Limiting**: Maximum 4000 tokens per request (using tiktoken)
- **XSS Prevention**: Sanitizes web content to prevent injection attacks

## Guardrails

The system includes comprehensive guardrails implemented in `src/guardrails/safety_controls.py`:

**SafetyGuardrails Class** provides:
- **Input Validation**: Checks all user inputs for blocked terms, malicious patterns, and length limits
- **Output Validation**: Validates agent responses before returning to users
- **Rate Limiting**: Tracks operations and enforces request limits per time window
- **Content Filtering**: Blocks harmful terms (malware, exploit, phishing, etc.)
- **Token Counting**: Uses tiktoken to count and limit tokens per request
- **Operation Logging**: Maintains audit trail of all agent operations
- **Confidence Scoring**: Validates output quality with minimum confidence thresholds
- **Citation Requirements**: Ensures research outputs include proper source citations

The guardrails are automatically applied to all agent operations through the orchestrator, ensuring safe and controlled execution throughout the system.

## Testing

Comprehensive test suite built with Python's `unittest` framework:

```bash
python tests/test_agents.py    # Agent creation and configuration tests
python tests/test_tools.py     # Web search, memory, and file operation tests
python tests/test_safety.py    # Security and validation tests
```

**What's tested:**
- Agent initialization and tool assignment
- Web search with rate limiting
- Memory storage and retrieval (RAG)
- File operations with path validation
- Content filtering and blocked terms
- Input/output validation
- Token counting and limits

**Testing tools used:**
- `unittest` - Python's built-in testing framework
- `unittest.mock` - Mocking for isolated tests

**Note**: You may see deprecation warnings from CrewAI and Pydantic libraries during startup. These are normal third-party library warnings and don't affect functionality.

## Configuration

Edit `config.yaml` to customize:
- Agent behavior and iteration limits
- Memory and RAG settings
- Safety controls
- Tool configurations

## What You Get

After running a research task, you'll find:
- `research_[timestamp]_[topic].txt` - Full research report with sources
- `summary_[timestamp]_[topic].txt` - Executive summary with recommendations

## Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for web search
