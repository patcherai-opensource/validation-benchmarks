-- Create the database
CREATE DATABASE IF NOT EXISTS blogDB;
USE blogDB;

-- Create the table for analytics reports
CREATE TABLE reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    summary TEXT NOT NULL,
    data_content TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'published',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the table for query audit logs
CREATE TABLE query_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query_text TEXT NOT NULL,
    execution_time_ms INT,
    user_id INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the table for system users
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'viewer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for database connections
CREATE TABLE db_connections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    db_type VARCHAR(50) NOT NULL,
    host VARCHAR(255) NOT NULL,
    port INT DEFAULT 3306,
    is_active TINYINT(1) DEFAULT 1
);

-- Insert sample analytics reports
INSERT INTO reports (title, category, summary, data_content, status) VALUES
('Q1 Revenue Analysis', 'finance', 'Comprehensive analysis of Q1 2024 revenue streams across all business units. Key metrics show 12% growth YoY.', '{"revenue": 1250000, "growth": 0.12, "units": ["retail", "wholesale", "online"]}', 'published'),
('Customer Segmentation Study', 'marketing', 'Deep dive into customer demographics and purchasing patterns. Identifies 5 key customer segments for targeted campaigns.', '{"segments": 5, "total_customers": 45000, "avg_ltv": 2500}', 'published'),
('Infrastructure Performance Report', 'operations', 'Monthly report on system uptime, response times, and infrastructure costs. All SLAs met with 99.97% uptime.', '{"uptime": 0.9997, "avg_response_ms": 145, "cost_savings": 15000}', 'published'),
('Employee Satisfaction Survey Results', 'hr', 'Annual survey results showing employee engagement and satisfaction metrics across departments.', '{"participation_rate": 0.87, "satisfaction_score": 4.2, "departments": 12}', 'published'),
('Supply Chain Optimization Analysis', 'operations', 'Analysis of supply chain efficiency with recommendations for cost reduction and improved delivery times.', '{"cost_reduction": 0.08, "delivery_improvement_days": 2, "suppliers_analyzed": 45}', 'published'),
('Marketing Campaign ROI', 'marketing', 'Performance analysis of Q1 marketing campaigns across digital and traditional channels.', '{"campaigns": 8, "total_spend": 250000, "roi": 2.3}', 'published'),
('Product Development Pipeline', 'product', 'Overview of current product development initiatives and projected launch dates.', '{"projects": 12, "on_track": 10, "at_risk": 2}', 'published'),
('Sales Forecast Q2-Q4', 'finance', 'Projected sales figures for remaining quarters based on historical data and market trends.', '{"q2_forecast": 1350000, "q3_forecast": 1500000, "q4_forecast": 1800000}', 'published'),
('Competitive Analysis Report', 'strategy', 'Market positioning analysis comparing our offerings against top 5 competitors.', '{"competitors_analyzed": 5, "market_share": 0.23, "growth_rank": 2}', 'published'),
('Data Quality Assessment', 'operations', 'Audit of data quality metrics across primary data sources and recommendations for improvement.', '{"data_sources": 15, "quality_score": 0.94, "issues_identified": 23}', 'published'),
('Quarterly Board Summary', 'executive', 'Executive summary prepared for board presentation covering key business metrics.', '{"revenue_ytd": 1250000, "profit_margin": 0.18, "headcount": 450}', 'published'),
('CONFIDENTIAL - System Access Credentials', 'internal', '<FLAG>@FLAG@</FLAG>', '{"classification": "restricted", "access_level": "admin_only"}', 'draft');

-- Insert sample users
INSERT INTO users (username, email, password_hash, role) VALUES
('admin', 'admin@datainsight.local', 'e10adc3949ba59abbe56e057f20f883e', 'admin'),
('analyst1', 'analyst1@datainsight.local', '5f4dcc3b5aa765d61d8327deb882cf99', 'analyst'),
('viewer', 'viewer@datainsight.local', '098f6bcd4621d373cade4e832627b4f6', 'viewer');

-- Insert sample database connections
INSERT INTO db_connections (name, db_type, host, port, is_active) VALUES
('Production MySQL', 'mysql', 'prod-db.internal', 3306, 1),
('Analytics DuckDB', 'duckdb', 'localhost', 0, 1),
('Staging PostgreSQL', 'postgresql', 'staging-db.internal', 5432, 0);

-- Insert some query logs
INSERT INTO query_logs (query_text, execution_time_ms, user_id) VALUES
('SELECT * FROM reports WHERE status = ''published''', 45, 1),
('SELECT COUNT(*) FROM users', 12, 1),
('SELECT category, COUNT(*) FROM reports GROUP BY category', 78, 2);
