# All SQL used by backend/app.py in one place.

# Dashboard basic statsqueries:
# 1 total books + copies
# 2 active members
# 3 overdue count
# 4 active rentals
# 5 outstanding fines
DASHBOARD_SQL = {
    1: """
SELECT COUNT(*) AS total, COALESCE(SUM(total_copies), 0) AS copies
FROM Books
""",
    2: """
SELECT COUNT(*) AS total
FROM Members
WHERE status = 'active'
""",
    3: """
SELECT COUNT(*) AS total
FROM Rentals
WHERE status IN ('active', 'overdue')
  AND due_date < CURDATE()
""",
    4: """
SELECT COUNT(*) AS total
FROM Rentals
WHERE status IN ('active', 'overdue')
""",
    5: """
SELECT COALESCE(SUM(fine_amount - paid_amount), 0) AS outstanding
FROM Fines
WHERE paid_status IN ('unpaid', 'partial')
""",
}


# These 10 quereies are the exact same as our queries on queries.sql. They are executed trhough the app.py file using the Flask query_db() function.
# Queries 1, 2, 3 are our views queries from views.sql.
QUERIES_SQL = {
    1: """
SELECT
    book_id,
    book_title,
    member_id,
    member_name,
    rental_id,
    rental_date,
    due_date,
    days_overdue,
    estimated_fine
FROM overdue_books_view
ORDER BY days_overdue DESC
""",
    2: """
SELECT
    book_id,
    title,
    author,
    category,
    total_copies,
    available_copies,
    copies_on_loan,
    availability_status,
    next_available_date
FROM book_availability_view
ORDER BY category, title
""",
    3: """
SELECT
    book_id,
    title,
    author,
    category,
    times_borrowed,
    total_copies,
    available_copies,
    last_borrowed_date
FROM popular_books_view
ORDER BY times_borrowed DESC
LIMIT 10
""",
    4: """
SELECT
    b.title,
    b.author,
    b.category,
    b.publication_year,
    b.total_copies,
    b.book_id
FROM Books b
LEFT JOIN Rentals r ON b.book_id = r.book_id
WHERE r.rental_id IS NULL
ORDER BY b.publication_year DESC
""",
    5: """
SELECT
    m.member_id,
    CONCAT(m.first_name, ' ', m.last_name) AS member_name,
    m.email,
    m.status,
    COUNT(f.fine_id) AS number_of_fines,
    SUM(f.fine_amount) AS total_fines_assessed,
    SUM(f.paid_amount) AS total_paid,
    SUM(f.fine_amount - f.paid_amount) AS outstanding_balance
FROM Members m
INNER JOIN Fines f ON m.member_id = f.member_id
GROUP BY m.member_id, m.first_name, m.last_name, m.email, m.status
ORDER BY outstanding_balance DESC, total_fines_assessed DESC
""",
    6: """
SELECT
    r.rental_id,
    b.title AS book_title,
    CONCAT(m.first_name, ' ', m.last_name) AS member_name,
    r.rental_date,
    r.due_date,
    r.status AS rental_status,
    ret.return_date,
    ret.condition_status,
    CASE
        WHEN ret.return_id IS NULL THEN 'Not Returned'
        WHEN ret.return_date <= r.due_date THEN 'Returned On Time'
        ELSE 'Returned Late'
    END AS return_timing, r.rental_id
FROM Rentals r
INNER JOIN Books b ON r.book_id = b.book_id
INNER JOIN Members m ON r.member_id = m.member_id
LEFT JOIN Returns ret ON r.rental_id = ret.rental_id
ORDER BY r.rental_date DESC
""",
    7: """
SELECT
    r.rental_id,
    b.title AS book_title,
    b.author,
    CONCAT(m.first_name, ' ', m.last_name) AS member_name,
    m.email,
    r.rental_date,
    r.due_date,
    r.status AS rental_status
FROM Rentals r
INNER JOIN Books b ON r.book_id = b.book_id
INNER JOIN Members m ON r.member_id = m.member_id
WHERE r.rental_date >= CURDATE() - INTERVAL 7 DAY
ORDER BY r.rental_date DESC
""",
    8: """
SELECT
    ret.return_id,
    b.title AS book_title,
    CONCAT(m.first_name, ' ', m.last_name) AS member_name,
    m.email,
    ret.return_date,
    f.fine_reason,
    f.fine_amount,
    f.paid_status
FROM Returns ret
INNER JOIN Rentals r ON ret.rental_id = r.rental_id
INNER JOIN Books b ON r.book_id = b.book_id
INNER JOIN Members m ON r.member_id = m.member_id
LEFT JOIN Fines f ON r.rental_id = f.rental_id
    AND f.fine_reason IN ('Damaged', 'Lost')
WHERE ret.condition_status IN ('Damaged', 'Lost')
ORDER BY ret.return_date DESC
""",
    9: """
SELECT
    DATE_FORMAT(r.rental_date, '%Y-%m') AS month,
    COUNT(*) AS total_rentals,
    COUNT(DISTINCT r.member_id) AS unique_members,
    COUNT(DISTINCT r.book_id) AS unique_books
FROM Rentals r
GROUP BY DATE_FORMAT(r.rental_date, '%Y-%m')
ORDER BY month DESC
""",
    10: """
SELECT
    f.fine_id,
    f.fine_date,
    CONCAT(m.first_name, ' ', m.last_name) AS member_name,
    b.title AS book_title,
    f.fine_reason,
    f.fine_amount,
    f.paid_amount,
    (f.fine_amount - f.paid_amount) AS outstanding_balance,
    f.paid_status
FROM Fines f
JOIN Members m ON f.member_id = m.member_id
JOIN Rentals r ON f.rental_id = r.rental_id
JOIN Books b ON r.book_id = b.book_id
WHERE f.paid_status IN ('unpaid', 'partial')
ORDER BY f.fine_date DESC
""",
}
