---
name: webread
description: Search the web and extract content from webpages using curl and bash/bat. Use when the user wants to search the web, look something up online, read a webpage, or extract information from a URL.
---

# Web Read

## Web Search

Use the appropriate script for the OS. Pass the query and an optional search page number (most of the time there are lots of results and they are split to multiple pages. Page number defaults to 1).

**Linux / macOS / Git Bash:**

```bash
bash skill/scripts/linux/web_search.sh "your search query" [page]
```

**Windows (CMD or PowerShell):**

```bat
skill\scripts\windows\web_search.bat "your search query" [page]
```

**Examples:**

```bash
bash skill/linux/scripts/web_search.sh "rust async tutorial"
skill\scripts\windows\web_search.bat "python web frameworks" 2
```

Returns numbered titles with links.

## Reading a Webpage

Use curl directly to fetch and strip HTML:

```bash
curl -s -L -A "Mozilla/5.0" "https://example.com" | sed 's/<script[^>]*>.*<\/script>//g; s/<style[^>]*>.*<\/style>//g; s/<[^>]*>//g; /^$/d'
```

On Windows (PowerShell), use `curl.exe` instead of `curl`:

```powershell
(curl.exe -s -L -A "Mozilla/5.0" "https://example.com") -replace '<script[^>]*>.*?</script>','' -replace '<style[^>]*>.*?</style>','' -replace '<[^>]*>','' | Where-Object { $_.Trim() }
```

For raw HTML:

```bash
curl -s -L -A "Mozilla/5.0" "https://example.com"
```

## Requirements

- `curl` (pre-installed on modern Windows, macOS, and Linux)
- **Linux/macOS:** `bash`
- **Windows:** `PowerShell` (used by the `.bat` wrapper)

## Installation

Copy the `skill/` folder into `~/.cursor/skills/webread/` for personal use across all projects, or into `.cursor/skills/webread/` for a single project.
