#!/bin/bash

# Stop all c0r.AI services

echo "🛑 Stopping c0r.AI services..."

# Kill processes on service ports
echo "🔄 Killing processes on ports 8000, 8001, 8002..."
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
lsof -ti:8002 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Also kill any uvicorn processes
pkill -f "uvicorn.*main:app" 2>/dev/null || true

echo "✅ All services stopped!"