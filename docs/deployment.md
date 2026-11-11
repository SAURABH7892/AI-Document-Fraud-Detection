# DocShield AI — Deployment & DevOps Guide

## 1. Local Development (Zero External Cloud Dependencies)
DocShield AI is architected to run immediately in a standard local Python + Node.js environment without requiring paid APIs or Docker.

### Prerequisites:
- Python 3.11+
- Node.js 18+ & npm

### Step 1: Backend Setup
```bash
# In the workspace root
pip install -r backend/requirements.txt
pip install pytest httpx email-validator

# Train the ML baseline classifier
python -m ai.training.train

# Start the FastAPI backend server (Runs on port 8000)
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 2: Frontend Setup
```bash
# In another terminal
cd frontend
npm install
npm run dev
# Frontend is accessible at http://localhost:3000
```

---

## 2. Multi-Container Docker Compose Deployment
For production staging or full containerized isolation:

```bash
# Copy and configure environment variables
cp .env.example .env

# Build and start all 5 microservices:
# (PostgreSQL 15, Redis 7, FastAPI Backend, Celery AI Worker, Next.js Frontend)
docker-compose up --build -d
```

### Services Launched:
- `docshield-backend`: `http://localhost:8000` (FastAPI REST API)
- `docshield-frontend`: `http://localhost:3000` (Next.js App Router Web UI)
- `docshield-postgres`: `localhost:5432` (PostgreSQL Database)
- `docshield-redis`: `localhost:6379` (Redis Queue Broker)
- `docshield-celery-worker`: Distributed Celery worker pool executing OCR & forensics

---

## 3. Cloud Deployment (AWS / GCP / VPS)
- **Container Registry:** Push backend and frontend images to Amazon ECR or Docker Hub.
- **Compute:** Deploy backend and worker containers to AWS ECS (Fargate) or Kubernetes cluster.
- **Database:** Managed Amazon RDS for PostgreSQL.
- **Object Storage:** Configure `STORAGE_TYPE=s3` and point to an S3 bucket with private read-write permissions and signed URLs.
- **Frontend:** Deploy Next.js to Vercel or AWS Amplify / ECS with `NEXT_PUBLIC_API_URL` set to the API gateway.
