-- =====================================================================
-- StreamScope OTT Analytics
-- Script 01: Database Initialization
-- Author: StreamScope Data & Product Analytics Team
-- RDBMS: MySQL 8.0+
-- =====================================================================

-- 1. Create Database if it does not already exist
CREATE DATABASE IF NOT EXISTS streamscope
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- 2. Switch to the active database
USE streamscope;

-- 3. Optional: Create a dedicated read-only user for Power BI / Reporting
-- Uncomment and execute with admin privileges if required:
-- CREATE USER IF NOT EXISTS 'streamscope_reader'@'%' IDENTIFIED BY 'StreamScope2025!Read';
-- GRANT SELECT, SHOW VIEW ON streamscope.* TO 'streamscope_reader'@'%';
-- FLUSH PRIVILEGES;

SELECT 'Database streamscope created and selected successfully.' AS status;
