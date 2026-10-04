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
│   ├── alembic/              # Database migrations
│   ├── app/
│   │   ├── core/             # Configuration, authentication & RBAC
│   │   ├── database/         # Database connection & sessions
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   └── routers/          # FastAPI API routes
│   ├── tests/                # Automated tests
│   ├── requirements.txt
│   ├── alembic.ini
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
├── .gitignore
└── README.md
```

---

## 🗄️ Database

SalesFlow CRM uses MySQL with a relational schema connecting users, customers,
opportunities, activities, and follow-ups.
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

## 📡 API

The backend exposes RESTful APIs for:

- Authentication and user management
- Customer management
- Sales opportunities and pipeline stages
- Customer activities and timelines
- Follow-up task management
- Dashboard analytics

Interactive API documentation is available through FastAPI:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
