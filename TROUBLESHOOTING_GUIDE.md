# 🚨 Troubleshooting Guide

This guide helps resolve common issues with the Microservice Chatbot project.

## 📋 Test Results Analysis

Based on your test results:
- ✅ Auth Service: Working
- ❌ User Service: Database connection issue
- ✅ Vector Service: Working  
- ✅ Chat Service: OpenAI quota exceeded
- ✅ Gateway: Working (user service unavailable)
- ❌ Frontend: Not accessible

## 🔧 Quick Fixes

### 1. OpenAI API Quota Issue (429 Error)

**Problem**: `You exceeded your current quota`

**Solutions**:

**Option A: Use Mock Chat Service (Recommended for Testing)**
```bash
# Use mock chat instead of OpenAI
cd chat-service
python mock_main.py
```

**Option B: Fix OpenAI Account**
- Check your OpenAI billing at [platform.openai.com](https://platform.openai.com/account/billing)
- Add payment method or upgrade plan
- Wait for quota reset (if on free tier)

### 2. User Service Database Issue

**Problem**: Database connection failed

**Solution**: Use SQLite (already configured)
```bash
# Verify SQLite database exists
cd user-service
ls -la chatbot.db  # Should show the database file

# If missing, restart the service to auto-create
python main.py
```

### 3. Frontend Not Accessible

**Problem**: Frontend service not running

**Solution**: Start the frontend
```bash
# Method 1: Direct start
cd frontend
streamlit run app.py

# Method 2: Use helper script
python start_frontend.py
```

## 🚀 Complete Setup Solutions

### Option 1: Start All Services with Mock Chat

```bash
# This starts all services with mock chat (no OpenAI needed)
python start_mock_services.py
```

### Option 2: Manual Service Start

Open 6 separate terminals and run:

```bash
# Terminal 1 - Auth Service
cd auth-service
python main.py

# Terminal 2 - User Service
cd user-service  
python main.py

# Terminal 3 - Vector Service (requires OpenAI)
cd vector-service
python main.py

# Terminal 4 - Mock Chat Service (no OpenAI)
cd chat-service
python mock_main.py

# Terminal 5 - Gateway
cd gateway
python main.py

# Terminal 6 - Frontend
cd frontend
streamlit run app.py
```

## 📞 Getting Help

1. Check service logs for specific errors
2. Verify all environment variables are set
3. Ensure ports are not blocked by firewall
4. Test individual components before integration