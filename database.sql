-- ============================================
-- HOSTEL MANAGEMENT SYSTEM - DATABASE SCHEMA
-- ============================================

CREATE DATABASE IF NOT EXISTS hostel_db;
USE hostel_db;

-- Table: Administrator
CREATE TABLE IF NOT EXISTS Administrator (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fname VARCHAR(50) NOT NULL,
    lname VARCHAR(50) NOT NULL,
    mob_no VARCHAR(15) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Hostel
CREATE TABLE IF NOT EXISTS Hostel (
    hostel_id INT AUTO_INCREMENT PRIMARY KEY,
    hostel_name VARCHAR(100) NOT NULL,
    no_of_rooms INT NOT NULL DEFAULT 0,
    no_of_students INT NOT NULL DEFAULT 0,
    admin_id INT,
    FOREIGN KEY (admin_id) REFERENCES Administrator(id) ON DELETE SET NULL
);

-- Table: Student
CREATE TABLE IF NOT EXISTS Student (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    fname VARCHAR(50) NOT NULL,
    lname VARCHAR(50) NOT NULL,
    mob_no VARCHAR(15) NOT NULL,
    dept VARCHAR(100) NOT NULL,
    year_of_study INT NOT NULL CHECK (year_of_study BETWEEN 1 AND 6),
    hostel_id INT,
    FOREIGN KEY (hostel_id) REFERENCES Hostel(hostel_id) ON DELETE SET NULL
);

-- Table: Room
CREATE TABLE IF NOT EXISTS Room (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    room_no VARCHAR(10) NOT NULL,
    hostel_id INT,
    capacity INT NOT NULL DEFAULT 2,
    FOREIGN KEY (hostel_id) REFERENCES Hostel(hostel_id) ON DELETE CASCADE
);

-- Table: Stay_At (Room Allocation)
CREATE TABLE IF NOT EXISTS Stay_At (
    stay_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT UNIQUE,  -- student can only be in one room
    room_id INT,
    FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES Room(room_id) ON DELETE CASCADE
);

-- Table: Visitors
CREATE TABLE IF NOT EXISTS Visitors (
    visitor_id INT AUTO_INCREMENT PRIMARY KEY,
    visitor_name VARCHAR(100) NOT NULL,
    visit_date DATE NOT NULL,
    in_time TIME NOT NULL,
    out_time TIME,
    student_id INT,
    FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE
);

-- Table: Furniture
CREATE TABLE IF NOT EXISTS Furniture (
    furniture_id INT AUTO_INCREMENT PRIMARY KEY,
    furniture_type VARCHAR(100) NOT NULL,
    room_id INT,
    FOREIGN KEY (room_id) REFERENCES Room(room_id) ON DELETE CASCADE
);

-- ============================================
-- SAMPLE DATA
-- ============================================

-- Admin: username = admin, password = admin123
INSERT INTO Administrator (fname, lname, mob_no, username, password_hash)
VALUES ('Super', 'Admin', '9876543210', 'admin',
        '$2b$12$6R9StmGHeETqzWeTWo3TauJ/HB6d7U1R/10ljtQt1EqKWi.eH84S.');

-- Hostels
INSERT INTO Hostel (hostel_name, no_of_rooms, no_of_students, admin_id) VALUES
('Sunrise Hostel', 20, 3, 1),
('Lakeview Hostel', 15, 1, 1);

-- Rooms
INSERT INTO Room (room_no, hostel_id, capacity) VALUES
('101', 1, 2), ('102', 1, 2), ('103', 1, 3),
('201', 1, 2), ('202', 1, 2),
('101', 2, 2), ('102', 2, 3);

-- Students
INSERT INTO Student (fname, lname, mob_no, dept, year_of_study, hostel_id) VALUES
('Rahul', 'Sharma', '9000000001', 'Computer Science', 2, 1),
('Priya', 'Verma', '9000000002', 'Mechanical', 1, 1),
('Amit', 'Singh', '9000000003', 'Electronics', 3, 1),
('Neha', 'Gupta', '9000000004', 'Civil', 2, 2);

-- Room Allocations
INSERT INTO Stay_At (student_id, room_id) VALUES
(1, 1), (2, 1), (3, 2), (4, 6);

-- Visitors
INSERT INTO Visitors (visitor_name, visit_date, in_time, out_time, student_id) VALUES
('Sunita Sharma', '2026-05-01', '10:00:00', '12:00:00', 1),
('Rakesh Verma', '2026-05-01', '14:00:00', '16:30:00', 2),
('Geeta Gupta', '2026-05-02', '09:30:00', NULL, 4);

-- Furniture
INSERT INTO Furniture (furniture_type, room_id) VALUES
('Bed', 1), ('Table', 1), ('Chair', 1),
('Bed', 2), ('Table', 2),
('Bed', 6), ('Wardrobe', 6);
