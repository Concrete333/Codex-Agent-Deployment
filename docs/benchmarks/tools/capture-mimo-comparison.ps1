# Maintenance only: capture visible comparison tables, never chart datasets.
param([string]$Destination = (Join-Path $PSScriptRoot '../mimo-comparison-2026-09-21.json'))
$ErrorActionPreference = 'Stop'
function Plain([string]$Html) {
    return [System.Net.WebUtility]::HtmlDecode(($Html -replace '<[^>]+>', ' ' -replace '\s+', ' ')).Trim()
}
$slugs = @('gpt-5-6-luna', 'gpt-5-6-sol-high', 'claude-opus-5-low', 'gpt-6-astra-high')
$pages = @()
foreach ($slug in $slugs) {
    $url = "https://artificialanalysis.ai/models/comparisons/mimo-v2-6-pro-vs-$slug"
    $html = (Invoke-WebRequest -Uri $url -TimeoutSec 25).Content
    $table = [regex]::Match($html, '<table[\s\S]*?</table>').Value
    if (-not $table) { throw "No visible comparison table: $url" }
    $rows = @()
    foreach ($row in [regex]::Matches($table, '<tr[\s\S]*?</tr>')) {
        $cells = @([regex]::Matches($row.Value, '<t[dh]\b[^>]*>([\s\S]*?)</t[dh]>') | ForEach-Object { Plain $_.Groups[1].Value })
        $rows += ,$cells
    }
    $version = [regex]::Match((Plain ($html -replace '<script\b[^>]*>[\s\S]*?</script>', '')), 'Intelligence Index v[\d.]+').Value
    if ($version -ne 'Intelligence Index v4.3.2') { throw "Unexpected benchmark version: $version" }
    $pages += @{ url=$url; benchmark=$version; table=$rows }
}
$catalogLines = @(kilo.cmd models kilo --verbose)
if ($LASTEXITCODE -ne 0) { throw 'Kilo catalog lookup failed' }
$start = [Array]::IndexOf($catalogLines, 'kilo/xiaomi/mimo-v2.6-pro')
if ($start -lt 0) { throw 'MiMo missing from Kilo catalog' }
$end = $start + 1
while ($end -lt $catalogLines.Count -and $catalogLines[$end] -notlike 'kilo/*') { $end++ }
$model = ($catalogLines[($start+1)..($end-1)] -join "`n") | ConvertFrom-Json
@{
    captured_at_utc = [DateTime]::UtcNow.ToString('o')
    model_page = 'https://artificialanalysis.ai/models/mimo-v2-6-pro'
    precision = 'Public table display precision; k/M values are rounded, not raw token counts.'
    pages = $pages
    kilo = @{
        cli_model = 'kilo/xiaomi/mimo-v2.6-pro'
        status = $model.status
        cost = $model.cost
        limits = $model.limit
        variants = $model.variants
    }
} | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath $Destination -Encoding utf8
"Captured $($pages.Count) comparison tables and Kilo catalog metadata."
