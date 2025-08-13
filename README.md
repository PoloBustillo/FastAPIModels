# 🚀 AI API Skeleton with FastAPI & Docker

## Project Structure

```
AI-API-Skeleton/
├── main.py            # FastAPI application
├── requirements.txt   # Python dependencies
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Local development with Docker
├── README.md          # Project documentation
└── .gitignore         # Python best practices
```

## Getting Started

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd AI-API-Skeleton
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run locally
```bash
uvicorn main:app --reload
```

### 4. Run with Docker
```bash
docker-compose up --build
```

### 5. API Documentation (Swagger UI)
FastAPI automatically provides interactive API docs at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

You can view and test your endpoints directly from these pages when the server is running.

## API Endpoints
- `GET /` — Welcome message
- `GET /health` — Health check

## Best Practices
- Use virtual environments for Python development.
- Add new dependencies to requirements.txt.
- Write tests in a `tests/` folder (not included in skeleton).

---
This skeleton is ready for building AI-powered APIs with FastAPI.
