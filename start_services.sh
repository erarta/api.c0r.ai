#!/bin/bash

# Start all services locally for development

echo "🚀 Starting c0r.AI services..."

# Kill any existing processes on these ports
echo "🔄 Cleaning up existing processes..."
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
lsof -ti:8002 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start ML service
echo "🧠 Starting ML service on port 8001..."
cd services/ml
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload &
ML_PID=$!
cd ../..

# Wait a bit for ML service to start
sleep 3

# Start Payment service
echo "💳 Starting Payment service on port 8002..."
cd services/pay
python3 -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload &
PAY_PID=$!
cd ../..

# Wait a bit for Payment service to start
sleep 3

# Start API service (Bot)
echo "🤖 Starting API Bot service on port 8000..."
cd services/api/bot
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!
cd ../../..

echo "✅ All services started!"
echo "📊 ML Service: http://localhost:8001"
echo "💰 Payment Service: http://localhost:8002"
echo "🤖 API Bot Service: http://localhost:8000"
echo ""
echo "Process IDs:"
echo "ML: $ML_PID"
echo "Payment: $PAY_PID"
echo "API: $API_PID"
echo ""
echo "To stop all services, run: ./stop_services.sh"
echo "Or manually kill processes: kill $ML_PID $PAY_PID $API_PID"

# Keep script running to show logs
wait