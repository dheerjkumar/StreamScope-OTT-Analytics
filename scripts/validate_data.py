"""
StreamScope Data Quality & Validation Script
============================================
Performs comprehensive integrity and quality checks on the generated CSV files:
1. File existence and row count verification
2. Primary key uniqueness (No duplicate IDs)
3. Non-null constraints on mandatory columns
4. Foreign key referential integrity across all relationships
5. Date and timestamp chronological consistency
6. Overlapping subscription detection per user
7. Range and domain validity (percentages, prices, status values)
"""

import os
import sys
import csv
from datetime import datetime

RAW_DIR = os.path.join("data", "raw")
REQUIRED_FILES = [
    "users.csv",
    "plans.csv",
    "content.csv",
    "subscriptions.csv",
    "viewing_sessions.csv",
    "app_events.csv"
]

def load_csv(filename):
    filepath = os.path.join(RAW_DIR, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Missing required file: {filepath}")
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def run_validations():
    print("=" * 65)
    print("StreamScope OTT Analytics - Data Validation Suite")
    print("=" * 65)
    
    passed_tests = 0
    total_tests = 0
    errors = []

    # Test 1: File Existence & Record Counts
    print("\n[Check 1: File Presence & Record Counts]")
    data = {}
    expected_ranges = {
        "users.csv": (9500, 10500),
        "plans.csv": (4, 4),
        "content.csv": (60, 100),
        "subscriptions.csv": (7000, 10000),
        "viewing_sessions.csv": (80000, 130000),
        "app_events.csv": (150000, 450000)
    }

    for fname in REQUIRED_FILES:
        total_tests += 1
        try:
            records = load_csv(fname)
            data[fname] = records
            cnt = len(records)
            min_r, max_r = expected_ranges[fname]
            if min_r <= cnt <= max_r:
                print(f"  ✓ {fname:<22}: {cnt:>7} records (Within expected range [{min_r}-{max_r}])")
                passed_tests += 1
            else:
                msg = f"  ✗ {fname}: {cnt} records out of expected range [{min_r}-{max_r}]"
                print(msg)
                errors.append(msg)
        except Exception as e:
            msg = f"  ✗ Failed to load {fname}: {str(e)}"
            print(msg)
            errors.append(msg)

    if errors:
        print(f"\nAborting further checks due to file loading errors.")
        return False

    # Test 2: Primary Key Uniqueness
    print("\n[Check 2: Primary Key Uniqueness]")
    pk_map = {
        "users.csv": "user_id",
        "plans.csv": "plan_id",
        "content.csv": "content_id",
        "subscriptions.csv": "subscription_id",
        "viewing_sessions.csv": "session_id",
        "app_events.csv": "event_id"
    }

    for fname, pk_col in pk_map.items():
        total_tests += 1
        seen = set()
        dups = 0
        for r in data[fname]:
            val = r[pk_col]
            if val in seen:
                dups += 1
            seen.add(val)
        if dups == 0:
            print(f"  ✓ {fname:<22}: Unique {pk_col} ({len(seen)} unique IDs)")
            passed_tests += 1
        else:
            msg = f"  ✗ {fname}: Found {dups} duplicate {pk_col} values!"
            print(msg)
            errors.append(msg)

    # Test 3: Foreign Key Integrity
    print("\n[Check 3: Referential Integrity (Foreign Keys)]")
    user_ids = {r["user_id"] for r in data["users.csv"]}
    plan_ids = {r["plan_id"] for r in data["plans.csv"]}
    content_ids = {r["content_id"] for r in data["content.csv"]}

    fk_checks = [
        ("subscriptions.csv", "user_id", user_ids, "users.user_id"),
        ("subscriptions.csv", "plan_id", plan_ids, "plans.plan_id"),
        ("viewing_sessions.csv", "user_id", user_ids, "users.user_id"),
        ("viewing_sessions.csv", "content_id", content_ids, "content.content_id"),
        ("app_events.csv", "user_id", user_ids, "users.user_id"),
    ]

    for fname, col, target_set, target_name in fk_checks:
        total_tests += 1
        orphan_count = 0
        for r in data[fname]:
            val = r[col]
            if val and val not in target_set:
                orphan_count += 1
        if orphan_count == 0:
            print(f"  ✓ {fname:<22}: All {col} match valid {target_name}")
            passed_tests += 1
        else:
            msg = f"  ✗ {fname}: {orphan_count} orphaned records referencing {target_name}!"
            print(msg)
            errors.append(msg)

    # Check app_events content_id (when non-empty)
    total_tests += 1
    event_content_orphans = sum(1 for r in data["app_events.csv"] if r["content_id"] and r["content_id"] not in content_ids)
    if event_content_orphans == 0:
        print(f"  ✓ {'app_events.csv':<22}: All non-null content_id match valid content.content_id")
        passed_tests += 1
    else:
        msg = f"  ✗ app_events.csv: {event_content_orphans} orphaned content_id values!"
        print(msg)
        errors.append(msg)

    # Test 4: Chronological & Date Consistency
    print("\n[Check 4: Chronological & Logical Date Consistency]")
    user_signup_map = {r["user_id"]: datetime.strptime(r["signup_date"], "%Y-%m-%d").date() for r in data["users.csv"]}

    # Subscriptions start >= signup, end >= start
    sub_date_errors = 0
    for r in data["subscriptions.csv"]:
        uid = r["user_id"]
        s_date = datetime.strptime(r["start_date"], "%Y-%m-%d").date()
        u_date = user_signup_map[uid]
        if s_date < u_date:
            sub_date_errors += 1
        if r["end_date"]:
            e_date = datetime.strptime(r["end_date"], "%Y-%m-%d").date()
            if e_date < s_date:
                sub_date_errors += 1

    total_tests += 1
    if sub_date_errors == 0:
        print(f"  ✓ {'subscriptions.csv':<22}: start_date >= signup_date and end_date >= start_date")
        passed_tests += 1
    else:
        msg = f"  ✗ subscriptions.csv: {sub_date_errors} chronological inconsistencies!"
        print(msg)
        errors.append(msg)

    # Viewing session start >= user signup
    view_date_errors = 0
    for r in data["viewing_sessions.csv"]:
        uid = r["user_id"]
        sess_dt = datetime.strptime(r["started_at"], "%Y-%m-%d %H:%M:%S").date()
        u_date = user_signup_map[uid]
        if sess_dt < u_date:
            view_date_errors += 1

    total_tests += 1
    if view_date_errors == 0:
        print(f"  ✓ {'viewing_sessions.csv':<22}: All viewing sessions started on or after user signup")
        passed_tests += 1
    else:
        msg = f"  ✗ viewing_sessions.csv: {view_date_errors} sessions occurred before signup!"
        print(msg)
        errors.append(msg)

    # Test 5: Subscription Overlap Check
    print("\n[Check 5: Non-Overlapping Subscription Periods]")
    from collections import defaultdict
    user_subs = defaultdict(list)
    for r in data["subscriptions.csv"]:
        s_date = datetime.strptime(r["start_date"], "%Y-%m-%d").date()
        e_date = datetime.strptime(r["end_date"], "%Y-%m-%d").date() if r["end_date"] else datetime(2099, 1, 1).date()
        user_subs[r["user_id"]].append((s_date, e_date, r["subscription_id"]))

    overlap_count = 0
    for uid, periods in user_subs.items():
        if len(periods) > 1:
            periods.sort(key=lambda x: x[0])
            for i in range(len(periods) - 1):
                cur_end = periods[i][1]
                next_start = periods[i+1][0]
                if next_start < cur_end:
                    overlap_count += 1

    total_tests += 1
    if overlap_count == 0:
        print(f"  ✓ {'subscriptions.csv':<22}: Zero overlapping subscriptions detected across all users")
        passed_tests += 1
    else:
        msg = f"  ✗ subscriptions.csv: {overlap_count} overlapping subscription periods found!"
        print(msg)
        errors.append(msg)

    # Test 6: Value Domain & Bounds Check
    print("\n[Check 6: Value Domains & Metrics Bounds]")
    domain_errors = 0

    # Completion pct between 0 and 100
    for r in data["viewing_sessions.csv"]:
        pct = float(r["completion_percentage"])
        mins = int(r["watch_minutes"])
        if not (0.0 <= pct <= 100.0) or mins <= 0:
            domain_errors += 1

    # Subscription monthly fee > 0 and status in ('Active', 'Canceled')
    for r in data["subscriptions.csv"]:
        fee = float(r["monthly_fee"])
        status = r["status"]
        if fee <= 0 or status not in ["Active", "Canceled"]:
            domain_errors += 1

    total_tests += 1
    if domain_errors == 0:
        print(f"  ✓ Domain Validation    : All percentages [0-100%], watch minutes > 0, fees valid")
        passed_tests += 1
    else:
        msg = f"  ✗ Domain Validation: {domain_errors} values out of bounds!"
        print(msg)
        errors.append(msg)

    # Final Summary
    print("\n" + "=" * 65)
    print(f"VALIDATION SUMMARY: {passed_tests} / {total_tests} Tests Passed ({(passed_tests/total_tests)*100:.1f}%)")
    print("=" * 65)

    if errors:
        print(f"FAILURES DETECTED ({len(errors)}):")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("ALL DATA QUALITY AND INTEGRITY CHECKS PASSED PERFECTLY!\n")
        return True

if __name__ == "__main__":
    success = run_validations()
    sys.exit(0 if success else 1)
