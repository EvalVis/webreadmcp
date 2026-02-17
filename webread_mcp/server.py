import asyncio
from bs4 import BeautifulSoup
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from urllib.parse import quote_plus

__version__ = "1.3.0"

app = Server("webread")

DEFAULT_MAX_CHARS = 500
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"


async def run_curl(args: list[str]) -> tuple[str, int]:
    proc = await asyncio.create_subprocess_exec(
        "curl", *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=30.0)
    return stdout.decode("utf-8", errors="replace"), proc.returncode


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def parse_search_results(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    results = []
    for a in soup.select("a.result__a"):
        title = a.get_text(strip=True)
        url = a.get("href", "")
        if title and url:
            results.append({"title": title, "href": url})
    return results


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="read_webpage",
            description="Fetches a webpage via curl and returns its text content. Strips HTML tags, scripts, and styles. Supports chunked reading for large pages.",
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
        encoded_query = quote_plus(query)
        post_data = f"q={encoded_query}"
        if page > 1:
            offset = (page - 1) * 30
            post_data += f"&s={offset}&dc={offset + 1}&o=json&api=d.js"

        html, returncode = await run_curl([
            "-s", "-L",
            "-A", USER_AGENT,
            "-X", "POST",
            "-d", post_data,
            "https://html.duckduckgo.com/html/",
        ])

        if returncode != 0:
            return [TextContent(type="text", text=f"Error: curl failed with code {returncode}")]

        results = parse_search_results(html)

        if not results:
            return [TextContent(type="text", text=f"No results found for: {query} (page {page})")]

        total = len(results)
        output = f"Search: {query} (page {page}, {total} results)\n\n"
        for i, r in enumerate(results, 1):
            output += f"{i}. {r['title']}\n   {r['href']}\n\n"

        return [TextContent(type="text", text=output)]
    except asyncio.TimeoutError:
        return [TextContent(type="text", text="Error: Search request timed out")]
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
        html, returncode = await run_curl([
            "-s", "-L",
            "-A", USER_AGENT,
            url,
        ])

        if returncode != 0:
            return [TextContent(type="text", text=f"Error: curl failed with code {returncode} for {url}")]

        content = html if raw_html else extract_text(html)
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
    except asyncio.TimeoutError:
        return [TextContent(type="text", text=f"Error: Request timed out for {url}")]
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
