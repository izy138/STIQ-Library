-- these are the triggers for the database, we have 4 triggers. they are used to automatically calculate the fine amount when a book is returned late, create a damage fine when a book is damaged or lost, update the available copies when a book is rented or returned, and prevent anymembers from renting a book if the account is suspended.
USE library_system;

DROP TRIGGER IF EXISTS auto_calculate_fine_on_return;
DROP TRIGGER IF EXISTS auto_create_damage_fine;
DROP TRIGGER IF EXISTS update_available_copies_on_rental;
DROP TRIGGER IF EXISTS prevent_rental_if_suspended;

-- !!!! Important !!!we need to use a delimiter (so make sure to add 'DELIMITER //' at the beginning and 'END// DELIMITER ;'  at theend of our triggers) to tell the database to execute them. using just a ; it would stop and the db would not continue to execute other triggers. 

-- TRIGGER 1: Auto Calculate a Fine On Return
-- This trigger is used to calculate the fine amount when a book is returned late.
-- It is used automatically insert the fine amount into the table.
-- It also updates the rental status to returned, and updates the available copies of the book.
DELIMITER // 
CREATE TRIGGER auto_calculate_fine_on_return
AFTER INSERT ON Returns
FOR EACH ROW
BEGIN
    DECLARE trig_due_date DATE;
    DECLARE trig_member_id INT;
    DECLARE trig_book_id INT;
    DECLARE trig_days_late INT;
    DECLARE trig_fine_amount DECIMAL(10,2);

    SELECT due_date, member_id, book_id
    INTO trig_due_date, trig_member_id, trig_book_id
    FROM Rentals
    WHERE rental_id = NEW.rental_id;

    SET trig_days_late = DATEDIFF(NEW.return_date, trig_due_date);

    IF trig_days_late > 0 THEN
        SET trig_fine_amount = trig_days_late * 1.00;
        INSERT INTO Fines (rental_id, member_id, fine_amount, fine_reason, fine_date, paid_status, paid_amount)
        VALUES (NEW.rental_id, trig_member_id, trig_fine_amount, 'Overdue', NEW.return_date, 'unpaid', 0.00);
    END IF;

    UPDATE Rentals
    SET status = 'returned'
    WHERE rental_id = NEW.rental_id;

    UPDATE Books
    SET available_copies = available_copies + 1
    WHERE book_id = trig_book_id;

END//

DELIMITER ;

-- TRIGGER 2: Auto Create a Damage Fine
-- This is used to automaticaly create a damage fine when a book is damaged or lost.
DELIMITER //

CREATE TRIGGER auto_create_damage_fine
AFTER INSERT ON Returns
FOR EACH ROW
BEGIN
    DECLARE trig_member_id INT;
    DECLARE trig_damage_fine DECIMAL(10,2);

    SELECT member_id
    INTO trig_member_id
    FROM Rentals
    WHERE rental_id = NEW.rental_id;

    IF NEW.condition_status = 'Damaged' THEN
        SET trig_damage_fine = 25.00;
        INSERT INTO Fines (rental_id, member_id, fine_amount, fine_reason, fine_date, paid_status, paid_amount)
        VALUES (NEW.rental_id, trig_member_id, trig_damage_fine, 'Damaged', NEW.return_date, 'unpaid', 0.00);
    END IF;

    IF NEW.condition_status = 'Lost' THEN
        SET trig_damage_fine = 50.00;
        INSERT INTO Fines (rental_id, member_id, fine_amount, fine_reason, fine_date, paid_status, paid_amount)
        VALUES (NEW.rental_id, trig_member_id, trig_damage_fine, 'Lost', NEW.return_date, 'unpaid', 0.00);
    END IF;

END//

DELIMITER ;

-- TRIGGER 3: Update Available Copies On Rental
-- used to auto update the available copies when a book is rented or returned.
DELIMITER //

CREATE TRIGGER update_available_copies_on_rental
AFTER INSERT ON Rentals
FOR EACH ROW
BEGIN
    UPDATE Books
    SET available_copies = available_copies - 1
    WHERE book_id = NEW.book_id
        AND available_copies > 0;
END//

DELIMITER ;

-- TRIGGER 4: Prevent a Rental If Suspended
-- used to prevent any members from renting a book if the account is suspended. 
-- This has been tested and shows an error message.
DELIMITER //

CREATE TRIGGER prevent_rental_if_suspended
BEFORE INSERT ON Rentals
FOR EACH ROW
BEGIN
    DECLARE trig_member_status VARCHAR(20);

    SELECT status INTO trig_member_status
    FROM Members
    WHERE member_id = NEW.member_id;

    IF trig_member_status = 'suspended' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot rent books: Member account is suspended';
    END IF;
END//

DELIMITER ;
