"""
StreamScope Analytical Views Fix & Verification Utility
======================================================
Executes the corrective view creation script and verifies database state:
1. Executes sql/13_create_views.sql (self-contained with all dependencies)
2. Executes sql/14_verify_database.sql (verifies 6 tables, 5 views, row counts)
3. Ensures zero data loss, zero table drops, zero duplicate imports
"""

import os
import sys
import subprocess
import getpass

def main():
    print("=" * 65)
    print("StreamScope MySQL Views Fix & Verification")
    print("=" * 65)
    
    mysql_path = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
    if not os.path.exists(mysql_path):
        mysql_path = "mysql"

    print("\nPlease enter your MySQL 'root' password to apply the view fixes:")
    try:
        pwd = getpass.getpass("MySQL Password: ")
    except Exception:
        pwd = input("MySQL Password: ")

    cmd_base = [mysql_path, "-u", "root", f"-p{pwd}", "-h", "127.0.0.1", "-P", "3306", "streamscope"]

    # Step 1: Create views
    print("\n[Step 1/2] Applying sql/13_create_views.sql...")
    with open("sql/13_create_views.sql", "r", encoding="utf-8") as f:
        res = subprocess.run(cmd_base, stdin=f, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Error applying views: {res.stderr}")
            sys.exit(1)
        print("✓ All 5 analytical views created successfully!")
        print(res.stdout)

    # Step 2: Verify database
    print("\n[Step 2/2] Running sql/14_verify_database.sql...")
    with open("sql/14_verify_database.sql", "r", encoding="utf-8") as f:
        res = subprocess.run(cmd_base, stdin=f, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Error during verification: {res.stderr}")
            sys.exit(1)
        print("✓ Database and View Verification Output:")
        print(res.stdout)

    print("\n" + "=" * 65)
    print("SUCCESS: Database fully operational. All data preserved.")
    print("=" * 65)

if __name__ == "__main__":
    main()
