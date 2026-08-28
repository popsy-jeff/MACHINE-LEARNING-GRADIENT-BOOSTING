@echo off
echo Starting backend (FastAPI) on port 8000...
start "Backend" cmd /k "cd backend && uvicorn main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo Starting frontend (Vite)...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo Both servers starting in separate windows.
