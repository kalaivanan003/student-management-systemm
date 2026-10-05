CREATE DATABASE IF NOT EXISTS student_management;
USE student_management;

CREATE TABLE IF NOT EXISTS students (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(100) NOT NULL UNIQUE,
    phone      VARCHAR(15)  NOT NULL,
    age        INT          NOT NULL,
    gender     VARCHAR(20)  NOT NULL,
    course     VARCHAR(100) NOT NULL,
    address    VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO students (name, email, phone, age, gender, course, address) VALUES
('Arjun Kumar',    'arjun.kumar@example.com',   '9876543210', 21, 'Male',   'Python Full Stack', '12 Anna Nagar, Chennai'),
('Priya Sharma',   'priya.sharma@example.com',  '9123456780', 20, 'Female', 'Data Science',      '45 T Nagar, Chennai'),
('Karthik Raj',    'karthik.raj@example.com',   '9988776655', 22, 'Male',   'Cyber Security',    '7 Gandhi Road, Coimbatore'),
('Divya Lakshmi',  'divya.lakshmi@example.com', '8765432109', 19, 'Female', 'Python Full Stack', '23 Race Course, Madurai'),
('Mohammed Faiz',  'faiz.m@example.com',        '7012345678', 23, 'Male',   'Web Development',   '88 Mount Road, Chennai'),
('Sneha Reddy',    'sneha.reddy@example.com',   '6301234567', 21, 'Female', 'Data Science',      NULL);
