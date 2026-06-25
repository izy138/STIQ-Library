# STIQ Library Management System

A full-stack library management web application for cataloging books, managing members, processing checkouts and returns, and tracking fines. Built around a normalized MySQL database with views, triggers, and analytical reporting queries, exposed through a Flask REST API and a lightweight single-page frontend.


---

## Features

- **Dashboard** — At-a-glance stats (total books, active members, open rentals, overdue count, outstanding fines) plus 10 built-in analytical reports
- **Books** — Browse, search, add, and update titles; track availability and discontinued status
- **Members** — Manage membership types, borrowing limits, and account status (active / suspended / expired)
- **Rentals & returns** — Check out books, process returns, and view rental history with overdue calculations
- **Fines** — View overdue and damage fines with paid / unpaid tracking
- **Database automation** — MySQL triggers handle fine calculation, inventory updates, and rental restrictions
- **UI** — Responsive layout with light/dark mode

---

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Frontend** | HTML, CSS, vanilla JavaScript (client-side SPA router) |
| **Backend** | Python 3.12, Flask |
| **Database** | MySQL 8.0 |
| **DevOps** | Docker, Docker Compose |

---

## Quick Start (Docker)

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

From the project root:

```bash
docker compose up --build
```

Open [http://localhost:5002](http://localhost:5002) in your browser.

The MySQL container loads schema, seed data, views, and triggers automatically on first run.

### Troubleshooting

**`Access denied` (MySQL error 1045)** — The database volume was created with a different root password. Reset local data and rebuild:

```bash
docker compose down -v
docker compose up --build
```

**Change ports or password** — Optional `.env` in the project root (gitignored):

```env
MYSQL_ROOT_PASSWORD=library
MYSQL_HOST_PORT=3306
WEB_HOST_PORT=5002
```

---

## Manual Setup (without Docker)

**Prerequisites:** Python 3.12+, MySQL 8.0, `mysql` CLI

1. **Install Python dependencies**

   ```bash
   pip3 install -r backend/requirements.txt
   ```

2. **Create and load the database** (from project root; you will be prompted for your MySQL root password)

   ```bash
   ./reload_db.sh
   ```

3. **Start the application**

   ```bash
   python3 backend/app.py
   ```

4. Open [http://localhost:5002]

For manual runs, ensure MySQL is reachable at `localhost:3306` with database `library_system` and credentials matching your local setup (defaults in `app.py` use `root` with an empty password unless overridden by environment variables).

---

## Project Structure

```
STIQ-Library/
├── backend/
│   ├── app.py           # Flask server and REST API routes
│   ├── queries.py       # Dashboard stats and 10 report queries
│   ├── views.sql        # SQL views (overdue, availability, popularity)
│   ├── triggers.sql     # Automated fines, inventory, rental rules
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── api.js       # API client
│       └── app.js       # SPA views and routing
├── db_proof/
│   ├── schema.sql       # Table definitions and constraints
│   ├── data.sql         # Seed data
│   ├── queries.sql      # Reference SQL for all 10 reports
│   └── constraints_test.sql
├── docker-compose.yml
├── Dockerfile
└── reload_db.sh         # Reload DB for local (non-Docker) development
```

---

## Database Design

Five normalized tables with referential integrity and check constraints:

| Table | Purpose |
|-------|---------|
| `Books` | Catalog, copy counts, active/discontinued status |
| `Members` | Patron profiles, membership type, borrowing limits |
| `Rentals` | Active and historical checkouts |
| `Returns` | One return per rental; condition on return |
| `Fines` | Overdue and damage charges linked to rentals |

**Views** (`backend/views.sql`): overdue books, book availability status, most popular titles.

**Triggers** (`backend/triggers.sql`):

1. Auto-calculate overdue fines on return
2. Create damage/loss fines based on return condition
3. Decrement/increment `available_copies` on checkout and return
4. Block rentals for suspended members

---

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/stats` | Dashboard summary metrics |
| `GET` | `/api/queries/:id` | Run analytical report 1–10 |
| `GET` | `/api/books?search=` | List/search books |
| `POST` | `/api/books` | Add a book |
| `PUT` | `/api/books/:id` | Update a book |
| `GET` | `/api/members?search=` | List/search members |
| `POST` | `/api/members` | Add a member |
| `PUT` | `/api/members/:id` | Update a member |
| `GET` | `/api/rentals` | List rentals |
| `POST` | `/api/rentals` | Check out a book |
| `GET` | `/api/returns` | List returns |
| `POST` | `/api/returns` | Process a return |
| `GET` | `/api/fines` | List fines |

---

## Analytical Reports

The dashboard exposes 10 SQL reports (defined in `backend/queries.py` and `db_proof/queries.sql`):

1. Overdue books  
2. Book availability  
3. Most popular books  
4. Never borrowed books  
5. Fines by member  
6. Rental and return history  
7. Recent rentals (7 days)  
8. Damaged or lost returns  
9. Monthly rental activity  
10. Unpaid / partial fines  

---

## License

Academic / portfolio project. Use and adapt as needed.
