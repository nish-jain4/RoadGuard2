CREATE DATABASE roadguard_db;
USE roadguard_db;

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Workshops table
CREATE TABLE workshops (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address TEXT NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    description TEXT,
    owner_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);

-- Workshop services table
CREATE TABLE workshop_services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    workshop_id INT NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workshop_id) REFERENCES workshops(id) ON DELETE CASCADE
);

-- Workshop pricing table
CREATE TABLE workshop_pricing (
    id INT AUTO_INCREMENT PRIMARY KEY,
    workshop_id INT NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (workshop_id) REFERENCES workshops(id) ON DELETE CASCADE
);

-- Workshop hours table
CREATE TABLE workshop_hours (
    id INT AUTO_INCREMENT PRIMARY KEY,
    workshop_id INT NOT NULL,
    day ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
    open_time TIME NOT NULL,
    close_time TIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workshop_id) REFERENCES workshops(id) ON DELETE CASCADE
);

-- Service requests table
CREATE TABLE service_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    workshop_id INT NOT NULL,
    mechanic_id INT,
    vehicle_type VARCHAR(50) NOT NULL,
    vehicle_model VARCHAR(50) NOT NULL,
    service_type VARCHAR(100) NOT NULL,
    problem_description TEXT NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    address TEXT NOT NULL,
    urgency ENUM('normal', 'urgent', 'emergency') DEFAULT 'normal',
    status ENUM('pending', 'accepted', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
    quotation DECIMAL(10, 2),
    rating INT,
    review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accepted_at TIMESTAMP NULL,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (workshop_id) REFERENCES workshops(id),
    FOREIGN KEY (mechanic_id) REFERENCES users(id)
);

-- Reviews table
CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    workshop_id INT NOT NULL,
    service_request_id INT,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (workshop_id) REFERENCES workshops(id),
    FOREIGN KEY (service_request_id) REFERENCES service_requests(id)
);

-- Saved workshops table
CREATE TABLE saved_workshops (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    workshop_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (workshop_id) REFERENCES workshops(id),
    UNIQUE KEY unique_saved_workshop (user_id, workshop_id)
);

-- Insert sample data
INSERT INTO users (name, email, phone, password) VALUES 
('John Doe', 'john@example.com', '+1234567890', 'password123'),
('Jane Smith', 'jane@example.com', '+0987654321', 'password123');

INSERT INTO workshops (name, email, phone, address, latitude, longitude, description) VALUES 
('City Auto Repair', 'cityauto@example.com', '+1122334455', '123 Main St, New York, NY', 40.7128, -74.0060, 'Full-service auto repair shop with 20 years of experience'),
('Quick Fix Mechanics', 'quickfix@example.com', '+5566778899', '456 Oak Ave, Brooklyn, NY', 40.6782, -73.9442, 'Fast and reliable car repair services');

INSERT INTO workshop_services (workshop_id, service_name) VALUES 
(1, 'Tire Change'), (1, 'Oil Change'), (1, 'Brake Repair'), (1, 'Battery Replacement'),
(2, 'Tire Change'), (2, 'Jump Start'), (2, 'Fuel Delivery'), (2, 'Lockout Service');

INSERT INTO workshop_pricing (workshop_id, service_name, price) VALUES 
(1, 'Tire Change', 50.00), (1, 'Oil Change', 35.00), (1, 'Brake Repair', 120.00), (1, 'Battery Replacement', 80.00),
(2, 'Tire Change', 45.00), (2, 'Jump Start', 30.00), (2, 'Fuel Delivery', 40.00), (2, 'Lockout Service', 50.00);

INSERT INTO workshop_hours (workshop_id, day, open_time, close_time) VALUES 
(1, 'Monday', '08:00:00', '18:00:00'),
(1, 'Tuesday', '08:00:00', '18:00:00'),
(1, 'Wednesday', '08:00:00', '18:00:00'),
(1, 'Thursday', '08:00:00', '18:00:00'),
(1, 'Friday', '08:00:00', '18:00:00'),
(1, 'Saturday', '09:00:00', '16:00:00'),
(2, 'Monday', '07:00:00', '19:00:00'),
(2, 'Tuesday', '07:00:00', '19:00:00'),
(2, 'Wednesday', '07:00:00', '19:00:00'),
(2, 'Thursday', '07:00:00', '19:00:00'),
(2, 'Friday', '07:00:00', '19:00:00'),
(2, 'Saturday', '08:00:00', '17:00:00');