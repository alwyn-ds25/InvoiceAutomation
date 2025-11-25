# PowerShell script to start all InvoiceCoreProcessor services
# Usage: .\start-services.ps1

Write-Host "Starting InvoiceCoreProcessor services..." -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host ".env file not found. Please copy .env.example to .env and configure it." -ForegroundColor Red
    exit 1
}

# Function to start a service in a new window
function Start-ServiceWindow {
    param(
        [string]$ServiceName,
        [string]$Command
    )
    Write-Host "Starting $ServiceName..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; $Command"
    Start-Sleep -Seconds 2
}

# Start all services in separate windows
Start-ServiceWindow "DataStore MCP Server" "python -m invoice_core_processor.servers.database_server"
Start-ServiceWindow "OCR MCP Server" "python -m invoice_core_processor.servers.ocr_server"
Start-ServiceWindow "Mapper MCP Server" "python -m invoice_core_processor.servers.mapper_server"
Start-ServiceWindow "Validation MCP Server" "python -m invoice_core_processor.servers.agent_server"
Start-ServiceWindow "Ingestion gRPC Server" "python -m invoice_core_processor.microservices.ingestion.main"
Start-ServiceWindow "FastAPI Main Server" "python main_processor.py"

Write-Host "`nAll services started in separate windows." -ForegroundColor Green
Write-Host "FastAPI will be available at: http://localhost:8000" -ForegroundColor Yellow
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "`nPress Ctrl+C to stop all services (close the windows manually)." -ForegroundColor Cyan

