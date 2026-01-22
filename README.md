# WebRead MCP

MCP server that allows AI to read webpages via GET requests.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "webread": {
      "command": "python",
      "args": ["path/to/server.py"]
    }
  }
}
```

## Tool

### read_webpage

Fetches a webpage and returns its text content.

**Parameters:**
- `url` (required): The URL to fetch
- `raw_html` (optional): Return raw HTML instead of extracted text

**Example:**
```json
{
  "url": "https://example.com",
  "raw_html": false
}
```
