# 🏨 Hostel Management System

A complete full-stack web application built with **Flask + MySQL + Vanilla JS**.

---

## 📁 Folder Structure

```
hostel/
├── app.py                  # Flask entry point
├── database.py             # MySQL connection helper
├── database.sql            # Full schema + sample data
├── setup_db.py             # One-time DB init script
├── generate_hash.py        # Bcrypt hash utility
├── requirements.txt
├── .env                    # DB credentials (edit this!)
├── routes/
│   ├── __init__.py
│   ├── auth.py             # Login / Register
│   ├── students.py         # Student CRUD
│   ├── hostels.py          # Hostel CRUD
│   ├── rooms.py            # Rooms + Allocations
│   ├── visitors.py         # Visitor logs
│   ├── furniture.py        # Furniture CRUD
│   └── dashboard.py        # Stats endpoint
├── templates/
│   ├── login.html          # Login / Register page
│   └── dashboard.html      # Main SPA dashboard
└── static/
    ├── style.css           # Full dark-theme CSS
    └── app.js              # All frontend JS logic
```

---

## ⚙️ Setup & Run (Step-by-Step)

### 1. Prerequisites
- Python 3.10+
- MySQL Server running locally
- A MySQL user (e.g. `root`) with a known password

---

### 2. Configure Database Credentials

Open `.env` and update:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD_HERE
DB_NAME=hostel_db
SECRET_KEY=hostel_super_secret_key_change_this
```

---

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Initialise the Database

```bash
python setup_db.py
```

This creates `hostel_db`, all tables, and inserts sample data.

✅ Default Admin Login:
- **Username:** `admin`
- **Password:** `admin123`

---

### 5. Start the Flask Server

```bash
python app.py
```

Server starts at: **http://localhost:5000**

---

## 🔌 API Endpoints Reference

| Module      | Method | Endpoint                       | Description              |
|-------------|--------|--------------------------------|--------------------------|
| Auth        | POST   | `/api/auth/register`           | Register admin           |
| Auth        | POST   | `/api/auth/login`              | Login → get JWT token    |
| Dashboard   | GET    | `/api/dashboard/stats`         | Summary stats            |
| Students    | GET    | `/api/students/`               | List all students        |
| Students    | POST   | `/api/students/`               | Add student              |
| Students    | PUT    | `/api/students/<id>`           | Update student           |
| Students    | DELETE | `/api/students/<id>`           | Delete student           |
| Hostels     | GET    | `/api/hostels/`                | List hostels             |
| Hostels     | POST   | `/api/hostels/`                | Add hostel               |
| Hostels     | DELETE | `/api/hostels/<id>`            | Delete hostel            |
| Rooms       | GET    | `/api/rooms/`                  | List rooms               |
| Rooms       | POST   | `/api/rooms/`                  | Add room                 |
| Rooms       | DELETE | `/api/rooms/<id>`              | Delete room              |
| Allocations | GET    | `/api/rooms/allocations`       | View allocations         |
| Allocations | POST   | `/api/rooms/allocations`       | Assign student to room   |
| Allocations | DELETE | `/api/rooms/allocations/<id>`  | Remove allocation        |
| Visitors    | GET    | `/api/visitors/`               | List visitors            |
| Visitors    | POST   | `/api/visitors/`               | Add visitor              |
| Visitors    | DELETE | `/api/visitors/<id>`           | Delete visitor           |
| Furniture   | GET    | `/api/furniture/`              | List furniture           |
| Furniture   | POST   | `/api/furniture/`              | Add furniture            |
| Furniture   | DELETE | `/api/furniture/<id>`          | Delete furniture         |

All routes except `/api/auth/login` and `/api/auth/register` require:
```
Authorization: Bearer <token>
```

---

## 🔐 Authentication Flow

1. Login via `/api/auth/login` → receive JWT token
2. Token stored in `localStorage`
3. All API calls include `Authorization: Bearer <token>` header
4. Token expires after **8 hours**

---

## 🎨 Features

- ✅ Dark modern UI with sidebar navigation
- ✅ Dashboard stats (students, rooms, hostels, visitors)
- ✅ Full Student CRUD with search + department filter
- ✅ Hostel cards with room/student counts
- ✅ Room management with capacity tracking
- ✅ Room allocation (prevents duplicates & over-capacity)
- ✅ Visitor log with active/left status badges
- ✅ Furniture assignment per room
- ✅ JWT-based authentication
- ✅ bcrypt password hashing
