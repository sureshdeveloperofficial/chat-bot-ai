# 🚨 Troubleshooting Guide

This guide helps you resolve common issues with the Microservice Chatbot.

## 🔧 Quick Fix Tool

Run the automated fix tool first:

```bash
python fix_issues.py
```

This tool will:
- ✅ Install missing Python packages
- ✅ Check/create .env configuration
- ✅ Start infrastructure services
- ✅ Start all microservices
- ✅ Verify everything is working

## 📊 Test Results Analysis

Based on your test results, here are the specific issues and fixes:

### ❌ Issue 1: User Service Not Running

**Problem**: `Connection failed (service not running)`

**Solutions**:
1. **Install database dependencies:**
   ```bash
   pip install psycopg2-binary sqlalchemy alembic
   ```

2. **Start PostgreSQL:**
   ```bash
   docker run -d --name chatbot-postgres \
     -e POSTGRES_DB=chatbot_db \
     -e POSTGRES_USER=user \
     -e POSTGRES_PASSWORD=password \
     -p 5432:5432 postgres:15
   ```

3. **Start User Service:**
   ```bash
   cd user-service
   python main.py
   ```

### ❌ Issue 2: OpenAI API Quota Exceeded

**Problem**: `Error code: 429 - insufficient_quota`

**Solutions**:
1. **Get a valid OpenAI API key:**
   - Visit [platform.openai.com](https://platform.openai.com)
   - Add payment method and credits
   - Create new API key

2. **Update .env file:**
   ```env
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

3. **Alternative: Use free local model:**
   - Modify chat-service to use Hugging Face transformers
   - Or use Ollama for local LLM

### ❌ Issue 3: Frontend Not Accessible

**Problem**: Frontend at http://localhost:8501 not responding

**Solutions**:
1. **Start Streamlit frontend:**
   ```bash
   cd frontend
   streamlit run app.py --server.port 8501
   ```

2. **Check if port is available:**
   ```bash
   netstat -ano | findstr :8501  # Windows
   lsof -i :8501                 # macOS/Linux
   ```

## 🛠 Service-by-Service Fixes

### Auth Service (Port 8001)
```bash
cd auth-service
pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt]
python main.py
```

### User Service (Port 8003)
```bash
cd user-service
pip install sqlalchemy psycopg2-binary alembic
python main.py
```

### Vector Service (Port 8004)
```bash
cd vector-service
pip install faiss-cpu langchain-openai PyPDF2 docx2txt
python main.py
```

### Chat Service (Port 8002)
```bash
cd chat-service
pip install langchain langchain-openai redis
python main.py
```

### Gateway (Port 8000)
```bash
cd gateway
pip install httpx
python main.py
```

### Frontend (Port 8501)
```bash
cd frontend
pip install streamlit streamlit-chat
streamlit run app.py
```

## 🐳 Docker Alternative

If local setup fails, use Docker:

```bash
# Start infrastructure only
docker-compose up postgres redis -d

# Or start everything with Docker
docker-compose up --build
```

## 🔍 Debugging Steps

### 1. Check Service Logs
```bash
# If running with Docker Compose
docker-compose logs <service-name>

# If running locally, check terminal output
```

### 2. Test Individual Services
```bash
# Test each service health endpoint
curl http://localhost:8001/health  # Auth
curl http://localhost:8003/health  # User  
curl http://localhost:8004/health  # Vector
curl http://localhost:8002/health  # Chat
curl http://localhost:8000/health  # Gateway
```

### 3. Check Database Connection
```bash
# Connect to PostgreSQL
docker exec -it chatbot-postgres psql -U user -d chatbot_db

# Check tables
\dt
```

### 4. Test Redis Connection
```bash
# Connect to Redis
docker exec -it chatbot-redis redis-cli

# Test connection
ping
```

## 🌐 Environment Configuration

### Required .env Variables
```env
# Essential
OPENAI_API_KEY=sk-your-actual-openai-api-key
SECRET_KEY=your-32-char-minimum-secret-key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/chatbot_db

# Redis
REDIS_URL=redis://localhost:6379

# Service URLs
AUTH_SERVICE_URL=http://localhost:8001
CHAT_SERVICE_URL=http://localhost:8002
USER_SERVICE_URL=http://localhost:8003
VECTOR_SERVICE_URL=http://localhost:8004
GATEWAY_URL=http://localhost:8000
```

## 🚨 Common Error Messages

### "Port already in use"
```bash
# Find and kill process using port
netstat -ano | findstr :8000    # Windows
lsof -i :8000 && kill -9 <PID>  # macOS/Linux
```

### "Module not found"
```bash
# Install missing packages
pip install -r requirements.txt

# Or install specific package
pip install <package-name>
```

### "Database connection failed"
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Restart PostgreSQL
docker restart chatbot-postgres
```

### "Redis connection failed"
```bash
# Check if Redis is running
docker ps | grep redis

# Restart Redis
docker restart chatbot-redis
```

### "OpenAI API error"
- Check API key is valid
- Verify account has credits
- Check internet connection
- Try different model (gpt-3.5-turbo)

## 🔄 Complete Reset

If nothing works, try a complete reset:

```bash
# Stop all services
docker-compose down

# Remove containers and volumes
docker system prune -a -f
docker volume prune -f

# Kill any Python processes
pkill -f python  # Be careful with this!

# Restart from scratch
python fix_issues.py
```

## 📱 Testing After Fixes

1. **Run the test script again:**
   ```bash
   python test_services.py
   ```

2. **Manual verification:**
   - Visit http://localhost:8501
   - Login with admin/admin123
   - Send a test message
   - Upload a document
   - Check chat history

## 🆘 Getting Help

If issues persist:

1. **Check logs** for detailed error messages
2. **Verify environment** variables are correct
3. **Test network connectivity** between services
4. **Check firewall/antivirus** blocking ports
5. **Try Docker approach** if local setup fails

### System Requirements
- Python 3.10+
- 4GB+ RAM (for AI models)
- 2GB+ disk space
- Internet connection (for OpenAI API)
- Available ports: 5432, 6379, 8000-8004, 8501

### Platform-Specific Notes

**Windows:**
- Use PowerShell or Command Prompt
- May need to install Visual C++ Build Tools
- Windows Defender might block services

**macOS:**
- Use Terminal
- May need to install Xcode Command Line Tools
- Check System Preferences > Security

**Linux:**
- Usually works out of the box
- Check firewall settings (ufw, iptables)
- Verify Docker permissions