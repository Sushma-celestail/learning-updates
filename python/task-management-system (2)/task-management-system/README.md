# FastAPI Task Management System

A production-grade REST API for task management built with FastAPI, featuring **SQLAlchemy ORM** connected to **Supabase PostgreSQL**, with **Alembic** migrations and background tasks.

## 🚀 Features

- **User Management**: Register, login, list, and delete users
- **Task Management**: Full CRUD operations with filtering and pagination
- **Database Storage**: Persistent storage in Supabase PostgreSQL via SQLAlchemy ORM
- **Database Migrations**: Managed by Alembic for versioned schema updates
- **Background Tasks**: Notification logging on task creation via FastAPI BackgroundTasks
- **Structured Logging**: Comprehensive logging with timestamps and levels
- **Error Handling**: Custom exceptions with global handlers
- **SOLID Principles**: Clean architecture matching Day 2 interface (DIP)
- **Validation**: Pydantic schemas with field-level validation
- **Pagination & Filtering**: Support for paginated results and multi-field filtering

## 📋 Table of Contents

- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Testing](#testing)
- [Architecture](#architecture)
- [Error Handling](#error-handling)
- [Logging](#logging)

## 📁 Project Structure

```
task_management/
├── main.py                      # Application entry point & DB startup
├── config.py                    # Environment configuration (Pydantic Settings)
├── database.py                  # SQLAlchemy engine & session setup
├── models/
│   ├── schemas.py              # Pydantic models (API layer)
│   ├── db_models.py            # SQLAlchemy models (DB layer)
│   └── enums.py                # Status and Priority enums
├── services/
│   ├── task_service.py         # Task business logic
│   └── user_service.py         # User business logic
├── repositories/
│   ├── base_repository.py      # Repository interface (ABC)
│   └── sqlalchemy_repository.py # SQLAlchemy implementation
├── routers/
│   ├── task_router.py          # Task endpoints & BackgroundTasks
│   └── user_router.py          # User endpoints
├── middleware/
│   └── logging_middleware.py   # Request logging middleware
├── exceptions/
│   └── custom_exceptions.py    # Custom error classes
├── alembic/                    # Migration environment
│   ├── versions/               # Schema version history
│   └── env.py                  # Migration setup
├── alembic.ini                  # Alembic configuration
├── tests/
│   ├── test_tasks.py           # Task tests (using SQLite in-memory)
│   └── test_users.py           # User tests (using SQLite in-memory)
├── logs/
│   ├── app.log                 # Application logs
│   └── notifications.log       # Background task notifications
├── .env                         # Environment variables (DB URL)
├── requirements.txt            # Pinned dependencies
└── README.md                   # This file
```

## 🔧 Requirements

- Python 3.8+
- FastAPI & Uvicorn
- Pydantic & Pydantic-settings
- SQLAlchemy 2.0+
- Alembic (for migrations)
- Psycopg2-binary (PostgreSQL driver)
- Python-dotenv (for .env)
- Pytest & Httpx (for testing)

## 💻 Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd task_management
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

## ⚙️ Configuration

Create a `.env` file in the project root:

```env
APP_NAME=TaskAPI
DEBUG=true
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Database URL for Supabase PostgreSQL
DATABASE_URL=postgresql://user:password@host:5432/postgres
SECRET_KEY=your-secret-key-here
```

## 🏃 Running the Application

1. **Run migrations**
```bash
python -m alembic upgrade head
```

2. **Start the server**
```bash
python main.py
# OR
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. **Access the API**
- API Base URL: `http://localhost:8000`
- Interactive Docs: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

## 📚 API Documentation

### User Endpoints

| Method | Endpoint | Description | Status Code |
|--------|----------|-------------|-------------|
| POST | `/users/register` | Register new user | 201 |
| POST | `/users/login` | Login with credentials | 200 |
| GET | `/users` | List all users | 200 |
| DELETE | `/users/{user_id}` | Delete user | 200 |

### Task Endpoints

| Method | Endpoint | Description | Status Code |
|--------|----------|-------------|-------------|
| POST | `/tasks` | Create new task | 201 |
| GET | `/tasks` | List tasks (with filters) | 200 |
| GET | `/tasks/{task_id}` | Get task by ID | 200 |
| PUT | `/tasks/{task_id}` | Full update | 200 |
| PATCH | `/tasks/{task_id}` | Partial update | 200 |
| DELETE | `/tasks/{task_id}` | Delete task | 200 |

### Query Parameters (GET /tasks)

- `status`: Filter by status (`pending`, `in_progress`, `completed`, `cancelled`)
- `priority`: Filter by priority (`low`, `medium`, `high`)
- `owner`: Filter by owner username
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10)

## 💡 Usage Examples

### Register a User

```bash
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "securepass123"
  }'
```

**Response:**
```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "created_at": "2026-03-23T10:00:00"
}
```

### Login

```bash
curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "securepass123"
  }'
```

### Create a Task

```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Write documentation",
    "description": "Complete API documentation",
    "priority": "high",
    "owner": "alice"
  }'
```

**Response:**
```json
{
  "id": 1,
  "title": "Write documentation",
  "description": "Complete API documentation",
  "status": "pending",
  "priority": "high",
  "owner": "alice",
  "created_at": "2026-03-23T10:05:00",
  "updated_at": "2026-03-23T10:05:00"
}
```

### List Tasks with Filters

```bash
# Get all high-priority tasks
curl "http://localhost:8000/tasks?priority=high"

# Get tasks by owner
curl "http://localhost:8000/tasks?owner=alice"

# Get completed tasks with pagination
curl "http://localhost:8000/tasks?status=completed&page=1&limit=5"
```

### Update a Task (Partial)

```bash
curl -X PATCH "http://localhost:8000/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress"
  }'
```

### Delete a Task

```bash
curl -X DELETE "http://localhost:8000/tasks/1"
```

## 🧪 Testing

### Run Tests

```bash
pytest tests/ -v
```

### Postman Collection

Import the `Day2-TaskAPI.postman_collection.json` file into Postman to test all endpoints.

**Test Folders:**
- **Users**: Register, Login, List Users, Delete User
- **Tasks**: Create, List (with filters), Get by ID, Update, Partial Update, Delete
- **Error Cases**: Invalid payload, Not found, Duplicate user, Bad credentials

## 🏗️ Architecture

### Design Principles

This project follows **SOLID principles**:

#### 1. Single Responsibility Principle (SRP)
- **Routers**: Handle HTTP request/response only
- **Services**: Contain business logic and validation
- **Repositories**: Manage data persistence
- **Middleware**: Handle cross-cutting concerns (logging)

#### 2. Open/Closed Principle (OCP)
- Adding new entities (e.g., Projects) requires only new files
- No modification of existing code needed

#### 3. Liskov Substitution Principle (LSP)
- `JSONRepository` can be replaced with any `BaseRepository` implementation
- Service layer remains unchanged

#### 4. Interface Segregation Principle (ISP)
- Repository interface defines only data access methods
- No unnecessary methods forced on implementations

#### 5. Dependency Inversion Principle (DIP)
- Services depend on `BaseRepository` abstraction
- Concrete implementations injected via FastAPI `Depends()`

### Layer Responsibilities

```
┌─────────────┐
│   Routers   │  ← HTTP layer (FastAPI)
└──────┬──────┘
       │
┌──────▼──────┐
│  Services   │  ← Business logic layer
└──────┬──────┘
       │
┌──────▼──────┐
│ Repositories│  ← Abstract Data Access layer
└──────┬──────┘
       │
┌──────▼──────┐
│ SQLAlchemy  │  ← ORM layer (PostgreSQL)
└─────────────┘
```

## ⚠️ Error Handling

### Custom Exceptions

- `UserNotFoundError` → 404
- `TaskNotFoundError` → 404
- `DuplicateUserError` → 409
- `InvalidCredentialsError` → 401
- `ValidationError` (Pydantic) → 422

### Error Response Format

```json
{
  "error": "TaskNotFoundError",
  "message": "Task with id 999 not found",
  "status_code": 404
}
```

### Handled Edge Cases

- Duplicate usernames during registration
- Empty or whitespace-only input fields
- Missing or corrupted JSON data files
- Invalid enum values
- Pagination beyond available data
- Concurrent file writes (atomic operations)

## 📝 Logging

### Log Format

```
[TIMESTAMP] - LEVEL - MODULE - MESSAGE
```

### Example Log Entries

```
2026-03-23 14:30:00 - INFO - task_router - POST /tasks | 201 | 15ms
2026-03-23 14:31:10 - INFO - user_service - User 'alice' registered
2026-03-23 14:32:05 - WARNING - user_service - Duplicate username: 'alice'
2026-03-23 14:33:00 - ERROR - task_service - Task ID 999 not found
```

### Log Levels

| Level | Usage |
|-------|-------|
| INFO | Successful operations, startup |
| WARNING | Duplicate entries, validation failures |
| ERROR | Not found, file errors, exceptions |

## 🔒 Security Notes

- Passwords are stored as plain text (for demo purposes)
- **Production**: Use bcrypt/argon2 for password hashing
- **Production**: Implement JWT authentication
- **Production**: Add rate limiting
- **Production**: Use environment variables for secrets

## 📄 License

This project is created for educational purposes.

## 👥 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📧 Contact

For questions or support, please contact the development team.

---

**Built with ❤️ using FastAPI**
