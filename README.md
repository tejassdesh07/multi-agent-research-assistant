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

- Content filtering to block harmful requests
- Rate limiting (10 requests per minute)
- Input sanitization
- Path traversal protection
- Output validation

## Testing

Run the test suites to make sure everything works:

```bash
python tests/test_agents.py
python tests/test_tools.py
python tests/test_safety.py
```

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

## License

MIT
