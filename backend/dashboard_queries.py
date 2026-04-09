
# All of these queries are used to display for the homepage of our site. It has all the queries used for the dashboard sections. We decided to put them all in one file to make it easier to manage and view. All of these queries are also found in db_proof/queries.sql at the bottom of the file. These queries are basic queries to display basic info about our library.
# 1: total books + total copies
# 2: active members
# 3: overdue count
# 4: active rentals
# 5: outstanding fines
# 6: recent rentals snapshot
# 7: overdue snapshot
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
    6: """
SELECT r.rental_id, b.title, CONCAT(m.first_name, ' ', m.last_name) AS member_name,
       r.rental_date, r.due_date, r.status
FROM Rentals r
JOIN Books b ON r.book_id = b.book_id
JOIN Members m ON r.member_id = m.member_id
ORDER BY r.rental_date DESC
LIMIT 5
""",
    7: """
SELECT r.rental_id, b.title, CONCAT(m.first_name, ' ', m.last_name) AS member_name,
       r.due_date, DATEDIFF(CURDATE(), r.due_date) AS days_overdue
FROM Rentals r
JOIN Books b ON r.book_id = b.book_id
JOIN Members m ON r.member_id = m.member_id
WHERE r.status IN ('active', 'overdue')
  AND r.due_date < CURDATE()
ORDER BY r.due_date ASC
LIMIT 5
""",
}
