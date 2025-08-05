
# chatgpt_export_to_markdown.ps1
# FINAL FIX: Handles empty .parts, string content, and fallback flattening

$ErrorActionPreference = "Stop"

# Paths
$exportZipPath = "C:\AI_SecondBrain\exports\chat-gpt-data-2025-06-18.zip"
$extractPath = "C:\AI_SecondBrain\exports\temp_extract"
$outputRoot = "C:\AI_SecondBrain\local-ai-packaged\data\personal_vault"

# Clean extraction dir
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $extractPath
New-Item -ItemType Directory -Force -Path $extractPath | Out-Null
New-Item -ItemType Directory -Force -Path $outputRoot | Out-Null

# Extract ZIP
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory($exportZipPath, $extractPath)

# Load JSON
$jsonPath = Join-Path $extractPath "conversations.json"
$jsonContent = Get-Content $jsonPath -Raw | ConvertFrom-Json

# Topic routing rules
$topicMap = @{
    "FPA" = "FPA_Building"
    "bike" = "Motorcycle_Fixes"
    "R1" = "Motorcycle_Fixes"
    "PLC" = "PLC_Programming"
    "AI" = "AI_System_Building"
    "Obsidian" = "AI_System_Building"
    "diet" = "Health_Lifestyle"
    "VA" = "VA_Benefits"
}

function Classify-Function($text) {
    $lc = $text.ToLower()
    if ($lc -match "how to" -or $lc -match "step by step") { return "HowTo_Guides" }
    elseif ($lc -match "idea" -or $lc -match "brainstorm") { return "Idea_Lists" }
    elseif ($lc -match "fix" -or $lc -match "troubleshoot") { return "Fix_Logs" }
    elseif ($text.Split().Count -gt 300) { return "Reference_Notes" }
    else { return "Misc" }
}

$assistantCount = 0
$skippedEmpty = 0

foreach ($convo in $jsonContent) {
    $title = $convo.title
    if (-not $title) { $title = "Untitled" }
    $safeTitle = ($title -replace '[^\w\s-]', '').Trim() -replace '\s+', '_'
    if (-not $convo.mapping) { continue }

    foreach ($msg in $convo.mapping.Values) {
        if (-not $msg.message) { continue }
        $role = $msg.message.author.role
        if ($role -ne "assistant") { continue }

        $text = $null

        # Try all known formats
        try {
            if ($msg.message.content -and $msg.message.content.parts.Count -gt 0) {
                $text = $msg.message.content.parts[0].Trim()
            }
            elseif ($msg.message.content -is [string]) {
                $text = $msg.message.content.Trim()
            }
            elseif ($msg.message.content.content_type -eq "text" -and $msg.message.content.parts) {
                $text = ($msg.message.content.parts -join "`n").Trim()
            }
        } catch {}

        if (-not $text -or $text.Trim() -eq "") {
            $skippedEmpty++
            continue
        }

        $assistantCount++

        $topic = "General"
        foreach ($k in $topicMap.Keys) {
            if ($title -like "*$k*") {
                $topic = $topicMap[$k]
                break
            }
        }

        $func = Classify-Function $text
        $folderPath = Join-Path $outputRoot "$topic\$func"
        New-Item -ItemType Directory -Force -Path $folderPath | Out-Null

        $filename = "$($safeTitle.Substring(0, [Math]::Min($safeTitle.Length, 40)))_" + ([guid]::NewGuid().ToString().Substring(0, 6)) + ".md"
        $filePath = Join-Path $folderPath $filename

        "# $title`n`n$text" | Out-File -Encoding UTF8 $filePath
    }
}

if ($assistantCount -eq 0) {
    Write-Host "❌ ERROR: No assistant messages were extracted. Skipped: $skippedEmpty (all were empty or unreadable)."
} else {
    Write-Host "✅ DONE: $assistantCount assistant replies saved. Skipped $skippedEmpty empty ones."
}
