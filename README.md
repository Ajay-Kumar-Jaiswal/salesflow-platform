# SalesFlow CRM

> **Enterprise-grade Customer Relationship Management (CRM) REST API and Single-Page Application.**
> Engineered with **FastAPI**, **SQLAlchemy 2.x**, **Pydantic v2**, **Alembic**, and a responsive modern JavaScript frontend.

---

## 📋 Overview

**SalesFlow CRM** is a modern, modular CRM system tailored for high-velocity sales and account management teams. Originally migrated from a Spring Boot/Hibernate prototype, this application was refactored into a high-performance Python/FastAPI architecture following clean layered design principles (`Router → Service → Model/Repository → Database`).

It provides end-to-end management of customer lifecycles, interactive sales deal pipelines (Kanban board), activity logging timelines, scheduled follow-up reminders, and executive dashboard analytics with zero simulated or mock data.

---

## ✨ Features

- **Executive CRM Dashboard**:
  - Real-time KPI summaries: Total Customers, Open Opportunities, Won Opportunities, Pipeline Value, Won Revenue, and Win Conversion Rate.
  - Interactive pipeline stage funnel chart (LEAD, CONTACTED, QUALIFIED, PROPOSAL, NEGOTIATION, WON, LOST).
  - Customer status breakdown distribution.
  - Live feeds of upcoming follow-ups, chronological activity stream, and recently onboarded accounts.
- **Customer Lifecycle Management**:
  - Full CRUD operations with email validation, phone, company, industry, and lead source tracking.
  - Advanced search (name, email, company), multi-status filtering, and configurable pagination & sorting.
  - Dedicated **Customer 360 Detail View** consolidating company context, notes, deal pipeline, activity history, and upcoming tasks.
- **Visual Sales Pipeline (Kanban Board)**:
  - Multi-stage deal board with column aggregations (deal counts and weighted dollar values).
  - Drag-and-drop and dropdown stage transitions with immediate database persistence.
- **Activity Tracking & Chronological Timelines**:
  - Log interactions: `CALL`, `EMAIL`, `MEETING`, `DEMO`, `NOTE`, and `OTHER`.
  - Reverse chronological timeline view per customer and system-wide.
- **Scheduled Follow-up Reminders**:
  - Actionable task manager categorized by *Today*, *Upcoming*, *Completed*, and *All*.
  - Inline completion toggle and task deadline management.
- **Enterprise Security & Role-Based Access Control (RBAC)**:
  - Cryptographically secure password hashing using `bcrypt`.
  - Stateless JWT authentication (`Bearer` tokens) with user scoping.
  - Granular RBAC (`ADMIN` vs. `SALES_REP`): Sales representatives manage their assigned accounts and opportunities, while administrators have system-wide visibility and team administration privileges.
  - Restricted CORS origins controlled via environment variables (no open `*` wildcards).
  - Sanitized API error handlers preventing database credentials or stack trace leaks.

---

## 🛠️ Tech Stack

### Backend
- **Python 3.12+ / 3.13**
- **FastAPI**: Asynchronous high-performance web framework
- **SQLAlchemy 2.x**: Modern ORM with clean declarative mapping
- **Alembic**: Database migrations and version tracking
- **Pydantic v2**: Strict schema validation and serialization
- **PyMySQL & Cryptography**: Native MySQL 8.0 connectivity
- **PyJWT & Bcrypt**: Secure token issuance and password hashing
- **Uvicorn**: ASGI web server

### Frontend
- **HTML5 & CSS3**: Custom responsive enterprise design system, CSS variables, accessible layout
- **Vanilla Modern JavaScript (ES6+)**: Centralized API abstraction, state management, modal system, HTML5 drag-and-drop

### Infrastructure & Testing
- **MySQL 8.0**: Relational database engine
- **Docker & Docker Compose**: Multi-container orchestration
- **Pytest & HTTPX**: Automated integration and regression test suite

---

## 🏗️ Architecture & Project Structure

```
salesflow-crm/
├── backend/
│   ├── alembic/              # Database schema migrations
│   │   ├── versions/         # Revision migration scripts
│   │   └── env.py            # Migration runtime config
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI entrypoint & middleware
│   │   ├── core/             # Configuration & security
│   │   │   ├── config.py     # Pydantic BaseSettings (.env loading)
│   │   │   ├── security.py   # JWT encoding/decoding & bcrypt hashing
│   │   │   └── dependencies.py # Auth & RBAC dependencies
│   │   ├── database/         # Database engine & sessionmaker
│   │   │   └── database.py
│   │   ├── models/           # SQLAlchemy 2.0 ORM models
│   │   │   ├── user.py
│   │   │   ├── customer.py
│   │   │   ├── activity.py
│   │   │   ├── opportunity.py
│   │   │   └── follow_up.py
│   │   ├── schemas/          # Pydantic v2 validation models
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── customer.py
│   │   │   ├── activity.py
│   │   │   ├── opportunity.py
│   │   │   ├── follow_up.py
│   │   │   └── dashboard.py
│   │   ├── services/         # Layered business logic
│   │   │   ├── auth_service.py
│   │   │   ├── customer_service.py
│   │   │   ├── opportunity_service.py
│   │   │   ├── activity_service.py
│   │   │   ├── follow_up_service.py
│   │   │   └── dashboard_service.py
│   │   └── routers/          # FastAPI REST endpoints
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── customers.py
│   │       ├── activities.py
│   │       ├── opportunities.py
│   │       ├── follow_ups.py
│   │       └── dashboard.py
│   ├── tests/                # Automated pytest suite (32 tests)
│   │   ├── conftest.py       # Isolated database & auth fixtures
│   │   ├── test_auth.py
│   │   ├── test_customers.py
│   │   ├── test_opportunities.py
│   │   ├── test_activities.py
│   │   ├── test_follow_ups.py
│   │   └── test_dashboard.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   └── .env.example
├── frontend/                 # Client UI application
│   ├── index.html            # Single-page application structure
│   ├── app.js                # Client controller & API layer
│   └── style.css             # Enterprise styling & layout
├── docker-compose.yml        # Docker composition (MySQL + Backend + Frontend)
├── .gitignore
└── README.md
```

---

## 🗄️ Database Schema

```mermaid
erDiagram
    USERS ||--o{ CUSTOMERS : "assigned to"
    USERS ||--o{ ACTIVITIES : "performed by"
    USERS ||--o{ OPPORTUNITIES : "owns"
    USERS ||--o{ FOLLOW_UPS : "assigned to"

    CUSTOMERS ||--o{ ACTIVITIES : "has"
    CUSTOMERS ||--o{ OPPORTUNITIES : "has"
    CUSTOMERS ||--o{ FOLLOW_UPS : "has"

    USERS {
        int id PK
        string name
        string email UK
        string hashed_password
        string role
        datetime created_at
        datetime updated_at
    }

    CUSTOMERS {
        int id PK
        string name
        string email
        string phone
        string company
        string industry
        string status
        string source
        int assigned_to FK
        text notes
        datetime created_at
        datetime updated_at
    }

    ACTIVITIES {
        int id PK
        int customer_id FK
        int user_id FK
        string activity_type
        string title
        text description
        datetime created_at
    }

    OPPORTUNITIES {
        int id PK
        int customer_id FK
        string title
        text description
        float amount
        string stage
        float probability
        datetime expected_close_date
        int assigned_to FK
        datetime created_at
        datetime updated_at
    }

    FOLLOW_UPS {
        int id PK
        int customer_id FK
        int user_id FK
        string title
        text description
        string follow_up_type
        datetime scheduled_at
        boolean completed
        datetime created_at
        datetime updated_at
    }
```

---

## 🔒 Authentication & Roles

SalesFlow CRM implements JWT-based authentication using `HS256`.

### Roles & Access Matrix

| Feature | ADMIN | SALES_REP |
| :--- | :---: | :---: |
| View System Dashboard | Full System | Assigned Pipeline |
| Manage Team Users | Yes | No |
| Create Customers | Yes | Yes |
| Edit / Delete Customers | All Customers | Assigned Only |
| Move Deals in Pipeline | All Deals | Assigned Deals |
| Log Activities & Follow-ups | Yes | Yes |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12 or newer
- MySQL 8.0 (or Docker)
- Modern web browser

### 1. Environment Configuration

Copy the example environment file inside `backend/`:

```bash
cd backend
cp .env.example .env
```

Configure `backend/.env` with your settings:

```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/salesflow
SECRET_KEY=generate_a_random_32_character_string_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5500,http://localhost:8000
ENVIRONMENT=development
```

> **Note**: For quick local testing without MySQL running, you can set `DATABASE_URL=sqlite:///./salesflow.db`.

### 2. Local Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
# On Linux/macOS: source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The interactive Swagger API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 3. Frontend Setup

You can open `frontend/index.html` directly in any web browser, or serve it using Python's built-in HTTP server or VS Code Live Server:

```bash
cd frontend
python -m http.server 3000
```

Open `http://localhost:3000` in your browser.

---

## 🧪 Running Automated Tests

SalesFlow CRM includes a test suite covering authentication, customer CRUD, pagination, filtering, deal pipeline stages, activities, follow-ups, and dashboard aggregations.

Run tests using pytest:

```bash
cd backend
pytest -v
```

Expected output:
```
============================== 32 passed in 7.20s ==============================
```

---

## 📡 API Reference

### Authentication
- `POST /api/auth/register` - Create a new user account
- `POST /api/auth/login` - Authenticate and obtain JWT access token
- `GET  /api/auth/me` - Get profile of the current authenticated user

### Customers
- `GET    /api/customers` - Paginated customer list (`?search=`, `?status=`, `?page=`, `?page_size=`)
- `GET    /api/customers/{id}` - Retrieve customer record
- `POST   /api/customers` - Create customer record
- `PUT    /api/customers/{id}` - Update customer
- `DELETE /api/customers/{id}` - Delete customer

### Pipeline & Opportunities
- `GET    /api/opportunities` - List deals (`?customer_id=`, `?stage=`)
- `GET    /api/opportunities/{id}` - Retrieve deal details
- `POST   /api/opportunities` - Create sales opportunity
- `PUT    /api/opportunities/{id}` - Update deal amount, probability, or stage
- `DELETE /api/opportunities/{id}` - Delete deal

### Activities & Follow-ups
- `GET    /api/customers/{customer_id}/activities` - Customer activity timeline
- `POST   /api/customers/{customer_id}/activities` - Log interaction (`CALL`, `EMAIL`, `MEETING`, etc.)
- `GET    /api/follow-ups` - List scheduled follow-ups (`?filter_status=today|upcoming|completed|all`)
- `POST   /api/follow-ups` - Schedule follow-up task
- `PUT    /api/follow-ups/{id}` - Update task or toggle completion
- `DELETE /api/follow-ups/{id}` - Remove follow-up

### Dashboard
- `GET    /api/dashboard/summary` - Aggregated CRM metrics and distributions

---

## 📄 License

This project is licensed under the MIT License.
