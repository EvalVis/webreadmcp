param(
    [Parameter(Mandatory=$true)][string]$Query,
    [int]$Page = 1
)

$encodedQuery = $Query -replace ' ', '+'
$tmpFile = Join-Path $env:TEMP "websearch_$((Get-Random)).html"

if ($Page -eq 1) {
    $postData = "q=$encodedQuery"
} else {
    $offset = ($Page - 1) * 30
    $dc = $offset + 1
    $postData = "q=$encodedQuery&s=$offset&dc=$dc"
}

curl.exe -s -L -A "Mozilla/5.0" -X POST -d $postData "https://html.duckduckgo.com/html/" -o $tmpFile

if (-not (Test-Path $tmpFile)) {
    Write-Host "Error: Failed to fetch search results"
    exit 1
}

$html = Get-Content -Raw $tmpFile
Remove-Item $tmpFile -ErrorAction SilentlyContinue

Write-Host "Search: $Query (page $Page)"
Write-Host ""

$pattern = 'class="result__a" href="([^"]*)"[^>]*>([^<]*)'
$matches = [regex]::Matches($html, $pattern)

$i = 0
foreach ($m in $matches) {
    $i++
    $url = $m.Groups[1].Value
    $title = $m.Groups[2].Value
    Write-Host ("{0}. {1}" -f $i, $title)
    Write-Host ("   {0}" -f $url)
    Write-Host ""
}

if ($i -eq 0) {
    Write-Host "No results found."
}
