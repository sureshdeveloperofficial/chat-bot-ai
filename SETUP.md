# 🛠 Setup Guide

This guide provides detailed setup instructions for the Microservice LLM-based Chatbot project.

## 📋 Prerequisites

### Required Software
- **Python 3.10+**: Download from [python.org](https://python.org)
- **Docker**: Download from [docker.com](https://docker.com)
- **Docker Compose**: Usually included with Docker Desktop
- **Git**: For cloning the repository

### Required Accounts
- **OpenAI Account**: Get API key from [platform.openai.com](https://platform.openai.com)

## 🚀 Quick Setup (Recommended)

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd chatai
```

### Step 2: Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit with your favorite editor
nano .env  # or code .env, vim .env, etc.
```

**Required Environment Variables:**
```env
# Essential - Update these values
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
SECRET_KEY=your-super-secret-jwt-key-min-32-chars

# Optional - Can keep defaults for local development
DATABASE_URL=postgresql://user:password@localhost:5432/chatbot_db
REDIS_URL=redis://localhost:6379
```

### Step 3: Start Services
```bash
# Start all services with Docker Compose
docker-compose up --build

# Or run in background
docker-compose up --build -d
```

### Step 4: Access Application
- **Frontend UI**: http://localhost:8501
- **API Gateway**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Step 5: Test with Default Users
- Username: `admin`, Password: `admin123`
- Username: `user`, Password: `user123`

## 🔧 Development Setup

For local development without Docker:

### Step 1: Install Python Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start Infrastructure Services
```bash
# Start only PostgreSQL and Redis
docker-compose up postgres redis -d
```

### Step 3: Configure Environment Files
Create `.env` files in each service directory:

```bash
# Copy environment templates
cp auth-service/.env.example auth-service/.env
cp gateway/.env.example gateway/.env
cp chat-service/.env.example chat-service/.env
cp user-service/.env.example user-service/.env
cp vector-service/.env.example vector-service/.env
cp frontend/.env.example frontend/.env
```

### Step 4: Start Services Individually
Open separate terminals for each service:

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

## ☁️ Production Deployment

### Docker Compose Production

1. **Update Environment Variables**
```env
# Production .env file
OPENAI_API_KEY=your-production-openai-key
SECRET_KEY=your-production-secret-key-32-chars-minimum
DATABASE_URL=postgresql://prod_user:secure_password@postgres:5432/chatbot_prod
```

2. **Deploy**
```bash
docker-compose -f docker-compose.yml up -d
```

### Kubernetes Deployment

1. **Prerequisites**
   - Kubernetes cluster (local or cloud)
   - kubectl configured
   - Container registry access

2. **Update Secrets**
```bash
# Create base64 encoded secrets
echo -n "your-openai-api-key" | base64
echo -n "your-secret-key" | base64

# Update deploy/kubernetes/configmap.yaml with encoded values
```

3. **Deploy Infrastructure**
```bash
kubectl apply -f deploy/kubernetes/namespace.yaml
kubectl apply -f deploy/kubernetes/postgres.yaml
kubectl apply -f deploy/kubernetes/redis.yaml
kubectl apply -f deploy/kubernetes/configmap.yaml
```

4. **Build and Push Images**
```bash
# Build all images
docker build -t your-registry/chatbot/auth-service:v1.0.0 ./auth-service
docker build -t your-registry/chatbot/user-service:v1.0.0 ./user-service
docker build -t your-registry/chatbot/vector-service:v1.0.0 ./vector-service
docker build -t your-registry/chatbot/chat-service:v1.0.0 ./chat-service
docker build -t your-registry/chatbot/gateway:v1.0.0 ./gateway
docker build -t your-registry/chatbot/frontend:v1.0.0 ./frontend

# Push to registry
docker push your-registry/chatbot/auth-service:v1.0.0
# ... repeat for all services
```

5. **Update Image References**
Update image names in Kubernetes YAML files to use your registry.

6. **Deploy Services**
```bash
kubectl apply -f deploy/kubernetes/auth-service.yaml
kubectl apply -f deploy/kubernetes/user-service.yaml
kubectl apply -f deploy/kubernetes/vector-service.yaml
kubectl apply -f deploy/kubernetes/chat-service.yaml
kubectl apply -f deploy/kubernetes/gateway.yaml
kubectl apply -f deploy/kubernetes/frontend.yaml
```

7. **Check Deployment**
```bash
kubectl get pods -n chatbot
kubectl get services -n chatbot
```

## 🔧 Configuration Details

### OpenAI API Key Setup

1. Visit [platform.openai.com](https://platform.openai.com)
2. Create account or login
3. Navigate to API Keys section
4. Create new API key
5. Copy key to your `.env` file

**Note**: Keep your API key secure and never commit it to version control.

### Database Configuration

**Local Development (Default):**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/chatbot_db
```

**Production Examples:**
```env
# AWS RDS
DATABASE_URL=postgresql://username:password@mydb.cluster-xyz.us-west-2.rds.amazonaws.com:5432/chatbot_prod

# Google Cloud SQL
DATABASE_URL=postgresql://username:password@/chatbot_prod?host=/cloudsql/project:region:instance

# Azure Database
DATABASE_URL=postgresql://username@server:password@server.postgres.database.azure.com:5432/chatbot_prod?sslmode=require
```

### Redis Configuration

**Local Development (Default):**
```env
REDIS_URL=redis://localhost:6379
```

**Production Examples:**
```env
# AWS ElastiCache
REDIS_URL=redis://my-cluster.abc123.cache.amazonaws.com:6379

# Redis Cloud
REDIS_URL=redis://username:password@redis-host:port
```

## 🧪 Verification & Testing

### Health Checks
```bash
# Check all services are running
curl http://localhost:8000/health

# Individual service health
curl http://localhost:8001/health  # Auth
curl http://localhost:8002/health  # Chat
curl http://localhost:8003/health  # User
curl http://localhost:8004/health  # Vector
```

### API Testing
```bash
# Test authentication
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Test chat (replace TOKEN with actual token)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"message": "Hello, how are you?"}'
```

### Frontend Testing
1. Open http://localhost:8501
2. Login with default credentials
3. Send test message
4. Upload a test document
5. Verify chat history

## 🚨 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Find process using port
lsof -i :8000  # On macOS/Linux
netstat -ano | findstr :8000  # On Windows

# Kill process
kill -9 <PID>  # On macOS/Linux
taskkill /PID <PID> /F  # On Windows
```

**2. Docker Issues**
```bash
# Clean up Docker
docker-compose down
docker system prune -f
docker-compose up --build
```

**3. Database Connection**
```bash
# Check PostgreSQL
docker-compose logs postgres

# Manual connection test
docker exec -it chatai_postgres_1 psql -U user -d chatbot_db
```

**4. OpenAI API Issues**
- Verify API key is correct
- Check API quota and billing
- Test with simple curl request

**5. Memory Issues**
```bash
# Check Redis
docker-compose logs redis
redis-cli ping
```

### Performance Optimization

**For Production:**
1. Use production-grade database (not Docker PostgreSQL)
2. Use managed Redis service
3. Configure proper resource limits
4. Enable logging and monitoring
5. Use load balancers for high availability

## 📚 Next Steps

After successful setup:
1. Explore the API documentation at http://localhost:8000/docs
2. Upload documents to test RAG functionality
3. Create custom users and test multi-user scenarios
4. Review logs for any errors or warnings
5. Consider enabling monitoring and alerting for production

## 🆘 Getting Help

If you encounter issues:
1. Check this troubleshooting guide
2. Review service logs: `docker-compose logs <service>`
3. Verify environment variables are set correctly
4. Check API connectivity and credentials
5. Create an issue in the repository with detailed error logs