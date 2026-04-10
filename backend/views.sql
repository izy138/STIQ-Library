-- These are the views queries for queries 1, 2, and 3 on queries.sql. The views are used to display the data  in the reports page.
USE library_system;

-- VIEWS Query 1: All Currently Overdue Books View
CREATE OR REPLACE VIEW overdue_books_view AS
SELECT
    r.rental_id,
    b.book_id,
    b.title AS book_title,
    m.member_id,
    CONCAT(m.first_name, ' ', m.last_name) AS member_name,
    r.rental_date,
    r.due_date,
    DATEDIFF(CURDATE(), r.due_date) AS days_overdue,
    (DATEDIFF(CURDATE(), r.due_date) * 1.00) AS estimated_fine
FROM Rentals r
INNER JOIN Books b ON r.book_id = b.book_id
INNER JOIN Members m ON r.member_id = m.member_id
WHERE r.status IN ('overdue', 'active')
    AND r.due_date < CURDATE();

-- VIEWS Query 2: Book Availability View
-- first checks book_status to see if the book is discontinued, if copies = 0 then it is unavailable, if copies <= 2 then it is low stock, if copies >= 3 then it is available.
CREATE OR REPLACE VIEW book_availability_view AS
SELECT
    b.book_id,
    b.title,
    b.author,
    b.publication_year,
    b.publisher,
    b.category,
    b.total_copies,
    b.available_copies,
    (b.total_copies - b.available_copies) AS copies_on_loan,
    CASE
        WHEN b.book_status = 'Discontinued' THEN 'Discontinued'
        WHEN b.available_copies = 0 THEN 'Unavailable'
        WHEN b.available_copies <= 2 THEN 'Low Stock'
        WHEN b.available_copies >= 3 THEN 'Available'
        ELSE 'Unknown'
    END AS availability_status,
    (SELECT MIN(r.due_date)
     FROM Rentals r
     WHERE r.book_id = b.book_id
       AND r.status = 'active') AS next_available_date
FROM Books b;

-- VIEWS Query 3:Most Popular Books View
-- shows the mose popular by checking the rental count of each book.
CREATE OR REPLACE VIEW popular_books_view AS
SELECT
    b.book_id,
    b.title,
    b.author,
    b.category,
    COUNT(r.rental_id) AS times_borrowed,
    b.total_copies,
    b.available_copies,
    MAX(r.rental_date) AS last_borrowed_date
FROM Books b
INNER JOIN Rentals r ON b.book_id = r.book_id
GROUP BY b.book_id, b.title, b.author, b.category, b.total_copies, b.available_copies
LIMIT 10;