USE library_system;

INSERT INTO Books (isbn, title, author, publisher, publication_year, category, total_copies, available_copies) VALUES
('9780553213119', 'Romeo and Juliet', 'William Shakespeare', 'Bantam Classics', 1980, 'Literature', 5, 2),
('9780141439518', 'Pride and Prejudice', 'Jane Austen', 'Penguin Classics', 2003, 'Literature', 5, 2),
('9780141439600', 'Wuthering Heights', 'Emily Brontë', 'Penguin Classics', 2003, 'Literature', 4, 1),
('9780743273565', 'The Great Gatsby', 'F. Scott Fitzgerald', 'Scribner', 2004, 'Literature', 4, 0),
('9780060935467', 'To Kill a Mockingbird', 'Harper Lee', 'Harper Perennial', 2006, 'Literature', 5, 4),
('9780451524935', '1984', 'George Orwell', 'Signet Classic', 1950, 'Literature', 3, 3),
('9780486282114', 'Frankenstein', 'Mary Shelley', 'Dover Publications', 1994, 'Literature', 4, 1),
('9780141439556', 'Jane Eyre', 'Charlotte Brontë', 'Penguin Classics', 2006, 'Literature', 3, 3);

INSERT INTO Members (first_name, last_name, email, phone, membership_type, registration_date, status, max_books_allowed) VALUES
('Chris', 'Rodriguez', 'crodriguez032@fiu.edu', '3055551234', 'Student', '2026-01-06', 'active', 5),
('Isabella', 'Perez', 'iperez@fiu.edu', '3055555678', 'Student', '2026-01-02', 'active', 5),
('Maria', 'Lopez', 'mlopez@fiu.edu', '3055559012', 'Faculty', '2026-02-02', 'active', 10),
('Kevin', 'Smith', 'ksmith@fiu.edu', '3055553456', 'Staff', '2026-01-23', 'suspended', 3),
('Jalen', 'Brown', 'jbrown@fiu.edu', '3055557890', 'Student', '2026-02-07', 'expired', 5),
('Chris', 'Lawrence', 'clawre@fiu.edu', '3055557231', 'Student', '2026-02-03', 'active', 5),
('Anna', 'Gonzalez', 'agonza@fiu.edu', '3055553121', 'Student', '2026-02-15', 'active', 5);

INSERT INTO Rentals (book_id, member_id, rental_date, due_date, status) VALUES
(1, 5, '2026-02-20', '2026-03-27', 'active'),
(2, 2, '2026-02-22', '2026-03-22', 'active'),
(3, 1, '2026-02-23', '2026-03-02', 'returned'),
(4, 1, '2026-02-24', '2026-03-23', 'active'),
(5, 4, '2026-02-25', '2026-03-04', 'returned'),
(6, 3, '2026-02-26', '2026-03-03', 'overdue'),
(7, 2, '2026-02-27', '2026-03-06', 'returned'),
(2, 7, '2026-02-17', '2026-03-01', 'returned'),
(5, 3, '2026-02-22', '2026-03-03', 'returned'),
(4, 6, '2026-02-18', '2026-02-25', 'returned');

INSERT INTO Returns (rental_id, return_date, condition_status, notes, processed_by) VALUES
(3, '2026-03-03', 'Good', '1 day overdue', 1),
(5, '2026-03-04', 'Good', 'On time', 1),
(7, '2026-03-12', 'Good', '6 days overdue', 1),
(8, '2026-03-01', 'Damaged', NULL, 1),
(9, '2026-03-03', 'Damaged', NULL, 1),
(10, '2026-02-25', 'Lost', NULL, 1);

-- $1/day overdue, $25 damage, Lost = replacement + $15
INSERT INTO Fines (rental_id, member_id, fine_amount, fine_reason, fine_date, paid_status, paid_amount, paid_date) VALUES
(3, 1, 1.00, 'Overdue', '2026-03-01', 'paid', 1.00, '2026-03-02'),
(6, 3, 5.00, 'Overdue', '2026-03-02', 'unpaid', 0.00, NULL),
(7, 2, 6.00, 'Overdue', '2026-03-05', 'partial', 3.00, NULL),
(8, 7, 25.00, 'Damaged', '2026-03-01', 'unpaid', 0.00, NULL),
(9, 3, 25.00, 'Damaged', '2026-03-03', 'paid', 25.00, '2026-03-03'),
(10, 6, 60.00, 'Lost', '2026-02-25', 'paid', 50.00, '2026-02-27');
