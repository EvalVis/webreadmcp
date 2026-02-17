---
name: webread
description: Search the web and extract content from webpages using curl and bash. Use when the user wants to search the web, look something up online, read a webpage, or extract information from a URL.
---

# Web Read

## Web Search

Run the bundled script to search the web. Pass the query and an optional page number (defaults to 1).

```bash
bash skill/scripts/web_search.sh "your search query" [page]
```

**Examples:**

```bash
bash skill/scripts/web_search.sh "rust async tutorial"
bash skill/scripts/web_search.sh "python web frameworks" 2
```

Returns numbered titles with links.

## Reading a Webpage

Use curl directly to fetch and extract text from a URL:

```bash
curl -s -L -A "Mozilla/5.0" "https://example.com" | sed 's/<script[^>]*>.*<\/script>//g; s/<style[^>]*>.*<\/style>//g; s/<[^>]*>//g; /^$/d'
```

For raw HTML when you need to inspect page structure:

```bash
curl -s -L -A "Mozilla/5.0" "https://example.com"
```

## Requirements

- `curl` (pre-installed on modern Windows, macOS, and Linux)
- `bash` (Git Bash on Windows, native on macOS/Linux)

## Installation

Copy the `skill/` folder into `~/.cursor/skills/webread/` for personal use across all projects, or into `.cursor/skills/webread/` for a single project.
