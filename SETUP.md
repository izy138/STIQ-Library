# Library Management System – Setup Guide

This guide walks you through setting up the database and running the frontend so you can view Books, Members, Rentals, Returns, and Fines.

---

## Prerequisites

- **MySQL 8.0+** – database server
- **Python 3.8+** – for the frontend
- **Git** – to clone the repo (if applicable)

---

## 1. Clone / Open the Project

```bash
cd /path/to/STIQ-Library
```

*(Or wherever the project is located.)*

---

## 2. Set Up the Database

### 2a. Start MySQL

Make sure MySQL is running. On macOS with Homebrew:

```bash
brew services start mysql
```

On Windows, start MySQL from Services or XAMPP. On Linux, use your package manager.

### 2b. Create the Database (if needed)

```bash
mysql -u root -e "CREATE DATABASE IF NOT EXISTS library_system;"
```

*(Add `-p` and enter your password if MySQL requires one.)*

### 2c. Load Schema and Data

From the **project root**:

```bash
# Load schema (creates tables)
mysql -u root library_system < db_proof/schema.sql

# Load sample data (books, members, rentals, returns, fines)
mysql -u root library_system < db_proof/data.sql
```

**If MySQL asks for a password:**

```bash
mysql -u root -p library_system < db_proof/schema.sql
mysql -u root -p library_system < db_proof/data.sql
```

### 2d. Load Triggers and Views (optional)

```bash
mysql -u root library_system < triggers.sql
mysql -u root library_system < views.sql
```

### 2e. One-Command Reload (optional)

To reset and reload everything:

```bash
./reload_db.sh
```

*(Add `-p` inside the script if MySQL needs a password.)*

### 2f. Verify the Data

```bash
mysql -u root library_system -e "SELECT COUNT(*) FROM Books; SELECT COUNT(*) FROM Members;"
```

You should see 9 books and 7 members (or similar counts).

---

## 3. Set Up the Frontend

### 3a. Create a Virtual Environment

```bash
cd simple-ui
python3 -m venv venv
```

### 3b. Activate the Virtual Environment

**macOS / Linux:**

```bash
source venv/bin/activate
```

**Windows (Command Prompt):**

```cmd
venv\Scripts\activate
```

**Windows (PowerShell):**

```powershell
venv\Scripts\Activate.ps1
```

### 3c. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs `flask` and `mysql-connector-python`.

### 3d. Configure the Database Password (if needed)

If your MySQL user has a password, edit `app.py` and set it:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password_here',  # <-- set this
    'database': 'library_system'
}
```

Leave `password` as `''` if you use no password.

---

## 4. Run the Frontend

From the `simple-ui` folder (with venv activated):

```bash
python app.py
```

You should see:

```
http://localhost:5002
 * Serving Flask app 'app'
 * Debug mode: on
```

Open a browser and go to: **http://localhost:5002**

---

## 5. What You’ll See

The frontend shows:

- **Books** – catalog with status (Available, Low Stock, Unavailable)
- **Members** – directory with type and status
- **Rentals** – all rentals with days overdue
- **Returns** – return history
- **Fines** – fine records and payment status

Use the navigation links to switch between sections.

---

## Troubleshooting

### "Database connection error"

- Confirm MySQL is running: `mysql -u root -e "SELECT 1;"`
- Check `DB_CONFIG` in `app.py` (host, user, password, database)
- Ensure `library_system` exists and has data

### "Port 5002 already in use"

- Stop any other app using port 5002, or
- Change the port in `app.py`: `app.run(..., port=5003)`

### "No data showing"

- Reload the database: `./reload_db.sh` (from project root)
- Restart the Flask app

### MySQL "Access denied"

- Use `-p` when running `mysql` and enter your password
- Update `DB_CONFIG['password']` in `app.py`

---

## Project Structure (relevant parts)

```
STIQ-Library/
├── db_proof/
│   ├── schema.sql      # Table definitions
│   └── data.sql        # Sample data
├── triggers.sql        # Database triggers (optional)
├── views.sql           # Database views (optional)
├── reload_db.sh        # Script to reload schema + data
├── simple-ui/          # Frontend (use this one)
│   ├── app.py          # Flask backend
│   ├── index.html
│   ├── css/style.css
│   ├── js/api.js
│   ├── js/app.js
│   └── requirements.txt
└── SETUP.md            # This file
```

---

## Quick Reference

| Step | Command |
|------|---------|
| Load database | `./reload_db.sh` (from project root) |
| Start frontend | `cd simple-ui && source venv/bin/activate && python app.py` |
| Open app | http://localhost:5002 |
