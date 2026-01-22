import asyncio
import httpx
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

__version__ = "1.0.1"

app = Server("webread")

DEFAULT_MAX_CHARS = 500
RESULTS_PER_PAGE = 10


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="read_webpage",
            description="Fetches a webpage via GET request and returns its text content. Strips HTML tags, scripts, and styles. Supports chunked reading for large pages.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the webpage to read",
                    },
                    "max_chars": {
                        "type": "integer",
                        "description": f"Maximum characters to return. Default: {DEFAULT_MAX_CHARS}",
                        "default": DEFAULT_MAX_CHARS,
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Starting character position for reading. Default: 0",
                        "default": 0,
                    },
                    "raw_html": {
                        "type": "boolean",
                        "description": "If true, returns raw HTML instead of extracted text. Default: false",
                        "default": False,
                    },
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="web_search",
            description="Performs a web search using DuckDuckGo and returns titles with links.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number (1-based). Default: 1",
                        "default": 1,
                    },
                },
                "required": ["query"],
            },
        ),
    ]


async def handle_web_search(arguments: dict) -> list[TextContent]:
    query = arguments.get("query")
    page = arguments.get("page", 1)

    if not query:
        return [TextContent(type="text", text="Error: query is required")]

    try:
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: DDGS().text(query, max_results=RESULTS_PER_PAGE * page)
        )

        total_results = len(results) if results else 0
        start_idx = (page - 1) * RESULTS_PER_PAGE
        end_idx = min(start_idx + RESULTS_PER_PAGE, total_results)
        page_results = results[start_idx:end_idx] if results else []

        if not page_results:
            return [TextContent(type="text", text=f"No results found for: {query} (page {page})")]

        output = f"Search: {query} (page {page}, showing {start_idx + 1}-{end_idx} of {total_results})\n\n"
        for i, r in enumerate(page_results, 1):
            output += f"{i}. {r['title']}\n   {r['href']}\n\n"

        return [TextContent(type="text", text=output)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_read_webpage(arguments: dict) -> list[TextContent]:
    url = arguments.get("url")
    max_chars = arguments.get("max_chars", DEFAULT_MAX_CHARS)
    offset = arguments.get("offset", 0)
    raw_html = arguments.get("raw_html", False)

    if not url:
        return [TextContent(type="text", text="Error: URL is required")]

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()

            content = response.text if raw_html else extract_text(response.text)
            total_size = len(content)

            if offset >= total_size:
                return [
                    TextContent(
                        type="text",
                        text=f"URL: {url}\nTotal size: {total_size} chars\nOffset {offset} exceeds content size.",
                    )
                ]

            chunk = content[offset:offset + max_chars]
            end_index = offset + len(chunk)

            if total_size <= max_chars and offset == 0:
                return [
                    TextContent(
                        type="text",
                        text=f"URL: {url}\nTotal size: {total_size} chars\n\n{content}",
                    )
                ]

            return [
                TextContent(
                    type="text",
                    text=f"URL: {url}\nTotal size: {total_size} chars\nShowing: {offset}-{end_index} of {total_size}\n\n{chunk}",
                )
            ]
    except httpx.TimeoutException:
        return [TextContent(type="text", text=f"Error: Request timed out for {url}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error: HTTP {e.response.status_code} for {url}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "web_search":
        return await handle_web_search(arguments)
    if name == "read_webpage":
        return await handle_read_webpage(arguments)
    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def run_server():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main():
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
