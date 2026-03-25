# Agent Cost Proxy

A local proxy that slashes AI agent token costs by intercepting and cleaning data before it reaches your LLM.

**One fetch of Yahoo Finance: 704,415 tokens → 2,624 tokens. 99.6% reduction.**

## The Problem

AI agents waste most of their token budget on data retrieval — loading raw HTML pages, parsing bloated API responses, and stuffing unstructured documents into the context window. This happens before any reasoning occurs.

## The Solution

Agent Cost Proxy sits between your agent and the internet. It intercepts data fetches, strips all noise, and delivers only clean signal to your LLM.

| Source | Raw Tokens | After Proxy | Reduction |
|--------|-----------|-------------|-----------|
| Yahoo Finance (AAPL) | 704,415 | 2,624 | **99.6%** |
| Wikipedia article | 341,825 | 45,791 | **86.6%** |

## Features

**Layer 1 — Prompt Refiner** (opt-in)
- Send a rough prompt, get back a cleaner version
- Strips filler words and hedging while protecting entities, negations, and context references
- You see both versions and decide which to use

**Layer 2 — Data Proxy** (automatic)
- Fetches any URL, strips HTML/JSON noise, returns clean text
- Caches results to avoid redundant fetches
- Handles HTML, JSON, and plain text responses
- Batch endpoint for multiple URLs at once

## Quick Start
```bash
git clone https://github.com/YOUR_USERNAME/agent-cost-proxy.git
cd agent-cost-proxy
chmod +x install.sh
./install.sh
source .venv/bin/activate
python3 proxy.py
```

## Usage

### Fetch and clean a webpage
```bash
curl -s http://localhost:8080/fetch \
  -H "content-type: application/json" \
  -d '{"url": "https://finance.yahoo.com/quote/AAPL/"}' \
  | python3 -m json.tool
```

### Refine a prompt (opt-in)
```bash
curl -s http://localhost:8080/refine \
  -H "content-type: application/json" \
  -d '{"text": "Hey could you please maybe help me analyze AAPL earnings compared to last quarter and what analysts are saying thanks"}' \
  | python3 -m json.tool
```

### Batch fetch multiple URLs
```bash
curl -s http://localhost:8080/fetch/batch \
  -H "content-type: application/json" \
  -d '{"urls": ["https://finance.yahoo.com/quote/AAPL/", "https://finance.yahoo.com/quote/MSFT/"]}' \
  | python3 -m json.tool
```

### Check session stats
```bash
curl -s http://localhost:8080/stats | python3 -m json.tool
```

## Run Tests
```bash
# Layer 1 only (offline)
python3 test_all.py

# Layer 1 + Layer 2 (needs internet)
python3 test_all.py --live
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/fetch` | POST | Fetch URL, strip noise, return clean data |
| `/fetch/batch` | POST | Fetch multiple URLs at once |
| `/refine` | POST | Opt-in prompt refinement |
| `/stats` | GET | Session statistics |
| `/` | GET | API info |

## How It Works
```
Your Agent
    │
    ▼
localhost:8080 (Agent Cost Proxy)
    │
    ├── /refine  → strips filler, protects entities, you decide
    ├── /fetch   → fetches URL, strips HTML noise, caches result
    │
    ▼
Clean data (2-15% of original token count)
```

## Roadmap

- [x] Layer 1: Prompt refiner
- [x] Layer 2: Data proxy with caching
- [ ] Browser fallback (Playwright) for sites that block bots
- [ ] Authenticated session management
- [ ] Layer 3: Output/history compression
- [ ] CLI tool (`agent-proxy refine "your prompt"`)
- [ ] Dashboard UI
- [ ] OpenAI/Ollama proxy mode

## Requirements

- Python 3.10+
- No API keys needed
- No GPU needed

## License

MIT
