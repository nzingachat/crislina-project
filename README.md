# 🚗 Vehicle Fleet Management & Analytics System

A web-based fleet management solution built with Flask and modern frontend technologies. It includes vehicle and driver management, trip tracking, maintenance scheduling, and an analytics dashboard.

## 🚀 Features

### Core Modules
- **Vehicle Management** – Add, update, delete, and monitor vehicle status
- **Driver Management** – Track driver info and assign to vehicles
- **Trip Management** – Record trips, distance, fuel usage, and destinations
- **Maintenance Tracking** – Schedule and log maintenance costs and events

### Analytics Dashboard
- 📈 Fuel consumption trends
- 📊 Trips per vehicle/driver
- 📉 Maintenance cost over time
- 🔥 Vehicle utilization rate

### Security & Access Control
- 🔐 JWT authentication
- 👤 Role-based access: Admin, Manager, Driver
- ✅ Secure API endpoints

## 🛠️ Tech Stack

**Backend**: Python, Flask, Flask-RESTful, SQLAlchemy, SQLite/PostgreSQL  
**Frontend**: HTML, CSS (Bootstrap), JS  
**Analytics**: Chart.js / Plotly  
**Auth**: JWT (via PyJWT)  
**Extras**: Flask-CORS, python-dotenv

## ⚙️ Installation

```bash
# 1. Clone the repo
git clone https://github.com/your-username/vehicle-fleet-management.git
cd vehicle-fleet-management

# 2. Create & activate virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize the database
python src/init_db.py
```

## 👥 User Roles

- **Admin**: Full access to vehicles, drivers, trips, maintenance
- **Manager**: Assign trips, view analytics
- **Driver**: View assigned trips only

## 🧩 Database Schema

- `users`: id, username, password (hashed), role  
- `vehicles`: id, reg_no, model, fuel_type, status  
- `drivers`: id, name, license_no  
- `trips`: id, vehicle_id, driver_id, source, destination, distance, fuel_used, date  
- `maintenance` _(optional)_: id, vehicle_id, date, cost, description  

## 🚧 Known Issues / Missing Features

### 🛠 Maintenance Module (Incomplete)
- `showAddMaintenanceModal()`, `editMaintenance()`, and `deleteMaintenance()` only display toast messages.
- ✅ **Missing**:
  - Full modal forms for Create, Edit, and Delete
  - API integration for CRUD operations
  - UI table updates after changes

### 📊 Reports / Analytics (Not Implemented)
- Charts and analytics for:
  - Vehicle statistics (usage, fuel, trip count)
  - Maintenance cost trends and frequency
- ✅ **Missing**:
  - API endpoints for analytics
  - Chart.js/Plotly integrations on dashboard

### 👤 Users / Admin Panel (Missing)
- No user management module for Admins
- ✅ **Missing**:
  - CRUD for users (add/edit/delete)
  - Role assignment (Admin, Manager, Driver)
  - Admin settings panel

### 🔔 Notification System (Basic Only)
- Only `showToast()` is used
- ✅ **Missing**:
  - Standardized notification system
  - Success, error, warning types across modules
  - Better UI/UX consistency for alerts

### 📈 Dashboard Statistics (JS Not Implemented)
- CSS-ready stat cards (e.g. Total Vehicles, Active Trips)
- ✅ **Missing**:
  - JS logic to fetch real-time stats
  - API endpoints for dashboard data
  - Dynamic card updates

### ❌ Error Handling (Incomplete)
- Maintenance module lacks error handling on failed API calls
- ✅ **Missing**:
  - Try-catch or `.catch()` for fetch/axios calls
  - User-friendly error messages
  - Fallback UIs or retry prompts

---

✅ Add these to your issue tracker or project board to prioritize the next development milestones.


## 🤝 Contributing

Pull requests are welcome! Please follow the code style and write clean, modular code.

## 📄 License

MIT License — free for personal and commercial use.

