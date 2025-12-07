#!/bin/bash
# Quick Start Script untuk Development

echo "🚀 Starting Absensi Wajah Development Environment"
echo ""

# Check if MySQL is running
echo "📊 Checking MySQL..."
if ! pgrep -x "mysqld" > /dev/null; then
    echo "⚠️  MySQL tidak running. Pastikan MySQL sudah distart."
    echo "   Windows: Start XAMPP/WAMP/MAMP"
    echo "   Linux: sudo systemctl start mysql"
    echo ""
fi

# Start Next.js dev server
echo "🌐 Starting Next.js (Port 3000)..."
npm run dev &
NEXTJS_PID=$!

# Wait a bit
sleep 3

# Start FastAPI server
echo "🤖 Starting FastAPI ML Server (Port 8000)..."
cd ML/api
python main.py &
FASTAPI_PID=$!

echo ""
echo "✅ Development servers started!"
echo ""
echo "📱 Next.js:  http://localhost:3000"
echo "🔧 FastAPI:  http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for Ctrl+C
wait $NEXTJS_PID
wait $FASTAPI_PID
