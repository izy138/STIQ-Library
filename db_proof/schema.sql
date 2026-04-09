-- Create database and select it
CREATE DATABASE IF NOT EXISTS library_system;
USE library_system;

-- Drop tables if they exist
DROP TABLE IF EXISTS Fines;
DROP TABLE IF EXISTS Returns;
DROP TABLE IF EXISTS Rentals;
DROP TABLE IF EXISTS Members;
DROP TABLE IF EXISTS Books;

-- TABLE: Books 
-- tracks book info and availability
CREATE TABLE Books (
    book_id INT AUTO_INCREMENT,
    isbn VARCHAR(13) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    publisher VARCHAR(255),
    publication_year INT,
    category VARCHAR(100),
    book_status ENUM('Active', 'Discontinued') DEFAULT 'Active',
    total_copies INT NOT NULL,
    available_copies INT NOT NULL,
    -- Primary Key
    CONSTRAINT pk_books PRIMARY KEY (book_id),
    -- Check Constraints
    CONSTRAINT chk_publication_year CHECK (publication_year > 1400 AND publication_year <= 2030),
    CONSTRAINT chk_total_copies CHECK (total_copies >= 0),
    CONSTRAINT chk_available_copies CHECK (available_copies >= 0 AND available_copies <= total_copies)
);

-- TABLE: Members 
-- stores library member information
CREATE TABLE Members (
    member_id INT AUTO_INCREMENT,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(15),
    membership_type ENUM('Student', 'Faculty', 'Staff') NOT NULL,
    registration_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    status ENUM('active', 'suspended', 'expired') NOT NULL DEFAULT 'active',
    max_books_allowed INT NOT NULL DEFAULT 5,
    -- Primary Key
    CONSTRAINT pk_members PRIMARY KEY (member_id),
    -- Check Constraints
    CONSTRAINT chk_max_books CHECK (
        (status = 'suspended' AND max_books_allowed = 0)
        OR (status <> 'suspended' AND max_books_allowed > 0)
    )
);

-- TABLE: Rentals 
-- tracks book borrowing and links books to members
CREATE TABLE Rentals (
    rental_id INT AUTO_INCREMENT,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    rental_date DATE NOT NULL,
    due_date DATE NOT NULL,
    status ENUM('active', 'overdue', 'returned') NOT NULL DEFAULT 'active',
    -- Primary Key
    CONSTRAINT pk_rentals PRIMARY KEY (rental_id),
    -- Foreign Keys
    CONSTRAINT fk_rentals_book FOREIGN KEY (book_id) 
        REFERENCES Books(book_id) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    CONSTRAINT fk_rentals_member FOREIGN KEY (member_id) 
        REFERENCES Members(member_id) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    -- Check Constraints
    CONSTRAINT chk_due_date CHECK (due_date > rental_date)
);

-- TABLE: Returns
-- tracks book returns, book conditions and who processed the return
-- each rental can only be returned once (1:1 relationship)
CREATE TABLE Returns (
    return_id INT AUTO_INCREMENT,
    rental_id INT UNIQUE NOT NULL,
    return_date DATE NOT NULL,
    condition_status ENUM('Good', 'Damaged', 'Lost') NOT NULL,
    notes VARCHAR(255),
    processed_by INT NOT NULL,
    -- Primary Key
    CONSTRAINT pk_returns PRIMARY KEY (return_id),
    -- Foreign Keys
    CONSTRAINT fk_returns_rental FOREIGN KEY (rental_id) 
        REFERENCES Rentals(rental_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT fk_returns_processed_by FOREIGN KEY (processed_by)
        REFERENCES Members(member_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- TABLE: Fines
-- links a fine to rentals and members, tracks payment and amount due.
-- a rental can have multiple fines (overdue + damage)
CREATE TABLE Fines (
    fine_id INT AUTO_INCREMENT,
    rental_id INT NOT NULL,
    member_id INT NOT NULL,
    fine_amount DECIMAL(10,2) NOT NULL,
    fine_reason ENUM('Overdue', 'Damaged', 'Lost') NOT NULL,
    fine_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    paid_status ENUM('unpaid', 'partial', 'paid') NOT NULL DEFAULT 'unpaid',
    paid_amount DECIMAL(10,2) DEFAULT 0.00,
    paid_date DATE,
    -- Primary Key
    CONSTRAINT pk_fines PRIMARY KEY (fine_id),
    -- Foreign Keys
    CONSTRAINT fk_fines_rental FOREIGN KEY (rental_id) 
        REFERENCES Rentals(rental_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT fk_fines_member FOREIGN KEY (member_id) 
        REFERENCES Members(member_id) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    -- Check Constraints
    CONSTRAINT chk_fine_amount CHECK (fine_amount >= 0),
    CONSTRAINT chk_paid_amount CHECK (paid_amount >= 0 AND paid_amount <= fine_amount)
);