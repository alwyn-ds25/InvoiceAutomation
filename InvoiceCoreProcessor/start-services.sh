#!/bin/bash
# Bash script to start all InvoiceCoreProcessor services
# Usage: ./start-services.sh

set -e

echo "Starting InvoiceCoreProcessor services..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ".env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Function to start a service in a new terminal
start_service_terminal() {
    local service_name=$1
    local command=$2
    
    echo "Starting $service_name..."
    
    # Detect the terminal emulator
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal --tab --title="$service_name" -- bash -c "cd '$PWD' && source venv/bin/activate && $command; exec bash"
    elif command -v xterm &> /dev/null; then
        xterm -T "$service_name" -e "cd '$PWD' && source venv/bin/activate && $command; exec bash" &
    elif command -v osascript &> /dev/null; then
        # macOS
        osascript -e "tell application \"Terminal\" to do script \"cd '$PWD' && source venv/bin/activate && $command\""
    else
        echo "Warning: Could not detect terminal emulator. Starting $service_name in background..."
        nohup bash -c "cd '$PWD' && source venv/bin/activate && $command" > "logs/${service_name// /_}.log" 2>&1 &
    fi
    
    sleep 2
}

# Create logs directory if it doesn't exist
mkdir -p logs

# Start all services in separate terminals
start_service_terminal "DataStore MCP Server" "python -m invoice_core_processor.servers.database_server"
start_service_terminal "OCR MCP Server" "python -m invoice_core_processor.servers.ocr_server"
start_service_terminal "Mapper MCP Server" "python -m invoice_core_processor.servers.mapper_server"
start_service_terminal "Validation MCP Server" "python -m invoice_core_processor.servers.agent_server"
start_service_terminal "Ingestion gRPC Server" "python -m invoice_core_processor.microservices.ingestion.main"
start_service_terminal "FastAPI Main Server" "python main_processor.py"

echo ""
echo "All services started in separate terminals."
echo "FastAPI will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "To stop services, close the terminal windows or use: pkill -f 'python -m invoice_core_processor'"

