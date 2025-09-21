@echo off
echo 🔧 Quick Fix for Chatbot Services
echo ================================

echo.
echo 📦 Installing required packages...
pip install psycopg2-binary sqlalchemy alembic streamlit

echo.
echo 🐳 Starting infrastructure services...
docker run -d --name chatbot-postgres -e POSTGRES_DB=chatbot_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15 2>nul
docker run -d --name chatbot-redis -p 6379:6379 redis:7-alpine 2>nul

echo.
echo ⏳ Waiting for services to initialize...
timeout /t 10 /nobreak >nul

echo.
echo 🚀 Starting User Service...
start "User Service" /D "user-service" python main.py

echo.
echo ⏳ Waiting for User Service...
timeout /t 5 /nobreak >nul

echo.
echo 🎨 Starting Frontend...
start "Frontend" /D "frontend" streamlit run app.py --server.port 8501

echo.
echo ✅ Services should now be starting!
echo.
echo 📱 Access points:
echo    Frontend: http://localhost:8501
echo    API Gateway: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo 👤 Default login:
echo    Username: admin
echo    Password: admin123
echo.
echo ⚠️  Note: Make sure to add your OpenAI API key to .env file!
echo.
pause