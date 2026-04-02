# LoanHub - Loan Application & Management System

LoanHub is a production-grade REST API built using FastAPI, SQLAlchemy, and PostgreSQL (Supabase). It supports role-based access for Users (Applicants) and Admins (Reviewers), featuring automated business logic, background notifications, and comprehensive analytics.

## 🚀 Features

- **Role-Based Access**: 
  - **User**: Register, apply for loans, track status, and view single loan details.
  - **Admin**: View all loans with pagination/filtering, review (approve/reject) pending applications with remarks, and view analytics dashboard.
- **Business Logic**: 
  - Max 3 pending loans per user.
  - Loan amount limits (₹1 to ₹10,00,000).
  - Tenure limits (6 to 360 months).
- **Concurrency**:
  - **Async Notifications**: `asyncio.gather` for concurrent Email/SMS/Push simulation.
  - **Bulk Checking**: `ThreadPoolExecutor` for concurrent eligibility scoring.
- **Infrastructure**:
  - **Alembic**: Full database migration versioning.
  - **Middleware**: Structured request logging to `logs/app.log`.
  - **Decorators**: `@timer` for performance tracking and `@retry` for DB resilience.
- **Analytics**: High-performance dashboard utilizing Python comprehensions.

## 🛠️ Prerequisites

- Python 3.8+
- PostgreSQL database (or Supabase)
- `.env` file based on the provided template

## ⚙️ Setup & Execution

### 1. Installation
Clone the project and install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root directory:
```properties
APP_NAME=LoanHub
DEBUG=true
DATABASE_URL=postgresql://postgres:<password>@<host>:5432/postgres
LOG_LEVEL=INFO
POOL_SIZE=5
MAX_OVERFLOW=10
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin1234
ADMIN_EMAIL=admin@loanhub.com
```

### 3. Database Migrations
Initialize the schema and apply updates:
```bash
python -m alembic upgrade head
```

### 4. Running the Application
Start the uvicorn server:
```bash
python main.py
```
The API will be available at `http://localhost:8000`.
Documentation can be accessed at `http://localhost:8000/docs`.

### 5. Running Tests
Execute the pytest suite:
```bash
python -m pytest tests/ -v
```

## 📜 Project Structure
- `main.py`: Entrypoint & lifespan seeding.
- `models/`: SQLAlchemy models and Pydantic schemas.
- `services/`: Core business logic layer.
- `repositories/`: Data access abstraction.
- `routers/`: API route definitions.
- `utils/`: Asynchronous notifications.
- `logs/`: Application and notification logs.

## 📡 Key Endpoints
- `POST /auth/register`: User registration.
- `POST /auth/login`: Authentication.
- `POST /loans`: Submit application.
- `GET /admin/loans`: (Admin) Manage all loans.
- `PATCH /admin/loans/{id}/review`: (Admin) Approve/Reject.
- `GET /analytics/summary`: (Admin) Visual statistics.
