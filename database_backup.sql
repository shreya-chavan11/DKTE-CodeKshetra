CREATE DATABASE IF NOT EXISTS breathcoder_db;
USE breathcoder_db;

CREATE TABLE IF NOT EXISTS patient_diagnostics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_name VARCHAR(100),
    age INT,
    gender VARCHAR(20),
    is_asthmatic BOOLEAN,
    smoking_years INT,
    risk_probability DECIMAL(5, 2),
    status VARCHAR(50),
    fev1_fvc_ratio DECIMAL(4, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

