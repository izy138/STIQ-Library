# we choose flask for the backend, its a web framework that runs the server and handles requests for us between the frontend and backend
#jsonify needed to conver t python lists to json objects which we need in order to send data to the frontend
#send_from_directory helps serve the static frontned files like index.html, api.js, app.js, and style.css
from flask import Flask, jsonify, send_from_directory, request
#mysql.connector is the library that we use that allows us to connect to the database
import mysql.connector
import os
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

#we import the 5 dashboard basic stats queries and the 10 queries we made from the queries.py file, they are used to display all queries on the dashboard page.
from queries import DASHBOARD_SQL, QUERIES_SQL

# variables that stores the path to the frontend directory, it is used to serve the static frontend files to the browser.
_REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = str(_REPO_ROOT / 'frontend')

#we are using flask to run the server and handle requests for us between the frontend and backend
# this is used to serve the static frontend files to the browser.
app = Flask(__name__, static_folder=FRONTEND_DIR)
#if sort_keys=True then jsonify would reorder all our columns alphabetically, we dont want this so we set it to False.
app.json.sort_keys = False

# dictionary that stores the database connection information.
# Override for docker compose.
DB_Connection = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'port': int(os.environ.get('MYSQL_PORT', '3306')),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', ''),
    'database': os.environ.get('MYSQL_DATABASE', 'library_system'),
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

#this is the sql query we want to execute. params is used when we add search and filters to the query later.
# query_db is used for every GET sql command, we use it to get data from our db, and then display it they way we want based on the query we write in this commad
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
        # we fetch the results of the query so we can display the data in a tabel.
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
                # new_row is a dictionary that stores the data for each column. we need it because the data is returned as a list of dictionaries by default
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
# execute_db is used for every single POST and PUT sql command, if we dont have this , then we cant add or update new data from the frontend. ! very important to understand how this works guys
def execute_db(sql, params=None):
    connection = get_db()
    if not connection:
        return False
    try:
        cursor = connection.cursor()
        # this executes the sql query with the cursor.execute() method it sends the parameters to the query
        cursor.execute(sql, params or ())
        # this commits the changes to the database
        connection.commit()
        # this closes the cursor and the connection to the database.
        cursor.close()
        connection.close()
        return True
    except mysql.connector.Error as e:
        print(f"Database Execute error: {e}")
        if connection:
            connection.close()
        return False

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

# BOOKS TABLE routes to the books page, it sends the books data from the db to the browser to display all he books in a table.
@app.route('/api/books')
def api_books():
    # book search for a book by title, author, or isbn.
    search = request.args.get('search', '')
    # we use VIEW #2 book_availability_view to get the availability status of the books. this view also shows all the info for the books in the books table, so we use it instead of just a regular select query.
    sql = """
        SELECT v.book_id, b.isbn, v.title, v.author, b.publisher, b.publication_year, v.category,
               b.book_status,
               v.total_copies, v.available_copies,
               v.availability_status AS status
        FROM book_availability_view v
        INNER JOIN Books b ON b.book_id = v.book_id
        WHERE 1=1
    """
    # this parameter is used for the search query. When the user tries to search for a book by title, author, or isbn, this parameter is used to filter the books.
    params = []
    if search:
        like = f"%{search}%"
        # this appends the search keyword to the books table query.
        sql += " AND (v.title LIKE %s OR v.author LIKE %s OR b.isbn LIKE %s)"
        params.extend([like, like, like])
    sql += " ORDER BY CASE b.book_status WHEN 'Active' THEN 0 ELSE 1 END, v.title"
    # executes query and returns the book data from the db
    rows = query_db(sql, tuple(params) if params else None)
    return jsonify(rows or [])

# ADD A NEW BOOK POST command, route lets the user add a new book to the books table, it takes the data from the frontend and inserts it into the database. 
# POST is used to insert a new item into our database 
# it uses data.get() for each field and adds it to our Insert query.
@app.route('/api/books', methods=['POST'])
def api_books_post():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400
    ok = execute_db(
        """INSERT INTO Books (isbn, title, author, publisher, publication_year, category, total_copies, available_copies)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        (
            # matches the users input to the database columns, if user doesnt enter a value for a column, it will be set to None to prevent errors.
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

# UPDATE EXISTINGBOOK PUT command, route updates an existing book in the books table, it takes the data from the frontend and updates the database.
#PUT is used to update an existing item in the db.
@app.route('/api/books/<int:book_id>', methods=['PUT'])
def api_books_put(book_id):
    data = request.get_json() # it gets the data through get_json() which is a method that converts the json data from the frontend to a python dictionary.
    if not data:
        return jsonify({'error': 'JSON body required'}), 400
    # then the data is passed to the execute_db() function to update the database using data.get() for each field to the update queery to edit a row in the db.
    # this checks if the book_status is valid, if not it returns an error.
    book_status = data.get('book_status', 'Active')
    if book_status not in ('Active', 'Discontinued'):
        return jsonify({'error': 'Invalid book_status'}), 400
    ok = execute_db(
        # this is the update query that updates the database with the new data.
        """UPDATE Books
           SET title=%s, author=%s, publisher=%s, publication_year=%s, category=%s, total_copies=%s, available_copies=%s, book_status=%s
           WHERE book_id=%s""",
        (
            data.get('title'),
            data.get('author'),
            data.get('publisher') or None,
            data.get('publication_year') or None,
            data.get('category') or None,
            int(data.get('total_copies', 1)),
            int(data.get('available_copies', 0)),
            book_status, #we added book_status to the update query so the user can update the book_status themselves.
            book_id,
        ),
    )
    if not ok:
        return jsonify({'error': 'Update failed'}), 500
    return jsonify({'ok': True})

# !!!! not sure if we should keep this, it deletes a book from the table, but maybe we dont want to be deleting book records.
# i used this to delete my test book records for the POST and PUT functions. 
#instead of deleting the book records, we can just set the book_status to 'Discontinued' so it doesnt show up in the books table.
#this route deletes a book from the books table using book_id, it takes the book_id as a parameter and deletes the corresponding row from the database.
# @app.route('/api/books/<int:book_id>', methods=['DELETE'])
# def api_books_delete(book_id):
#     ok = execute_db("DELETE FROM Books WHERE book_id = %s", (book_id,))
#     if not ok:
#         return jsonify({'error': 'Delete failed'}), 400
#     return jsonify({'ok': True})

# MEMBERS TABLE all members, this displays every member in the db active or not
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
    # search feature for members where the user can search my email first name or last name using LIKE 
    params = []
    if search:
        like = f"%{search}%"
        sql += " AND (first_name LIKE %s OR last_name LIKE %s OR email LIKE %s)"
        params.extend([like, like, like])
    sql += " ORDER BY first_name, last_name"
    rows = query_db(sql, tuple(params) if params else None)
    return jsonify(rows or [])

#ADD A NEW MEMBER POST command, exact same way for books, this route lets the user add a new member to the members table, it takes the data from the frontend and inserts it into the database. POST is used to insert a new item into our database and it uses data.get() for each field and adds it to Insert query.
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

#UPDATE AMEMBER PUT command, same way for books, we can edit any info we need for existin members. it takes the data from the frontend and updatesour database.
@app.route('/api/members/<int:member_id>', methods=['PUT'])
def api_members_put(member_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400
    #the user can update a members status and max books allowed.
    status = data.get('status', 'active')
    # checks if the status is valid
    if status not in ('active', 'suspended', 'expired'):
        return jsonify({'error': 'Invalid status'}), 400
    #checks if the max books allowed is valid
    max_books = int(data.get('max_books_allowed', 5))
    # if the membersstatus is suspended, the max books allowed is set to 0.
    if status == 'suspended':
        max_books = 0
    elif max_books < 1:
        return jsonify({'error': 'max_books_allowed must be at least 1 unless status is suspended'}), 400
    # our update query that updates the database with the new data.
    ok = execute_db(
        # i added status to this so the user can update a member status in the modal too
        """UPDATE Members
           SET first_name=%s, last_name=%s, email=%s, phone=%s, membership_type=%s, max_books_allowed=%s, status=%s
           WHERE member_id=%s""",
        (
            data.get('first_name'),
            data.get('last_name'),
            data.get('email'),
            data.get('phone') or None,
            data.get('membership_type'),
            max_books,
            status, #we also added status here like in books to the update query so the user can update a members status 
            member_id,
        ),
    )
    if not ok:
        return jsonify({'error': 'Update failed'}), 500
    return jsonify({'ok': True})

# RENTALS select query routes to the rentals table page, it sends the rentals data from the db to the browser to display all the rentals in a table.
# it displays all rentals in the db. Its ordered by the rental date so recent ones at the top. maybe we can add a filter at somepoint 
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

# CHECKOUT BOOK POST command, this route handles checking out a book, it takes the data from the frontend and inserts it into the Rentals table in the database.
@app.route('/api/rentals', methods=['POST'])
def api_checkout():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400
    book_id = data.get('book_id')
   
    book_row = query_db(
        "SELECT book_status FROM Books WHERE book_id = %s",
        (book_id,),
    )
    # checks if the book is available for checkout, it checks the book_status column in the books table. if it is 'Discontinued' then it is not available for checkout. We set one book to discontinued to test that its book isbn = '9780064471046' Lion the Witch and the Wardrobe if you want to test it out you will see an error cmoe up
    if not book_row or book_row[0].get('book_status') != 'Active':
        return jsonify({'error': 'Book is not available for checkout'}), 400
    ok = execute_db(
        """INSERT INTO Rentals (book_id, member_id, rental_date, due_date, status)
           VALUES (%s,%s,%s,%s,'active')""",
        (book_id, data.get('member_id'), data.get('rental_date'), data.get('due_date')),
    )
    if not ok:
        return jsonify({'error': 'Checkout failed'}), 500
    return jsonify({'ok': True}), 201

#RETURNS TABLE select query for returns page, it sends the returns data from the db to the browser to display all the returns in a table.
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

# RETURN A RENTED BOOK POST command, this route handles returning a book, it inserts a new row into Returns, updates the  rental status
# trigger 3 is used everytime book is returned, mysql auto updates the available copies of the book when insert command is used here.
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
        # the trigger 3 is triggered by this command here. 
        "INSERT INTO Returns (rental_id, return_date, condition_status, processed_by) VALUES (%s,%s,%s,%s)",
        (rental_id, data.get('return_date'), data.get('condition_status', 'Good'), processed_by),
    )
    if not ok:
        return jsonify({'error': 'Return failed'}), 500
    return jsonify({'ok': True}), 201

#FINES TABLE this routes to the fines table page, basic select query 
# sends the fines data from the db to the browser to display all the fines in a table, ordered by the paid status first then fine date.
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
        ORDER BY f.paid_status ASC, f.fine_date DESC
    """)
    return jsonify(rows or [])
 
#THIS IS IMPORTANT, ITS WHERE THE QUERIES ARE RUN AND DISPLAYED FOR DASHBOARD!! make sure to read and understand how this works so we can explain properly, read all comments pls

#ALL 5 DSAHBOARD
# these are the 5 stats at the top of the homepage: total books, active members, open rentals count, overdue count, outstanding fines.
# idecided to put these in their own seperate route so if we want to add more stats we can just add them directly to the dictionary i made for sepcifically dashboard stats, its much easier to add new ones this way.
@app.route('/api/stats')
def api_stats():
    stats = {}
    # query 1 total books and copies shows the total num of books and the copies, so it uses an if statement to check and display the data correct
    query = query_db(DASHBOARD_SQL[1])
    if query: 
        stats['total_books'] = query[0]['total'] or 0
        stats['total_copies'] = query[0]['copies'] or 0
    # routes for the queries 2-5 shows totals for active members, overdue books, active rentals, and outstanding fines.
    query = query_db(DASHBOARD_SQL[2])
    stats['active_members'] = query[0]['total'] if query else 0
    query = query_db(DASHBOARD_SQL[3])
    stats['overdue_count'] = query[0]['total'] if query else 0
    query = query_db(DASHBOARD_SQL[4])
    stats['active_rentals'] = query[0]['total'] if query else 0
    query = query_db(DASHBOARD_SQL[5])
    stats['outstanding_fines'] = float(query[0]['outstanding']) if query and query[0]['outstanding'] is not None else 0.0
    return jsonify(stats)

# ALL 10 QUERIES 
# route is used to run all of the 10 queries we made for the dashboard, it takes the query_id as a parameter and runs the corresponding sql query from queries.py. It then sends the data to the frontend to display in a table format. so if we want to run query 1 we would go to localhost:5002/api/queries/1 it is displayed here in json format, and it would be displayed in the frotend at localhost:5002/#query-1
@app.route('/api/queries/<int:query_id>')
def api_query(query_id):
    sql = QUERIES_SQL.get(query_id) # this is where it happens, its gets the query_id from our dictionary in queries.py
    if sql is None:
        return jsonify({'error': 'Unknown query'}), 404
    rows = query_db(sql)
    return jsonify(rows or [])

# this is the main function that runs the app at port 5002
if __name__ == '__main__':
    print("http://localhost:5002")
    app.run(debug=True, host='0.0.0.0', port=5002)
