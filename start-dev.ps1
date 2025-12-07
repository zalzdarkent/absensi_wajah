# Quick Start Script untuk Windows Development

Write-Host "🚀 Starting Absensi Wajah Development Environment" -ForegroundColor Green
Write-Host ""

# Start Next.js in new window
Write-Host "🌐 Starting Next.js (Port 3000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm run dev"

Start-Sleep -Seconds 2

# Start FastAPI in new window
Write-Host "🤖 Starting FastAPI ML Server (Port 8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\ML'; python api\main.py"

Write-Host ""
Write-Host "✅ Development servers starting in separate windows!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Next.js:  http://localhost:3000" -ForegroundColor Yellow
Write-Host "🔧 FastAPI:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "📖 API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  Pastikan MySQL sudah running!" -ForegroundColor Red
Write-Host "   Windows: Start XAMPP/WAMP/MAMP" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
