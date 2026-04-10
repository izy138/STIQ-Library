
-- 10 queries: JOINs, aggregates, GROUP BY, CASE, LEFT JOIN, date filters, HAVING.
-- Queries 1, 2, and 3 are read from views.sql through the app.py file.
-- Then we have 7 smaller queries for the dashboard homepage, they just display basic stats for us.

-- QUERY 1: All Currently Overdue Books
-- Uses view 1: overdue_books_view from backend/views.sql
-- shows all the overdue books and it included overdue and active rentals, shows the estimated fine
SELECT
    book_title,
    book_id,
    member_name,
    member_id,
    rental_id,
    rental_date,
    due_date,
    days_overdue,
    estimated_fine
FROM overdue_books_view
ORDER BY days_overdue DESC;

-- QUERY 2: Books by Availability Status
-- Uses view 2: book_availability_view from backend/views.sql
-- updates the availability status of each book based on the numbe of available copies.
SELECT
    title,
    author,
    category,
    book_id,
    total_copies,
    available_copies,
    copies_on_loan,
    availability_status,
    next_available_date
FROM book_availability_view
ORDER BY category, title;

-- QUERY 3: Most Popular Books
-- Uses view 3: popular_books_view from backend/views.sql.
-- It shows the top 10 most popular books by checking the num of times each book has been borrowed
SELECT
    title,
    author,
    category,
    times_borrowed,
    total_copies,
    available_copies,
    last_borrowed_date,
    book_id
FROM popular_books_view
ORDER BY times_borrowed DESC
LIMIT 10;

-- QUERY 4: Books Never Borrowed
-- finds all books that have never been borrowed by checking rental id is NULL
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
ORDER BY b.publication_year DESC;

-- QUERY 5: Total Fines by Member
-- joins members and fines to get the total fines accrued by a member
SELECT
    CONCAT(m.first_name, ' ', m.last_name) AS member_name,
    m.email,
    m.member_id,
    m.status,
    COUNT(f.fine_id) AS number_of_fines,
    SUM(f.fine_amount) AS total_fines_assessed,
    SUM(f.paid_amount) AS total_paid,
    SUM(f.fine_amount - f.paid_amount) AS outstanding_balance
FROM Members m
INNER JOIN Fines f ON m.member_id = f.member_id
GROUP BY m.member_id, m.first_name, m.last_name, m.email, m.status
ORDER BY outstanding_balance DESC, total_fines_assessed DESC;

-- QUERY 6: Rental History with Return Details
-- shows all the rental history with the return details its ordered by the rental date in descending so we can see the most recent rentals first
SELECT
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
    END AS return_timing,
    r.rental_id
FROM Rentals r
INNER JOIN Books b ON r.book_id = b.book_id
INNER JOIN Members m ON r.member_id = m.member_id
LEFT JOIN Returns ret ON r.rental_id = ret.rental_id
ORDER BY r.rental_date DESC;

-- QUERY 7: Recent Rentals for the last 7 days
-- shows only the rentals for the last week, its ordered by the rental date 
SELECT
    b.title AS book_title,
    b.author,
    CONCAT(m.first_name, ' ', m.last_name) AS member_name,
    m.email,
    r.rental_date,
    r.due_date,
    r.status AS rental_status,
    r.rental_id
FROM Rentals r
INNER JOIN Books b ON r.book_id = b.book_id
INNER JOIN Members m ON r.member_id = m.member_id
WHERE r.rental_date >= CURDATE() - INTERVAL 7 DAY
ORDER BY r.rental_date DESC;

-- QUERY 8: Damaged or Lost Books Report
-- we find books using fine_reason to display damaged or lost books only with fines included.
SELECT
    b.title AS book_title,
    b.isbn,
    CONCAT(m.first_name, ' ', m.last_name) AS member_name,
    m.email,
    ret.return_date,
    ret.condition_status,
    f.fine_reason,
    f.fine_amount,
    f.paid_status,
    r.rental_id,
    ret.return_id
FROM Returns ret
INNER JOIN Rentals r ON ret.rental_id = r.rental_id
INNER JOIN Books b ON r.book_id = b.book_id
INNER JOIN Members m ON r.member_id = m.member_id
LEFT JOIN Fines f ON r.rental_id = f.rental_id
    AND f.fine_reason IN ('Damaged', 'Lost')
WHERE ret.condition_status IN ('Damaged', 'Lost')
ORDER BY ret.return_date DESC;

-- QUERY 9: Monthly Rental Activity
-- we group the rentals by the month and year to see how many rentals, members and books were rented in each month.
SELECT 
    DATE_FORMAT(r.rental_date, '%Y-%m') AS month,
    COUNT(*) AS total_rentals,
    COUNT(DISTINCT r.member_id) AS unique_members,
    COUNT(DISTINCT r.book_id) AS unique_books
FROM Rentals r
GROUP BY DATE_FORMAT(r.rental_date, '%Y-%m')
ORDER BY month DESC;

-- Query 10: Unpaid / partial fines
-- we join the fines, members and rentals to get the unpaid or partial fines for each member and books
SELECT
    CONCAT(m.first_name, ' ', m.last_name) AS member_name,
    b.title AS book_title,
    f.fine_reason,
    f.fine_amount,
    f.paid_amount,
    (f.fine_amount - f.paid_amount) AS outstanding_balance,
    f.paid_status,
    f.fine_date,
    f.fine_id
FROM Fines f
JOIN Members m ON f.member_id = m.member_id
JOIN Rentals r ON f.rental_id = r.rental_id
JOIN Books b ON r.book_id = b.book_id
WHERE f.paid_status IN ('unpaid', 'partial')
ORDER BY f.fine_date DESC;

--
-- 
-- ALL DASHBOARD QUERIES ARE HERE 
-- These queries we run with app.py using dashboard_queries.py
-- the quereies are imported to our app.py file to be used in the dashboard homepage.

-- Dashboard Query 1: book titles and total copy count
SELECT COUNT(*) AS total_books, COALESCE(SUM(total_copies), 0) AS total_copies
FROM Books;

-- Dashboard Query 2: members with active status
SELECT COUNT(*) AS active_members
FROM Members
WHERE status = 'active';

-- Dashboard Query 3: rentals past due, this checks books that ar still checked out, active and overdue
SELECT COUNT(*) AS overdue_count
FROM Rentals
WHERE status IN ('active', 'overdue')
  AND due_date < CURDATE();

-- Dashboard Query 4: all open rentals, counts overdue rentals as well.
SELECT COUNT(*) AS active_rentals
FROM Rentals
WHERE status IN ('active', 'overdue');

-- Dashboard Query 5: total outstanding fines for the entire library.
SELECT COALESCE(SUM(fine_amount - paid_amount), 0) AS outstanding_fines
FROM Fines
WHERE paid_status IN ('unpaid', 'partial');
