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

**Windows:**

```bat
skill\scripts\windows\web_search.bat "your search query" [page]
```

**Examples:**

```bash
bash skill/scripts/linux/web_search.sh "rust async tutorial"
skill\scripts\windows\web_search.bat "python web frameworks" 2
```

Returns numbered titles with links.

## Reading a Webpage

**Linux / macOS / Git Bash:**

```bash
curl -s -L -A "Mozilla/5.0" "https://example.com" | sed 's/<script[^>]*>.*<\/script>//g; s/<style[^>]*>.*<\/style>//g; s/<[^>]*>//g; /^$/d'
```

**Windows:**

<b>Note</b>: the below command can be executed on CMD if before the command you type: `powershell -NoProfile -Command` and envelop the command in parenthesis


```powershell
(curl.exe -s -L -A "Mozilla/5.0" "https://example.com") -replace '<script[^>]*>.*?</script>','' -replace '<style[^>]*>.*?</style>','' -replace '<[^>]*>','' | Where-Object { $_.Trim() }
```

## Raw HTML

**Linux / macOS / Git Bash:**

```bash
curl -s -L -A "Mozilla/5.0" "https://example.com"
```

**Windows:**

```powershell
curl.exe -s -L -A "Mozilla/5.0" "https://example.com"
```

## Requirements

- `curl` (pre-installed on modern Windows, macOS, and Linux)
- **Linux/macOS:** `bash`

## Installation

Copy the `skill/` folder into your AI context folder.
