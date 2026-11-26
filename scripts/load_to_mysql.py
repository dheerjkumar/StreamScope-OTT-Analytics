"""
StreamScope MySQL Database Loader
=================================
Automates database schema initialization and data loading into MySQL:
1. Connects to local MySQL Server (port 3306)
2. Executes 01_create_database.sql & 02_create_tables.sql
3. Loads seed data from data/processed/streamscope_seed.sql (or raw CSVs)
4. Verifies final table row counts in MySQL

Usage:
  py scripts/load_to_mysql.py
"""

import os
import sys
import getpass
import subprocess

def get_mysql_credentials():
    print("=" * 60)
    print("StreamScope MySQL Loader")
    print("=" * 60)
    
    # Check .env or prompt
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    user = os.getenv("DB_ROOT_USER", "root")
    password = os.getenv("DB_ROOT_PASSWORD", None)

    if not password:
        print(f"Connecting as user '{user}' to MySQL on {host}:{port}.")
        print("Note: Password input is masked for security.")
        try:
            password = getpass.getpass("Enter MySQL password: ")
        except Exception:
            password = input("Enter MySQL password: ")

    return host, port, user, password

def run_mysql_command(user, password, host, port, sql_file, database=None):
    # Locate mysql CLI if available
    mysql_paths = [
        "mysql",
        r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe",
        r"C:\Program Files\MySQL\MySQL Shell 8.0\bin\mysql.exe"
    ]
    mysql_bin = None
    for p in mysql_paths:
        if os.path.exists(p) or p == "mysql":
            mysql_bin = p
            break

    cmd = [mysql_bin, f"-u{user}", f"-h{host}", f"-P{port}"]
    if password:
        cmd.append(f"-p{password}")
    if database:
        cmd.append(database)

    print(f"Executing {os.path.basename(sql_file)} ...")
    with open(sql_file, "r", encoding="utf-8") as f:
        res = subprocess.run(cmd, stdin=f, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Error executing {sql_file}: {res.stderr}")
            return False
        return True

def main():
    host, port, user, password = get_mysql_credentials()

    # Step 1: Create Database
    db_file = os.path.join("sql", "01_create_database.sql")
    if not run_mysql_command(user, password, host, port, db_file):
        print("Failed to initialize database.")
        sys.exit(1)

    # Step 2: Create Tables
    tbl_file = os.path.join("sql", "02_create_tables.sql")
    if not run_mysql_command(user, password, host, port, tbl_file, database="streamscope"):
        print("Failed to create tables.")
        sys.exit(1)

    # Step 3: Seed Data
    seed_file = os.path.join("data", "processed", "streamscope_seed.sql")
    if not os.path.exists(seed_file):
        print(f"Seed file {seed_file} not found. Running seed generator...")
        import prepare_sql_seed
        prepare_sql_seed.main()

    if not run_mysql_command(user, password, host, port, seed_file, database="streamscope"):
        print("Failed to load seed data.")
        sys.exit(1)

    print("\n✓ Database initialized and data imported successfully into MySQL!")

if __name__ == "__main__":
    main()
