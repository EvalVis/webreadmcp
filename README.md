# WebRead MCP

A Model Context Protocol (MCP) server that enables AI assistants to read webpages and perform web searches.

## Tools

### read_webpage

Fetches a webpage via GET request and returns its text content.

**Parameters:**
- `url` (required) - The URL to fetch
- `max_chars` (optional, default: 500) - Maximum characters to return
- `offset` (optional, default: 0) - Starting character position for chunked reading
- `raw_html` (optional, default: false) - Return raw HTML instead of extracted text

**Example:**
```json
{
  "url": "https://example.com",
  "max_chars": 1000,
  "offset": 0
}
```

### web_search

Performs a web search using DuckDuckGo and returns titles with links.

**Parameters:**
- `query` (required) - The search query
- `page` (optional, default: 1) - Page number (1-based)

**Example:**
```json
{
  "query": "python tutorial",
  "page": 1
}
```

## Installation

### From PyPI

```bash
pip install webread-mcp
```

### From Source

```bash
git clone <repository-url>
cd webreadmcp
pip install -e .
```

## Configuration

Add the server to your MCP client configuration:

### If installed via pip

```json
{
  "mcpServers": {
    "webread": {
      "command": "python",
      "args": ["-m", "webread_mcp"]
    }
  }
}
```

### If running from source

```json
{
  "mcpServers": {
    "webread": {
      "command": "python",
      "args": ["/absolute/path/to/webreadmcp/server.py"]
    }
  }
}
```

## Running Manually

```bash
python -m webread_mcp
```

Or from source:

```bash
python server.py
```

The server communicates via stdio and will wait for MCP protocol messages.

## Dependencies

- `mcp` - Model Context Protocol SDK
- `httpx` - HTTP client
- `beautifulsoup4` - HTML parsing
- `duckduckgo_search` - Web search
