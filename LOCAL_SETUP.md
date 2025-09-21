# 🚀 Local Setup Complete! 

✅ **ALL DEPENDENCIES INSTALLED AND CONFIGURED**

Your microservice chatbot is ready to run!

## 🎯 Quick Start (3 Simple Steps)

### Step 1: Start All Services
```bash
python quick_start.py
```

### Step 2: Wait for Startup (30-60 seconds)
Services will open in separate console windows.

### Step 3: Access the Application
**Open your browser:** http://localhost:8501

## 🔐 Login Credentials

### For Windows:
```cmd
# 1. Install all dependencies
install_local.bat

# 2. Edit .env file with your OpenAI API key
notepad .env

# 3. Start all services
start_local.bat
```

### For Linux/macOS:
```bash
# 1. Install all dependencies
./install_local.sh

# 2. Edit .env file with your OpenAI API key
nano .env

# 3. Start all services
./start_local.sh
```

## 🔧 Manual Setup (Step by Step)

### Step 1: Install Dependencies

```bash
# Install using Python script
python install_local.py

# Or manually:
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
pip install -r auth-service/requirements.txt
pip install -r gateway/requirements.txt
pip install -r chat-service/requirements.txt
pip install -r user-service/requirements.txt
pip install -r vector-service/requirements.txt
pip install -r frontend/requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy environment files
cp .env.example .env
cp auth-service/.env.example auth-service/.env
cp gateway/.env.example gateway/.env
cp chat-service/.env.example chat-service/.env
cp user-service/.env.example user-service/.env
cp vector-service/.env.example vector-service/.env
cp frontend/.env.example frontend/.env
```

**Edit `.env` file with your actual values:**
```env
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
SECRET_KEY=your-super-secret-key-change-in-production
DATABASE_URL=postgresql://user:password@localhost:5432/chatbot_db
REDIS_URL=redis://localhost:6379
```

### Step 3: Start Infrastructure

**Option A: Using Docker (Recommended)**
```bash
# Start PostgreSQL and Redis
docker-compose up postgres redis -d

# Initialize database
python init_database.py
```

**Option B: Install Locally**

**PostgreSQL:**
- Windows: Download from [postgresql.org](https://postgresql.org)
- macOS: `brew install postgresql`
- Linux: `sudo apt-get install postgresql`

Create database:
```sql
-- Connect to PostgreSQL as superuser
createdb chatbot_db
-- Or manually: CREATE DATABASE chatbot_db;
```

**Redis:**
- Windows: Use Redis Stack or WSL
- macOS: `brew install redis`
- Linux: `sudo apt-get install redis-server`

### Step 4: Start Services

**Option A: Automated (Recommended)**
```bash
# Windows
start_local.bat

# Linux/macOS
./start_local.sh
```

**Option B: Manual**

Open 6 separate terminals and run:

```bash
# Terminal 1 - Auth Service
cd auth-service
python main.py

# Terminal 2 - User Service
cd user-service
python main.py

# Terminal 3 - Vector Service
cd vector-service
python main.py

# Terminal 4 - Chat Service
cd chat-service
python main.py

# Terminal 5 - Gateway
cd gateway
python main.py

# Terminal 6 - Frontend
cd frontend
streamlit run app.py
```

## 🌐 Access the Application

Once all services are running:

- **Frontend UI**: http://localhost:8501
- **API Gateway**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs

### Default Test Users:
- Username: `admin`, Password: `admin123`
- Username: `user`, Password: `user123`

## 📊 Service Status Check

Check if all services are healthy:

```bash
# Using curl
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health

# Or visit in browser
http://localhost:8000/health
```

## 🔧 Development Workflow

### Making Changes

1. **Stop services** (Ctrl+C in terminal or stop script)
2. **Make your changes** to the code
3. **Restart services** using start script

### Adding New Dependencies

```bash
# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Install new package
pip install new-package

# Update requirements file
pip freeze > requirements.txt
# Or for specific service
pip freeze > auth-service/requirements.txt
```

### Database Changes

If you modify database schemas:

```bash
# Reinitialize database
python init_database.py

# Or manually connect and run SQL
docker exec -it chatai_postgres_1 psql -U user -d chatbot_db
```

## 🧪 Testing the Application

### 1. User Registration/Login
1. Open http://localhost:8501
2. Click "Register" tab
3. Create a new account
4. Login with credentials

### 2. Basic Chat
1. After login, send a message: "Hello, how are you?"
2. Verify you get a response from OpenAI

### 3. Document Upload
1. Click "Browse files" in sidebar
2. Upload a text/PDF file
3. Send a question about the document
4. Verify contextual responses

### 4. Chat History
1. Send multiple messages
2. Check "Chat History" in sidebar
3. Click on previous sessions

## 🚨 Troubleshooting

### Common Issues

**1. Python Version Error**
```
❌ Python 3.10+ required
```
**Solution:** Install Python 3.10 or higher from python.org

**2. Virtual Environment Issues**
```
❌ Virtual environment not found
```
**Solution:** 
```bash
python -m venv venv
# Then run install script again
```

**3. OpenAI API Errors**
```
❌ OpenAI API key not configured
```
**Solution:** Edit `.env` file and add your actual API key:
```env
OPENAI_API_KEY=sk-your-actual-key-here
```

**4. Database Connection Error**
```
❌ Could not connect to PostgreSQL
```
**Solution:**
- Ensure PostgreSQL is running
- Check connection string in `.env`
- For Docker: `docker-compose up postgres -d`

**5. Redis Connection Error**
```
❌ Redis connection failed
```
**Solution:**
- Ensure Redis is running
- For Docker: `docker-compose up redis -d`
- Services will work without Redis (uses in-memory storage)

**6. Port Already in Use**
```
❌ Port 8000 already in use
```
**Solution:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :8000
kill -9 <PID>
```

**7. Import Errors**
```
❌ ModuleNotFoundError: No module named 'fastapi'
```
**Solution:**
```bash
# Activate virtual environment first
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Then install dependencies
pip install -r requirements.txt
```

### Service-Specific Issues

**Auth Service (Port 8001)**
- Check if SECRET_KEY is set in `.env`
- Verify database connection

**Chat Service (Port 8002)**
- Verify OpenAI API key is valid
- Check Redis connection (optional)
- Ensure other services are running

**Vector Service (Port 8004)**
- Verify OpenAI API key for embeddings
- Check write permissions for vector storage
- Ensure sufficient disk space

**Frontend (Port 8501)**
- Check if Streamlit is installed: `pip install streamlit`
- Verify gateway is running on port 8000

### Logs and Debugging

**View service logs:**
```bash
# If using automated script, logs appear in terminal
# For Docker infrastructure:
docker-compose logs postgres
docker-compose logs redis

# For individual service debugging:
cd auth-service
python main.py  # See error messages directly
```

**Enable debug mode:**
Add to service `.env` files:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

## 🔧 Performance Optimization

### For Better Performance:

1. **Use SSD storage** for vector databases
2. **Increase memory** for vector operations
3. **Use production database** instead of Docker PostgreSQL
4. **Enable Redis** for better session management
5. **Configure proper logging** levels

### Resource Usage:
- **RAM**: ~2-4GB total for all services
- **CPU**: Modern multi-core processor recommended
- **Storage**: ~1GB + documents uploaded
- **Network**: Internet connection for OpenAI API

## 📚 Next Steps

After successful setup:

1. **Explore the codebase** - Each service is well-documented
2. **Read API documentation** - http://localhost:8000/docs
3. **Upload test documents** - Try different file formats
4. **Modify prompts** - Customize chat behavior
5. **Add new features** - The architecture is extensible

## 🆘 Getting Help

If you're still having issues:

1. **Check this troubleshooting section**
2. **Review service logs** for specific errors
3. **Verify environment variables** are correct
4. **Test components individually** (database, Redis, OpenAI API)
5. **Create an issue** in the repository with:
   - Your operating system
   - Python version
   - Error messages
   - Steps you've tried

## 🎯 Success Indicators

You'll know everything is working when:

- ✅ All 6 services start without errors
- ✅ Health checks return 200 OK
- ✅ Frontend loads at http://localhost:8501
- ✅ You can login with default users
- ✅ Chat responses come from OpenAI
- ✅ Document upload and search work
- ✅ Chat history is saved and retrievable

Happy coding! 🚀