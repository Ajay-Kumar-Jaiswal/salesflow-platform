# SalesFlow CRM

> A full-stack CRM platform for managing customers, sales opportunities,
> activities, and follow-ups.

Built with **FastAPI**, **SQLAlchemy 2.x**, **Pydantic v2**, **Alembic**,
**MySQL**, and a responsive JavaScript frontend.

---

## 📋 Overview

SalesFlow CRM provides tools for managing customer relationships and sales workflows
through a centralized platform.

The application includes customer management, a Kanban sales pipeline,
activity tracking, follow-up management, dashboard analytics,
JWT authentication, and role-based access control.

The backend follows a layered architecture:

`Router → Service → Model → Database`

---

## ✨ Features

- **CRM Dashboard**
  - Customer, opportunity, pipeline, revenue, and conversion metrics
  - Pipeline stage and customer status breakdowns
  - Upcoming follow-ups and recent activity

- **Customer Management**
  - Customer CRUD with validation
  - Search, filtering, pagination, and sorting
  - Customer 360 view with deals, activities, and follow-ups

- **Sales Pipeline**
  - Kanban-based opportunity management
  - Deal stages, values, probabilities, and expected close dates
  - Persistent stage updates

- **Activity Tracking**
  - Log calls, emails, meetings, demos, notes, and other interactions
  - Customer-specific activity timelines

- **Follow-up Management**
  - Schedule and track follow-up tasks
  - Today, upcoming, completed, and all task views

- **Authentication & RBAC**
  - JWT-based authentication
  - Admin and Sales Representative roles
  - Role-based access to customers and opportunities

---

## 🛠️ Tech Stack

### Backend
- **Python 3.12+**
- **FastAPI**
- **SQLAlchemy 2.x**
- **Pydantic v2**
- **Alembic**
- **PyMySQL**
- **PyJWT**
- **Bcrypt**
- **Uvicorn**

### Frontend
- **HTML5**
- **CSS3**
- **Vanilla JavaScript (ES6+)**

### Database & Testing
- **MySQL 8.0**
- **Pytest**
- **HTTPX**

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

SalesFlow CRM uses JWT-based authentication with `HS256` and role-based access control.

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
- MySQL 8.0
- Modern web browser

### 1. Environment Configuration

Copy the example environment file:

```bash
cd backend
cp .env.example .env
```

Configure `backend/.env` with your settings:

```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/salesflow
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ENVIRONMENT=development
```


### 2. Local Backend Setup

```bash
cd backend

python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt

alembic upgrade head

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The interactive Swagger API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 3. Frontend Setup

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
