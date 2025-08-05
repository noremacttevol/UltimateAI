$vaultDir = "C:\AI_SecondBrain\local-ai-packaged\data\personal_vault"
$logFile = "C:\AI_SecondBrain\scripts\supabase_ingest_log.txt"
$serverUrl = "http://localhost:8051/tool/crawl_single_page"

# Initialize log
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path $logFile -Value "[$timestamp] Starting ingestion process"

$ingested = 0
$failed = 0

# Get all .md files
$mdFiles = Get-ChildItem -Path $vaultDir -Filter *.md
if (-not $mdFiles) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logFile -Value "[$timestamp] Warning: No .md files found in $vaultDir"
    Write-Host "Warning: No .md files found"
    exit
}

foreach ($file in $mdFiles) {
    $filePath = $file.FullName -replace '\\', '/'
    $url = "file:///$filePath"
    $body = @{ url = $url } | ConvertTo-Json
    $headers = @{ "Content-Type" = "application/json" }
    
    Write-Host "Crawling: $($file.Name)"
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    try {
        $response = Invoke-WebRequest -Uri $serverUrl -Method POST -Headers $headers -Body $body
        Add-Content -Path $logFile -Value "[$timestamp] Success: Ingested $($file.Name)"
        $ingested++
    }
    catch {
        Add-Content -Path $logFile -Value "[$timestamp] Error: Failed to ingest $($file.Name): $($_.Exception.Message)"
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        $failed++
    }
    
    Start-Sleep -Milliseconds 300
}

# Summary
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$summary = "[$timestamp] Success: DONE: $ingested files ingested to Supabase`n[$timestamp] Error: Failed: $failed files`n[$timestamp] Log saved to: $logFile"
Add-Content -Path $logFile -Value $summary
Write-Host $summary