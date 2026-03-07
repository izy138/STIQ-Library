from flask import Flask, jsonify, send_from_directory, request
import mysql.connector
from datetime import date, datetime

app = Flask(__name__, static_folder='.')

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'library_system'
}

def get_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        print(f"DB error: {e}")
        return None


def query_db(sql, params=None):
    conn = get_db()
    if not conn:
        return []
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        rows = cur.fetchall()
        cur.close()
        conn.close()
        for row in rows:
            for k, v in row.items():
                if isinstance(v, (date, datetime)):
                    row[k] = v.isoformat()
        return rows
    except mysql.connector.Error as e:
        print(f"Query error: {e}")
        if conn:
            conn.close()
        return []


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def static_file(path):
    if path.startswith('api'):
        return jsonify({'error': 'Not found'}), 404
    return send_from_directory('.', path)


@app.route('/api/books')
def api_books():
    rows = query_db("""
        SELECT book_id, isbn, title, author, publisher, publication_year, category,
               total_copies, available_copies,
               CASE WHEN available_copies = 0 THEN 'Unavailable'
                    WHEN available_copies <= 2 THEN 'Low Stock' ELSE 'Available' END AS status
        FROM Books ORDER BY title
    """)
    return jsonify(rows or [])


@app.route('/api/members')
def api_members():
    rows = query_db("""
        SELECT member_id, first_name, last_name, CONCAT(first_name,' ',last_name) as name,
               email, phone, membership_type, registration_date, status, max_books_allowed
        FROM Members ORDER BY member_id
    """)
    return jsonify(rows or [])


@app.route('/api/rentals')
def api_rentals():
    rows = query_db("""
        SELECT r.rental_id, b.title, b.author, CONCAT(m.first_name,' ',m.last_name) as member_name, m.email,
               r.rental_date, r.due_date, r.status,
               CASE
                 WHEN r.status = 'returned' AND ret.return_date IS NOT NULL
                   THEN GREATEST(0, DATEDIFF(ret.return_date, r.due_date))
                 ELSE GREATEST(0, DATEDIFF(CURDATE(), r.due_date))
               END as days_overdue
        FROM Rentals r
        JOIN Books b ON r.book_id = b.book_id
        JOIN Members m ON r.member_id = m.member_id
        LEFT JOIN Returns ret ON r.rental_id = ret.rental_id
        ORDER BY r.rental_date DESC
    """)
    return jsonify(rows or [])


@app.route('/api/returns')
def api_returns():
    rows = query_db("""
        SELECT ret.return_id, ret.rental_id, b.title, CONCAT(m.first_name,' ',m.last_name) as member_name,
               r.rental_date, r.due_date, ret.return_date, ret.condition_status as condition_on_return,
               GREATEST(0, DATEDIFF(ret.return_date, r.due_date)) as days_overdue
        FROM Returns ret
        JOIN Rentals r ON ret.rental_id = r.rental_id
        JOIN Books b ON r.book_id = b.book_id
        JOIN Members m ON r.member_id = m.member_id
        ORDER BY ret.return_date DESC
    """)
    return jsonify(rows or [])


@app.route('/api/fines')
def api_fines():
    rows = query_db("""
        SELECT f.fine_id, f.rental_id, CONCAT(m.first_name,' ',m.last_name) as member_name,
               b.title as book_title, f.fine_amount, f.paid_amount, (f.fine_amount - f.paid_amount) as outstanding,
               f.fine_reason, f.fine_date, f.paid_status
        FROM Fines f
        JOIN Members m ON f.member_id = m.member_id
        JOIN Rentals r ON f.rental_id = r.rental_id
        JOIN Books b ON r.book_id = b.book_id
        ORDER BY f.fine_date DESC
    """)
    return jsonify(rows or [])


if __name__ == '__main__':
    print("http://localhost:5002")
    app.run(debug=True, host='0.0.0.0', port=5002)
