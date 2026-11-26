"""
StreamScope SQL Seed Generator
==============================
Converts generated CSV records into an optimized, standard SQL script:
data/processed/streamscope_seed.sql

This allows instant, seamless import into MySQL via:
- MySQL Workbench (File -> Open SQL Script -> Execute)
- MySQL CLI: mysql -u root -p streamscope < data/processed/streamscope_seed.sql
"""

import os
import csv

RAW_DIR = os.path.join("data", "raw")
OUTPUT_SQL = os.path.join("data", "processed", "streamscope_seed.sql")

def escape_sql(val):
    if val is None or val == "":
        return "NULL"
    # If numeric
    try:
        if "." in val:
            float(val)
            return val
        else:
            int(val)
            return val
    except ValueError:
        pass
    # String escape
    val_esc = str(val).replace("\\", "\\\\").replace("'", "''")
    return f"'{val_esc}'"

def generate_inserts(table_name, csv_file, columns, batch_size=1000):
    filepath = os.path.join(RAW_DIR, csv_file)
    if not os.path.exists(filepath):
        print(f"Skipping {table_name}: {filepath} not found.")
        return []

    statements = []
    statements.append(f"-- ---------------------------------------------------------")
    statements.append(f"-- Seed Data for {table_name}")
    statements.append(f"-- ---------------------------------------------------------")
    statements.append(f"SET FOREIGN_KEY_CHECKS = 0;")
    statements.append(f"TRUNCATE TABLE {table_name};")

    col_list = ", ".join(columns)

    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        batch = []
        for row in reader:
            vals = []
            for col in columns:
                raw_val = row[col]
                vals.append(escape_sql(raw_val))
            batch.append(f"({', '.join(vals)})")

            if len(batch) >= batch_size:
                stmt = f"INSERT INTO {table_name} ({col_list}) VALUES\n" + ",\n".join(batch) + ";"
                statements.append(stmt)
                batch = []

        if batch:
            stmt = f"INSERT INTO {table_name} ({col_list}) VALUES\n" + ",\n".join(batch) + ";"
            statements.append(stmt)

    statements.append(f"SET FOREIGN_KEY_CHECKS = 1;\n")
    return statements

def main():
    print("Generating optimized MySQL seed script...")
    all_sql = [
        "-- =========================================================",
        "-- StreamScope OTT Analytics - Full Database Seed Script",
        "-- Auto-generated from validated synthetic datasets",
        "-- =========================================================",
        "USE streamscope;\n"
    ]

    specs = [
        ("plans", "plans.csv", ["plan_id", "plan_name", "monthly_price", "max_screens", "video_quality"]),
        ("content", "content.csv", ["content_id", "title", "genre", "release_year", "content_type", "duration_minutes"]),
        ("users", "users.csv", ["user_id", "signup_date", "country", "age_group", "acquisition_channel", "preferred_device"]),
        ("subscriptions", "subscriptions.csv", ["subscription_id", "user_id", "plan_id", "start_date", "end_date", "status", "billing_cycle", "monthly_fee", "cancellation_reason"]),
        ("viewing_sessions", "viewing_sessions.csv", ["session_id", "user_id", "content_id", "started_at", "watch_minutes", "completion_percentage", "device_type"]),
        ("app_events", "app_events.csv", ["event_id", "user_id", "event_timestamp", "event_type", "content_id", "device_type"])
    ]

    for tbl, csv_name, cols in specs:
        print(f"  Formatting {tbl}...")
        tbl_stmts = generate_inserts(tbl, csv_name, cols, batch_size=2000)
        all_sql.extend(tbl_stmts)

    with open(OUTPUT_SQL, mode="w", encoding="utf-8") as f:
        f.write("\n".join(all_sql))

    size_mb = os.path.getsize(OUTPUT_SQL) / (1024 * 1024)
    print(f"Generated {OUTPUT_SQL} successfully! Size: {size_mb:.2f} MB")

if __name__ == "__main__":
    main()
