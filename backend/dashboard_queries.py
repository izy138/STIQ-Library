# All of these queries are used to display for the homepage of our site. It has all the queries used for the dashboard sections. We decided to put them all in one file to make it easier to manage and view. All of these queries are also found in db_proof/queries.sql. at the bottom of the file. These queries are basic queries to display basic info about our library .

Dashboard1_BOOK_AND_COPIES = """
SELECT COUNT(*) AS total, COALESCE(SUM(total_copies), 0) AS copies
FROM Books
"""

Dashboard2_ACTIVE_MEMBERS = """
SELECT COUNT(*) AS total
FROM Members
WHERE status = 'active'
"""

Dashboard3_OVERDUE_COUNT = """
SELECT COUNT(*) AS total
FROM Rentals
WHERE status IN ('active', 'overdue')
  AND due_date < CURDATE()
"""

Dashboard4_ACTIVE_RENTALS = """
SELECT COUNT(*) AS total
FROM Rentals
WHERE status IN ('active', 'overdue')
"""

Dashboard5_OUTSTANDING_FINES = """
SELECT COALESCE(SUM(fine_amount - paid_amount), 0) AS outstanding
FROM Fines
WHERE paid_status IN ('unpaid', 'partial')
"""

Dashboard6_RECENT_RENTALS = """
SELECT r.rental_id, b.title, CONCAT(m.first_name, ' ', m.last_name) AS member_name,
       r.rental_date, r.due_date, r.status
FROM Rentals r
JOIN Books b ON r.book_id = b.book_id
JOIN Members m ON r.member_id = m.member_id
ORDER BY r.rental_date DESC
LIMIT 5
"""

Dashboard7_OVERDUE_SNAPSHOT = """
SELECT r.rental_id, b.title, CONCAT(m.first_name, ' ', m.last_name) AS member_name,
       r.due_date, DATEDIFF(CURDATE(), r.due_date) AS days_overdue
FROM Rentals r
JOIN Books b ON r.book_id = b.book_id
JOIN Members m ON r.member_id = m.member_id
WHERE r.status IN ('active', 'overdue')
  AND r.due_date < CURDATE()
ORDER BY r.due_date ASC
LIMIT 5
"""
