#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: bash web_search.sh \"<query>\" [page]"
  exit 1
fi

query="$1"
page="${2:-1}"
encoded_query=$(printf '%s' "$query" | sed 's/ /+/g')

if [ "$page" -eq 1 ]; then
  html=$(curl -s -L -A "Mozilla/5.0" -X POST \
    -d "q=${encoded_query}" \
    "https://html.duckduckgo.com/html/")
else
  offset=$(( (page - 1) * 30 ))
  html=$(curl -s -L -A "Mozilla/5.0" -X POST \
    -d "q=${encoded_query}&s=${offset}&dc=$((offset + 1))&o=json&api=d.js" \
    "https://html.duckduckgo.com/html/")
fi

if [ -z "$html" ]; then
  echo "Error: Failed to fetch search results"
  exit 1
fi

echo "Search: $query (page $page)"
echo

count=0
while IFS= read -r line; do
  [ -z "$line" ] && continue

  url=$(echo "$line" | sed 's/.*href="\([^"]*\)".*/\1/')
  title=$(echo "$line" | sed 's/.*">//' | sed "s/&#x27;/'/g; s/&amp;/\&/g; s/&lt;/</g; s/&gt;/>/g; s/&quot;/\"/g; s/&#39;/'/g")

  if [ -n "$url" ] && [ -n "$title" ]; then
    count=$((count + 1))
    echo "${count}. ${title}"
    echo "   ${url}"
    echo
  fi
done <<< "$(echo "$html" | grep -o 'class="result__a" href="[^"]*">[^<]*')"

if [ "$count" -eq 0 ]; then
  echo "No results found."
fi
