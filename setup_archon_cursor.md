# Complete Setup Guide: Archon + Crawl4AI + Cursor MCP Integration

## Current Status Check

Based on your workspace, you have:
- ✅ Archon project with MCP server ready
- ✅ Crawl4AI with MCP server
- ❌ Services not currently running (ports 8051, 8100, 8501 not active)

## Step-by-Step Setup

### 1. Start Archon Components

#### A. Start Archon UI (Streamlit) - Port 8501
```powershell
cd archon
python -m streamlit run streamlit_ui.py
```
Verify: Open http://localhost:8501 in browser

#### B. Start Archon Graph Service - Port 8100
Open a new terminal:
```powershell
cd archon
python graph_service.py
```
Verify: Visit http://localhost:8100/health - should see `{"status":"ok"}`

#### C. Build and Run Archon MCP Docker Container
Open another terminal:
```powershell
cd archon/mcp
docker build -t archon-mcp:latest .
```

### 2. Start Crawl4AI - Port 8051

Open a new terminal:
```powershell
cd crawl4ai
# If using Docker:
docker build -t crawl4ai-mcp .
docker run -p 8051:8051 crawl4ai-mcp

# Or if using Python directly:
cd src
python crawl4ai_mcp.py
```
Verify: Visit http://localhost:8051/sse - should connect (blank page is OK)

### 3. Configure Cursor MCP Connections

#### Method 1: Via Cursor UI
1. Open Cursor Settings (Ctrl+,)
2. Go to Tools & Integrations → MCP
3. Click "New MCP Server"

**For Archon:**
- Name: `archon`
- Transport: `Command`
- Command: `docker run -i --rm -e GRAPH_SERVICE_URL=http://host.docker.internal:8100 archon-mcp:latest`

**For Crawl4AI:**
- Name: `crawl4ai-rag`
- Transport: `SSE`
- URL: `http://localhost:8051/sse`

#### Method 2: Edit Configuration File
Edit `%USERPROFILE%\.cursor\mcp.json`:
```json
{
  "mcpServers": {
    "archon": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "GRAPH_SERVICE_URL=http://host.docker.internal:8100", "archon-mcp:latest"]
    },
    "crawl4ai-rag": {
      "transport": "sse",
      "url": "http://localhost:8051/sse"
    }
  }
}
```

### 4. Test the Integration

1. Restart Cursor after adding MCP servers
2. Open a new chat in Cursor
3. Check if tools appear in "Available Tools" section

Test commands:
```
# Test Archon
"Use Archon to create a simple Python function that adds two numbers"

# Test Crawl4AI
"Use crawl4ai-rag to analyze the content at https://example.com"
```

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. "Connection refused" errors
- **Check if services are running:**
  ```powershell
  netstat -an | findstr "8051 8100 8501" | findstr LISTENING
  ```
- **Solution:** Start the missing service (see steps above)

#### 2. Docker: "Cannot connect to Docker daemon"
- **Solution:** Ensure Docker Desktop is running
- Alternative: Run services directly with Python instead

#### 3. MCP tools not showing in Cursor
- Click refresh icon in MCP settings
- Restart Cursor completely
- Check `%USERPROFILE%\.cursor\mcp.json` for syntax errors

#### 4. "host.docker.internal" not working
- Replace with your actual local IP:
  ```powershell
  ipconfig
  # Look for IPv4 Address, use that instead
  ```

#### 5. Port already in use
- Find and kill the process:
  ```powershell
  netstat -ano | findstr :8100
  taskkill /PID <pid> /F
  ```

## Quick Status Check Script

Save this as `check_services.ps1`:
```powershell
Write-Host "Checking AI Services Status..." -ForegroundColor Cyan

$services = @(
    @{Name="Archon UI"; Port=8501; URL="http://localhost:8501"},
    @{Name="Archon Graph Service"; Port=8100; URL="http://localhost:8100/health"},
    @{Name="Crawl4AI MCP"; Port=8051; URL="http://localhost:8051/sse"}
)

foreach ($service in $services) {
    try {
        $response = Invoke-WebRequest -Uri $service.URL -TimeoutSec 2 -ErrorAction Stop
        Write-Host "✅ $($service.Name) is running on port $($service.Port)" -ForegroundColor Green
    } catch {
        Write-Host "❌ $($service.Name) is NOT running on port $($service.Port)" -ForegroundColor Red
    }
}
```

## Next Steps After Setup

1. **Verify all services are green** in the status check
2. **Test each tool individually** in Cursor
3. **Check logs** if issues occur:
   - Archon logs: `archon/workbench/logs.txt`
   - Cursor logs: Help → Toggle Developer Tools → Console

## Understanding Your Setup

### What Each Component Does:
- **Archon UI (8501)**: Web interface for manual agent interaction
- **Graph Service (8100)**: Core agent logic that processes requests
- **MCP Server**: Bridge between Cursor and Graph Service
- **Crawl4AI (8051)**: Web scraping and RAG capabilities

### How They Connect:
```
Cursor → MCP Protocol → Docker Container → Graph Service (8100) → Agent Logic
       → MCP Protocol → Crawl4AI (8051) → Web Scraping
```

Ready to test? Start with step 1 and work through each component! 