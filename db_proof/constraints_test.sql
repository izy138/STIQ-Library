USE library_system;

-- TEST 1: Foreign Key Constraints
-- Attempt to insert a rental with a non-existent book_id.
INSERT INTO Rentals (book_id, member_id, rental_date, due_date, status)
VALUES (999, 1, '2026-03-01', '2026-03-10', 'active');
-- ERROR 1452 (23000) at line 6: Cannot add or update a child row: a foreign key constraint fails (`library_system`.`rentals`, CONSTRAINT `fk_rentals_book` FOREIGN KEY (`book_id`) REFERENCES `books` (`book_id`) ON DELETE RESTRICT ON UPDATE CASCADE)

-- Attempt to insert a return with a non-existent rental_id.
INSERT INTO Returns (rental_id, return_date, condition_status, notes, processed_by)
VALUES (999, '2026-03-05', 'Good', 'Test invalid rental', 1);
-- ERROR 1452 (23000) at line 11: Cannot add or update a child row: a foreign key constraint fails (`library_system`.`rentals`, CONSTRAINT `fk_rentals_member` FOREIGN KEY (`member_id`) REFERENCES `members` (`member_id`) ON DELETE RESTRICT ON UPDATE CASCADE)

-- TEST 2: Unique Constraints
-- ============================================================
-- Attempt to insert a book with a duplicate ISBN.
INSERT INTO Books (isbn, title, author, publisher, publication_year, category, total_copies, available_copies)
VALUES ('9783869711423', 'Duplicate Book', 'Test Author', 'Test Publisher', 2020, 'Test', 1, 1);
-- ERROR 1062 (23000) at line 18: Duplicate entry '9783869711423' for key 'books.isbn'

-- Attempt to insert a member with a duplicate email.
INSERT INTO Members (first_name, last_name, email, phone, membership_type, registration_date, status, max_books_allowed)
VALUES ('Test', 'User', 'crodriguez032@fiu.edu', '3055550000', 'Student', '2026-03-10', 'active', 5);
-- ERROR 1062 (23000) at line 23: Duplicate entry 'crodriguez032@fiu.edu' for key 'members.email'

-- Attempt to insert a return for a rental_id that already exists in Returns.
INSERT INTO Returns (rental_id, return_date, condition_status, notes, processed_by)
VALUES (1, '2026-03-10', 'Good', 'Returned on time', 1);
-- ERROR 1452 (23000) at line 29: Cannot add or update a child row: a foreign key constraint fails (`library_system`.`returns`, CONSTRAINT `fk_returns_rental` FOREIGN KEY (`rental_id`) REFERENCES `rentals` (`rental_id`) ON DELETE CASCADE ON UPDATE CASCADE)

-- TEST 3: NOT NULL Constraints
-- ============================================================
-- Attempt to insert a book with a NULL title.
INSERT INTO Books (isbn, title, author, publisher, publication_year, category, book_status, total_copies, available_copies)
VALUES ('1234567890123', NULL, 'John Smith', 'Pearson', 2020, 'Fiction', 'Active', 5, 5);
-- ERROR 1048 (23000) at line 36: Column 'title' cannot be null

-- Attempt to insert a fine with a NULL fine_amount.
INSERT INTO Fines (rental_id, member_id, fine_amount, fine_reason, fine_date, paid_status, paid_amount)
VALUES (3, 1, NULL, 'Overdue', '2026-03-05', 'unpaid', 0.00);
-- ERROR 1048 (23000) at line 45: Column 'fine_amount' cannot be null

-- TEST 4: ENUM Constraints (Invalid Values)
-- ============================================================
-- Attempt to insert a rental with an invalid status value.
INSERT INTO Rentals (book_id, member_id, rental_date, due_date, status)
VALUES (1, 1, '2026-03-10', '2026-03-25', 'lost');
-- ERROR 1265 (01000) at line 52: Data truncated for column 'status' at row 1

-- Attempt to insert a fine with an invalid paid_status value.
INSERT INTO Fines (rental_id, member_id, fine_amount, fine_reason, fine_date, paid_status, paid_amount)
VALUES (1, 1, 5.00, 'Overdue', '2026-03-10', 'complete', 0.00);
-- ERROR 1265 (01000) at line 57: Data truncated for column 'paid_status' at row 1

-- TEST 5: CASCADE / RESTRICT on DELETE
-- ============================================================
-- Attempt to delete a book that is still referenced by rentals.
DELETE FROM Books WHERE book_id = 1;
-- ERROR 1451 (23000) at line 64: Cannot delete or update a parent row: a foreign key constraint fails (`library_system`.`rentals`, CONSTRAINT `fk_rentals_book` FOREIGN KEY (`book_id`) REFERENCES `books` (`book_id`) ON DELETE RESTRICT ON UPDATE CASCADE)

-- TEST 6: Check Constraint — Members (chk_max_books)
-- Rule: suspended members must have max_books_allowed = 0,
--       non-suspended members must have max_books_allowed > 0
-- ============================================================
-- Attempt to insert an active member with a negative max_books_allowed value.
INSERT INTO Members (first_name, last_name, email, phone, membership_type, registration_date, status, max_books_allowed)
VALUES ('Jessica', 'Alvarez', 'jalvarez_201@fiu.edu', '3055552002', 'Student', '2026-03-01', 'active', -5);
-- EXPECTED ERROR: CheckERROR 3819 (HY000) at line 72: Check constraint 'chk_max_books' is violated. 

-- TEST 7: Check Constraint — Rentals (chk_due_date)
-- Rule: due_date must be strictly greater than rental_date
-- ============================================================
-- Attempt to insert a rental where due_date is before rental_date.
INSERT INTO Rentals (book_id, member_id, rental_date, due_date, status)
VALUES (1, 1, '2026-03-10', '2026-03-05', 'active');
-- ERROR 3819 (HY000) at line 80: Check constraint 'chk_due_date' is violated.

-- TEST 8: Check Constraint — Books (chk_publication_year, chk_total_copies, chk_available_copies)
-- Rules: publication_year > 1400 AND <= 2030
--        total_copies >= 0
--        available_copies >= 0 AND available_copies <= total_copies
-- ============================================================
-- Attempt to insert a book with a publication_year below the allowed range.
INSERT INTO Books (isbn, title, author, publisher, publication_year, category, total_copies, available_copies)
VALUES ('9781111111111', 'Ancient Text', 'Unknown', 'Lost Press', 1300, 'Literature', 3, 3);
-- ERROR 3819 (HY000) at line 90: Check constraint 'chk_publication_year' is violated.

-- Attempt to insert a book with a negative total_copies value.
INSERT INTO Books (isbn, title, author, publisher, publication_year, category, total_copies, available_copies)
VALUES ('9782222222222', 'Bad Copies', 'Test Author', 'Test Pub', 2020, 'Fiction', -1, 0);
-- ERROR 3819 (HY000) at line 95: Check constraint 'chk_available_copies' is violated.

-- TEST 9: Check Constraint — Fines (chk_fine_amount, chk_paid_amount)
-- Rules: fine_amount >= 0
--        paid_amount >= 0 AND paid_amount <= fine_amount
-- ============================================================
-- Attempt to insert a fine with a negative fine_amount.
INSERT INTO Fines (rental_id, member_id, fine_amount, fine_reason, fine_date, paid_status, paid_amount)
VALUES (1, 1, -5.00, 'Overdue', '2026-03-10', 'unpaid', 0.00);
-- ERROR 3819 (HY000) at line 104: Check constraint 'chk_fine_amount' is violated.

-- Attempt to insert a fine where paid_amount is greater than fine_amount.
INSERT INTO Fines (rental_id, member_id, fine_amount, fine_reason, fine_date, paid_status, paid_amount)
VALUES (1, 1, 5.00, 'Overdue', '2026-03-10', 'unpaid', 10.00);
-- ERROR 3819 (HY000) at line 109: Check constraint 'chk_paid_amount' is violated.
