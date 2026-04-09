-- Dashboard Query 6: 10 most recent rentals 
SELECT
    r.rental_id,
    b.title,
    CONCAT(m.first_name, ' ', m.last_name) AS member_name,
    r.rental_date,
    r.due_date,
    r.status
FROM Rentals r
JOIN Books b ON r.book_id = b.book_id
JOIN Members m ON r.member_id = m.member_id
ORDER BY r.rental_date DESC
LIMIT 10;

-- Dashboard Query 7: show sthe latest 10 overdue rentals.
SELECT
    r.rental_id,
    b.title,
    CONCAT(m.first_name, ' ', m.last_name) AS member_name,
    r.due_date,
    DATEDIFF(CURDATE(), r.due_date) AS days_overdue
FROM Rentals r
JOIN Books b ON r.book_id = b.book_id
JOIN Members m ON r.member_id = m.member_id
WHERE r.status IN ('active', 'overdue')
  AND r.due_date < CURDATE()
ORDER BY r.due_date ASC
LIMIT 10;


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

### 2d. Load Views and Triggers (optional)

After sample data is loaded, apply views then triggers (triggers fire on new inserts, so load them **after** `data.sql`):

```bash
mysql -u root library_system < backend/views.sql
mysql -u root library_system < backend/triggers.sql
```

Proof they work:

```bash
python3 backend/verify_triggers_views.py
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
- Change the port in `backend/app.py`: `app.run(..., port=5003)`

### "No data showing"

- Reload the database: `./reload_db.sh` (from project root)
- Restart the Flask app

### MySQL "Access denied"

- Use `-p` when running `mysql` and enter your password
- Update `DB_Connection['password']` in `backend/app.py`

---

## Project Structure (relevant parts)

```
STIQ-Library/
├── db_proof/
│   ├── schema.sql      # Table definitions
│   └── data.sql        # Sample data
├── backend/
│   ├── app.py          # Flask API (canonical)
│   ├── triggers.sql    # Load after data.sql
│   ├── views.sql
│   └── verify_triggers_views.py
├── reload_db.sh        # Reload schema, data, views, triggers
├── frontend/           # Static UI for backend/app.py
│   ├── index.html
│   ├── css/style.css
│   └── js/
├── simple-ui/          # Alternate small UI
└── SETUP.md            # This file
```

---

## Quick Reference

| Step | Command |
|------|---------|
| Load database | `./reload_db.sh` (from project root) |
| Start frontend | `cd simple-ui && source venv/bin/activate && python app.py` |
| Open app | http://localhost:5002 |


# Library Management System - Database Project

## Project Overview

This project implements a complete relational database system for a university department library. The system manages books, members, rentals, returns, and fines with automated business logic and comprehensive reporting capabilities.

## Team Information

- **Team Members:** [Your Names Here]
- **Project Type:** Database-focused capstone project
- **DBMS:** MySQL 8.0+
- **Database Name:** library_system

## Database Schema

### Tables (5)

1. **Books** - Stores book inventory information
   - Primary Key: `book_id`
   - Unique Constraint: `isbn`
   - Tracks total and available copies

2. **Members** - Stores library member information
   - Primary Key: `member_id`
   - Unique Constraint: `email`
   - Supports different membership types (student, faculty, staff)

3. **Rentals** - Tracks book borrowing transactions
   - Primary Key: `rental_id`
   - Foreign Keys: `book_id`, `member_id`
   - Tracks rental status (active, returned, overdue)

4. **Returns** - Records book return details
   - Primary Key: `return_id`
   - Foreign Key: `rental_id` (UNIQUE - enforces 1:1 relationship)
   - Tracks condition and overdue days

5. **Fines** - Manages member fines
   - Primary Key: `fine_id`
   - Foreign Keys: `rental_id`, `member_id`
   - Tracks fine amounts, reasons, and payment status

### Entity Relationships

- **Books ↔ Rentals**: 1:M (One book can have many rentals)
- **Members ↔ Rentals**: 1:M (One member can have many rentals)
- **Rentals ↔ Returns**: 1:1 (Each rental has at most one return)
- **Rentals ↔ Fines**: 1:M (One rental can generate multiple fines)
- **Members ↔ Fines**: 1:M (One member can have many fines)

## Advanced Features

### 1. Triggers (4)

- **auto_calculate_fine_on_return**: Automatically calculates and creates overdue fines when books are returned late ($1/day)
- **auto_create_damage_fine**: Creates additional fines for damaged ($25) or lost books ($50)
- **update_available_copies_on_rental**: Automatically decrements available copies when book is rented
- **prevent_rental_if_suspended**: Prevents suspended members from renting books

### 2. Views (3)

- **overdue_books_view**: Past-due active or overdue rentals (used by Query 1)
- **book_availability_view**: Catalog availability and next due date (used by Query 2)
- **popular_books_view**: Rental counts per book (used by Query 5)

Unpaid/partial fines are reported via **R1** in `db_proof/queries.sql` (no view).

## Key Constraints

### Primary Keys
All tables have auto-incrementing integer primary keys

### Foreign Keys
- Rentals references Books and Members
- Returns references Rentals
- Fines references Rentals and Members
- All foreign keys use appropriate DELETE/UPDATE rules

### Check Constraints
- `chk_publication_year`: Publication year must be > 1800 and <= current year
- `chk_total_copies`: Total copies must be > 0
- `chk_available_copies`: Available copies must be >= 0 and <= total copies
- `chk_due_date`: Due date must be after rental date
- `chk_days_overdue`: Days overdue must be >= 0
- `chk_fine_amount`: Fine amount must be >= 0
- `chk_paid_amount`: Paid amount must be >= 0 and <= fine amount
- `chk_max_books`: Max books allowed must be > 0

### Unique Constraints
- `Books.isbn`: Each ISBN must be unique
- `Members.email`: Each email must be unique
- `Returns.rental_id`: Each rental can only have one return record

### NOT NULL Constraints
Applied to critical fields: title, author, isbn, email, rental dates, etc.

## SQL Queries (12)

The project includes 12 comprehensive queries covering:

1. Multi-table JOINs (10 queries)
2. Aggregate functions - COUNT, SUM, AVG (5 queries)
3. GROUP BY with HAVING (1 query)
4. Subqueries (2 queries)
5. Date functions (3 queries)
6. CASE statements (2 queries)
7. LEFT JOINs for optional relationships (3 queries)
8. ORDER BY and LIMIT (8 queries)

### Query Categories
- **Operational**: Overdue books, book availability, rental history
- **Financial**: Fine calculations, outstanding balances
- **Analytics**: Popular books, borrowing patterns, member statistics
- **Administrative**: Inactive members, damaged books, monthly activity

## Installation & Setup

### Prerequisites
- MySQL 8.0 or higher
- MySQL Workbench (recommended) or command-line client

### Step 1: Create Database
```sql
CREATE DATABASE library_system;
USE library_system;
```

### Step 2: Load Schema
```bash
mysql -u your_username -p library_system < db_proof/schema.sql
```

### Step 3: Load Sample Data
```bash
mysql -u your_username -p library_system < db_proof/data.sql
```

### Step 4: Create Views
```bash
mysql -u your_username -p library_system < backend/views.sql
```

### Step 5: Create Triggers (must be after sample data)
Triggers fire on `INSERT` into `Rentals` and `Returns`. Load them **after** `data.sql` so bulk inserts are not processed twice (which would duplicate fines and break `available_copies`).

```bash
mysql -u your_username -p library_system < backend/triggers.sql
```

### Step 6: Test Constraints
```bash
mysql -u your_username -p library_system < db_proof/constraints_test.sql
```
Note: These queries are expected to fail to demonstrate constraint enforcement.

### Step 7: Run Queries
```bash
mysql -u your_username -p library_system < db_proof/queries.sql
```

### Step 8: Verify triggers and views (optional proof)
```bash
mysql -u your_username -p library_system < backend/verify_triggers_views.sql
python3 backend/verify_triggers_views.py
```
The Python script uses transactions and `ROLLBACK` so seed data is unchanged. It checks that all six views and four triggers exist and that trigger behaviour matches the design (suspended block, copy decrement, overdue/damage/lost fines).

## Testing

### Constraint Testing
Run the SQL statements in `db_proof/constraints_test.sql` one by one. Each should produce an error message demonstrating the constraint is working.

Expected errors:
- Foreign key violations
- Check constraint violations
- Unique constraint violations
- NOT NULL violations

### Sample Data
The database includes realistic test data:
- 11 books across multiple categories
- 9 members (students, faculty, staff)
- 11 rental records (active, returned, overdue)
- 6 return records (various conditions)
- 6 fine records (paid, unpaid, partial)

### Edge Cases Included
- NULL values in optional fields
- Boundary values (minimum year = 1801, minimum books = 1)
- Zero values (days_overdue = 0, fine_amount = 0.00)
- Suspended member with unpaid fines
- Partial payment scenarios
- Damaged books with multiple fines

## Project Structure

```
library_system/
│
├── README.md                     # This file
│
├── backend/                      # Application server + DB objects (NO AI)
│   ├── app.py                   # Flask API + serves ../frontend static files
│   ├── report_queries.py        # Report SQL (mirrors db_proof/queries.sql)
│   ├── dashboard_queries.py     # Dashboard SQL (D1–D7)
│   ├── triggers.sql             # MySQL triggers (load after data.sql)
│   ├── views.sql                # MySQL views (3; Queries 1,2,5 use these)
│   ├── verify_triggers_views.sql # Manual checklist / counts
│   └── verify_triggers_views.py # Automated PASS/FAIL (uses ROLLBACK)
│
├── db_proof/                     # Database verification files
│   ├── schema.sql               # Complete table definitions
│   ├── data.sql                 # Sample data with edge cases
│   ├── constraints_test.sql     # Constraint violation tests
│   ├── queries.sql              # 12 comprehensive queries
│   └── query_outputs.txt        # Query results (to be filled)
│
└── frontend/                     # Static UI (HTML, CSS, JS); run server from backend/
```

## Business Rules Enforced

1. **Books cannot be rented if no copies available** (available_copies must be > 0)
2. **Members with 'suspended' status cannot rent books** (enforced by trigger)
3. **Rental due dates must be after rental dates** (check constraint)
4. **Each rental can only be returned once** (unique constraint on Returns.rental_id)
5. **Overdue fines are calculated automatically** ($1 per day, via trigger)
6. **Damage fines are $25, lost book fines are $50** (via trigger)
7. **Available copies are automatically maintained** (via triggers on rental/return)
8. **Payment amounts cannot exceed fine amounts** (check constraint)

## Design Decisions

### Why Separate Returns Table?
- Allows tracking return-specific information (condition, actual return date)
- Enforces 1:1 relationship with rentals
- Cleaner separation of concerns

### Why Multiple Fine Types?
- A single rental can incur both overdue AND damage fines
- Different fine reasons have different amounts
- Allows flexible payment tracking

### Why Triggers Instead of Application Logic?
- Ensures consistency regardless of application layer
- Centralizes business rules in database
- Automatic execution eliminates human error
- Better for multi-application environments

### Why These Specific Views?
- Encapsulate most common queries staff would need
- Simplify frontend development
- Provide consistent data access layer
- Can grant view access without table access (security)

## Future Enhancements

Potential additions for extended project:
- Stored procedures for complex operations (rental checkout, payment processing)
- Transaction-based rental/return workflows
- Role-based access control
- Book reservation system
- Email notification triggers
- Audit logging
- Enhanced reporting with analytics

## Notes

- All database design, schema, queries, triggers, and views were created **without AI assistance** (per project requirements)
- Frontend interface code may use AI assistance when implemented
- Sample data includes realistic edge cases and boundary conditions
- Constraint tests demonstrate proper database constraint enforcement
- Query outputs must be generated by running queries against the loaded database

## Database Normalization

The schema follows 3rd Normal Form (3NF):
- **1NF**: All columns contain atomic values
- **2NF**: No partial dependencies (all non-key attributes depend on entire primary key)
- **3NF**: No transitive dependencies (non-key attributes don't depend on other non-key attributes)

### Justification:
- Books table: All attributes depend solely on book_id
- Members table: All attributes depend solely on member_id
- Rentals table: Composite information properly normalized
- Returns table: Return-specific info separated from rental info
- Fines table: Fine info separated from rental info

## Contact & Support

For questions or issues:
- Check MySQL error logs for detailed error messages
- Verify all files loaded in correct order
- Ensure MySQL 8.0+ is being used (earlier versions may not support all constraints)
- Review constraint definitions if inserts fail

---

**Project Status**: Backend Complete | Frontend Pending
**Last Updated**: February 2026