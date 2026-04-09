# we choose flask for the backend, its a web framework that runs the server and handles requests for us between the frontend and backend
#jsonify needed to conver t python lists to json objects which we need in order to send data to the frontend
#send_from_directory helps serve the static frontned files like index.html, api.js, app.js, and style.css
from flask import Flask, jsonify, send_from_directory, request
#mysql.connector is the library that we use that allows us to connect to the database
import mysql.connector
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

#we import the 5 dashboard basic stats queries and the 10 queries we made from the queries.py file, they are used to display all queries on the dashboard page.
from queries import DASHBOARD_SQL, QUERIES_SQL

# variables that stores the path to the frontend directory, it is used to serve the static frontend files to the browser.
_REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = str(_REPO_ROOT / 'frontend')

#we are using flask to run the server and handle requests for us between the frontend and backend
# This is used to serve the static frontend files to the browser.
app = Flask(__name__, static_folder=FRONTEND_DIR)
# if sort_keys=True then jsonify would reorder all our columns alphabetically, we dont want this so we set it to False.
app.json.sort_keys = False

# dictionary that stores the database connection information.
DB_Connection = {
    'host': 'localhost', #running on our local machine
    'user': 'root', #my sql username
    'password': '', #my sql password -this is usually empty just press enter if ur asked
    'database': 'library_system' #our database name we connect to
}

#this is needed to open a connection to the database
#if the connection fails it returns None and lets us know there is a DB error. 
#it takes our DB_Connection info and connects with mysql.connector.connect()
def get_db():
    try:
        return mysql.connector.connect(**DB_Connection)
    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")
        return None

#sql is the sql query we want to execute. params is used when we add search and filters to the query later.
def query_db(sql, params=None):
    #we open the connection to the database by calling get_db()
    connection = get_db()
    if not connection: #if theres no connection we return an empty list
        return []
    try:
        #we create a cursor object and the cursor allows us to execute the sql query
        #dictionary=True means we want the results to be returned as a dictionary 
        # without this it means we get our data listed like: (1, 'The Great Gatsby', 'F. Scott Fitzgerald', 1925, 'Scribner', 'Classic') instead of including the column names, which we need to display the data in a table format.
        cursor = connection.cursor(dictionary=True)
        #we execute the sql query with the cursor.execute() method
        cursor.execute(sql, params or ())
        #we fetch the results of the query so we can display the data in a tabel.
        col_names = [d[0] for d in (cursor.description or [])]
        rows = cursor.fetchall()
        #we close the cursor and the connection to the database because we are done and dont need the connection to stay open
        cursor.close()
        connection.close()
        
        # rebuild each row in the SELECT column order so the frontend table matches the query/view.
        #we loop through the rows, columns, and data. then  convert the date objects to isoformat so we can display the data in a table format. isoformat is a way to format dates and times. without it we get the date as a string, when we need it to be a date object.
        out = []
        for row in rows:
            new_row = {}
            for column in col_names:
                data = row[column]
                if isinstance(data, (date, datetime)):
                    new_row[column] = data.isoformat()
                elif isinstance(data, Decimal):
                    new_row[column] = float(data)
                else:
                    new_row[column] = data
            out.append(new_row)
        return out
    except mysql.connector.Error as e:
        print(f"Database Query error: {e}")
        if connection:
            connection.close()
        return []

# this is used for CRUD, it lets the user add new, update, and delete data directly on the app.
def execute_db(sql, params=None):
    connection = get_db()
    if not connection:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute(sql, params or ())
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except mysql.connector.Error as e:
        print(f"Database Execute error: {e}")
        if connection:
            connection.close()
        return False


# check if the view exists in the database first
# views are used to store the data in a table format so we can display it
def _has_view(name):
    rows = query_db(
        "SELECT 1 FROM information_schema.views WHERE table_schema = DATABASE() AND table_name = %s",
        (name,),
    )
    return bool(rows)

# the route for the index page, it sends the index.html file to the browser
@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

# route for the static files, it sends the static files to the browser, the static files are the css, and js files.
@app.route('/<path:path>')
def static_file(path):
    if path.startswith('api'):
        return jsonify({'error': 'Not found'}), 404
    return send_from_directory(FRONTEND_DIR, path)

#this routes to the books table page, it sends the books data from the db to the browser to display all he books in a table.
@app.route('/api/books')
def api_books():
    # book search for a book by title, author, or isbn.
    search = request.args.get('search', '')
    sql = """
        SELECT book_id, isbn, title, author, publisher, publication_year, category,
               total_copies, available_copies,
               CASE WHEN available_copies = 0 THEN 'Unavailable'
                    WHEN available_copies <= 2 THEN 'Low Stock' ELSE 'Available' END AS status
        FROM Books
        WHERE 1=1
    """
    params = []
    if search:
        like = f"%{search}%"
        sql += " AND (title LIKE %s OR author LIKE %s OR isbn LIKE %s)"
        params.extend([like, like, like])
    sql += " ORDER BY title"
    rows = query_db(sql, tuple(params) if params else None)
    return jsonify(rows or [])

#this route gets all the distinct categories from the books table, it is used to display the categories in a dropdown filter on the frontend. It takes the data from the database and sends it to the frontend to display in a dropdown format.
@app.route('/api/books/categories')
def api_books_categories():
    rows = query_db("SELECT DISTINCT category FROM Books WHERE category IS NOT NULL ORDER BY category")
    return jsonify([r['category'] for r in (rows or [])])

#this route lets the user add a new book to the books table, it takes the data from the frontend and inserts it into the database.
@app.route('/api/books', methods=['POST'])
def api_books_post():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400
    ok = execute_db(
        """INSERT INTO Books (isbn, title, author, publisher, publication_year, category, total_copies, available_copies)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        (
            data.get('isbn'),
            data.get('title'),
            data.get('author'),
            data.get('publisher') or None,
            data.get('publication_year') or None,
            data.get('category') or None,
            int(data.get('total_copies', 1)),
            int(data.get('available_copies', 1)),
        ),
    )
    if not ok:
        return jsonify({'error': 'Insert failed'}), 500
    return jsonify({'ok': True}), 201

#this route updates an existing book in the books table, it takes the data from the frontend and updates the database.
@app.route('/api/books/<int:book_id>', methods=['PUT'])
def api_books_put(book_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400
    ok = execute_db(
        """UPDATE Books
           SET title=%s, author=%s, publisher=%s, publication_year=%s, category=%s, total_copies=%s, available_copies=%s
           WHERE book_id=%s""",
        (
            data.get('title'),
            data.get('author'),
            data.get('publisher') or None,
            data.get('publication_year') or None,
            data.get('category') or None,
            int(data.get('total_copies', 1)),
            int(data.get('available_copies', 0)),
            book_id,
        ),
    )
    if not ok:
        return jsonify({'error': 'Update failed'}), 500
    return jsonify({'ok': True})

#this route deletes a book from the books table using book_id, it takes the book_id as a parameter and deletes the corresponding row from the database.
@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def api_books_delete(book_id):
    ok = execute_db("DELETE FROM Books WHERE book_id = %s", (book_id,))
    if not ok:
        return jsonify({'error': 'Delete failed'}), 400
    return jsonify({'ok': True})

#this routes to the members table page, it sends the members data from the db to the browser to display all the members in a table.
@app.route('/api/members')
def api_members():
    search = request.args.get('search', '')
    sql = """
        SELECT member_id, first_name, last_name, CONCAT(first_name,' ',last_name) as name,
               email, phone, membership_type, registration_date, status, max_books_allowed
        FROM Members
        WHERE 1=1
    """
    params = []
    if search:
        like = f"%{search}%"
        sql += " AND (first_name LIKE %s OR last_name LIKE %s OR email LIKE %s)"
        params.extend([like, like, like])
    sql += " ORDER BY first_name, last_name"
    rows = query_db(sql, tuple(params) if params else None)
    return jsonify(rows or [])

#this route lets the user add a new member to the members table, it takes the data from the frontend and inserts it into the database. 
@app.route('/api/members', methods=['POST'])
def api_members_post():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400
    ok = execute_db(
        """INSERT INTO Members (first_name, last_name, email, phone, membership_type, max_books_allowed)
           VALUES (%s,%s,%s,%s,%s,%s)""",
        (
            data.get('first_name'),
            data.get('last_name'),
            data.get('email'),
            data.get('phone') or None,
            data.get('membership_type', 'Student'),
            int(data.get('max_books_allowed', 5)),
        ),
    )
    if not ok:
        return jsonify({'error': 'Insert failed'}), 500
    return jsonify({'ok': True}), 201

#this route updates an existing member in the members table, it takes the data from the frontend and updates the database.
@app.route('/api/members/<int:member_id>', methods=['PUT'])
def api_members_put(member_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400
    ok = execute_db(
        """UPDATE Members
           SET first_name=%s, last_name=%s, email=%s, phone=%s, membership_type=%s, max_books_allowed=%s
           WHERE member_id=%s""",
        (
            data.get('first_name'),
            data.get('last_name'),
            data.get('email'),
            data.get('phone') or None,
            data.get('membership_type'),
            int(data.get('max_books_allowed', 5)),
            member_id,
        ),
    )
    if not ok:
        return jsonify({'error': 'Update failed'}), 500
    return jsonify({'ok': True})

#this routes to the rentals table page, it sends the rentals data from the db to the browser to display all the rentals in a table.
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

#this route handles checking out a book, it takes the data from the frontend and inserts it into the Rentals table in the database. 
@app.route('/api/rentals/checkout', methods=['POST'])
def api_checkout():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400
    book_id = data.get('book_id')
    ok = execute_db(
        """INSERT INTO Rentals (book_id, member_id, rental_date, due_date, status)
           VALUES (%s,%s,%s,%s,'active')""",
        (book_id, data.get('member_id'), data.get('rental_date'), data.get('due_date')),
    )
    if not ok:
        return jsonify({'error': 'Checkout failed'}), 500
    execute_db(
        "UPDATE Books SET available_copies = available_copies - 1 WHERE book_id = %s AND available_copies > 0",
        (book_id,),
    )
    return jsonify({'ok': True}), 201

#this routes to the returns table page, it sends the returns data from the db to the browser to display all the returns in a table.
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

#this route gets all active rentals that have not been returned yet, it is used to display the active rentals. It takes the data from the database and sends it to the frontend to display in a table format. 
@app.route('/api/returns/active-rentals')
def api_returns_active_rentals():
    rows = query_db("""
        SELECT r.rental_id, b.title, CONCAT(m.first_name,' ',m.last_name) as member_name, r.due_date
        FROM Rentals r
        JOIN Books b ON r.book_id = b.book_id
        JOIN Members m ON r.member_id = m.member_id
        WHERE r.status IN ('active','overdue')
          AND NOT EXISTS (SELECT 1 FROM Returns ret WHERE ret.rental_id = r.rental_id)
        ORDER BY r.due_date
    """)
    return jsonify(rows or [])

#this route handles returning a book, it inserts a new row into Returns, updates the rental status, and increases the available copies of the book.
@app.route('/api/returns', methods=['POST'])
def api_returns_post():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400
    rental_id = data.get('rental_id')
    member_row = query_db("SELECT member_id, book_id FROM Rentals WHERE rental_id = %s", (rental_id,))
    if not member_row:
        return jsonify({'error': 'Rental not found'}), 404
    processed_by = member_row[0]['member_id']
    ok = execute_db(
        "INSERT INTO Returns (rental_id, return_date, condition_status, processed_by) VALUES (%s,%s,%s,%s)",
        (rental_id, data.get('return_date'), data.get('condition_status', 'Good'), processed_by),
    )
    if not ok:
        return jsonify({'error': 'Return failed'}), 500
    execute_db("UPDATE Rentals SET status = 'returned' WHERE rental_id = %s", (rental_id,))
    execute_db("UPDATE Books SET available_copies = available_copies + 1 WHERE book_id = %s", (member_row[0]['book_id'],))
    return jsonify({'ok': True}), 201

#this routes to the fines table page, it sends the fines data from the db to the browser to display all the fines in a table.
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

#these are the 5 stats at the top of the homepage, they show the total books in the library, the total members, the total overdue books, and the total active rentals. The outstanding fines is the total amount of fines that are not paid.
@app.route('/api/stats')
def api_stats():
    stats = {}
    r = query_db(DASHBOARD_SQL[1])
    if r:
        stats['total_books'] = r[0]['total'] or 0
        stats['total_copies'] = r[0]['copies'] or 0
    r = query_db(DASHBOARD_SQL[2])
    stats['active_members'] = r[0]['total'] if r else 0
    r = query_db(DASHBOARD_SQL[3])
    stats['overdue_count'] = r[0]['total'] if r else 0
    r = query_db(DASHBOARD_SQL[4])
    stats['active_rentals'] = r[0]['total'] if r else 0
    r = query_db(DASHBOARD_SQL[5])
    stats['outstanding_fines'] = float(r[0]['outstanding']) if r and r[0]['outstanding'] is not None else 0.0
    return jsonify(stats)

#these are the 3 main reports that are displayed on the homepage, they show the overdue books, the popular books, and the availability of books. they use views if they exist, otherwise they run the raw sql query from queries.py
@app.route('/api/reports/overdue')
def api_report_overdue():
    if _has_view('overdue_books_view'):
        rows = query_db("SELECT * FROM overdue_books_view ORDER BY days_overdue DESC")
    else:
        rows = query_db(QUERIES_SQL[1])
    return jsonify(rows or [])

#this route gets the 20 most popular books based on the number of times they have been borrowed, it is used to display the popular books. It takes the data from the database and sends it to the frontend to display in a table format.
@app.route('/api/reports/popular')
def api_report_popular():
    if _has_view('popular_books_view'):
        rows = query_db("SELECT * FROM popular_books_view ORDER BY times_borrowed DESC LIMIT 20")
    else:
        rows = query_db(QUERIES_SQL[3])
    return jsonify(rows or [])
#this route gets the availability of all books, it is used to display the availability of books. It takes the data from the database and sends it to the frontend to display in a table format.
@app.route('/api/reports/availability')
def api_report_availability():
    if _has_view('book_availability_view'):
        rows = query_db("SELECT * FROM book_availability_view ORDER BY title")
    else:
        rows = query_db(QUERIES_SQL[2])
    return jsonify(rows or [])

#this route is used to run any of the 10 queries we made for the dashboard, it takes the dash_id as a parameter and runs the corresponding sql query from queries.py. It then sends the data to the frontend to display in a table format.
@app.route('/api/reports/dash/<int:dash_id>')
def api_reports_dash(dash_id):
    sql = DASHBOARD_SQL.get(dash_id)
    if sql is None:
        return jsonify({'error': 'Unknown dashboard query'}), 404
    rows = query_db(sql)
    return jsonify(rows or [])

#this route is used to run any of the 10 queries we made for the reports page, it takes the report_id as a parameter and runs the corresponding sql query from queries.py. It then sends the data to the frontend to display in a table format.
@app.route('/api/reports/<int:report_id>')
def api_report(report_id):
    sql = QUERIES_SQL.get(report_id)
    if sql is None:
        return jsonify({'error': 'Unknown report'}), 404
    rows = query_db(sql)
    return jsonify(rows or [])

# this is the main function that runs the app
if __name__ == '__main__':
    print("http://localhost:5002")
    app.run(debug=True, host='0.0.0.0', port=5002)
