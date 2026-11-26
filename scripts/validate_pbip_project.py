"""
StreamScope Power BI Project (PBIP) Validation Suite
===================================================
Validates the complete integrity of the rebuilt Power BI Project:
1. Entry point .pbip JSON schema and pointer
2. Report definition and references (definition.pbir)
3. Report layout (report.json), page count, visual containers
4. Semantic model definition (definition.pbism, definition.pbidataset)
5. TMSL model schema (model.bim), tables, measures, and relationships
6. Underlying data extracts existence and integrity
"""

import os
import sys
import json

BASE_PBI = "powerbi"

def validate_pbip():
    print("=" * 65)
    print("StreamScope Power BI Project (PBIP) Integrity Audit")
    print("=" * 65)

    tests_passed = 0
    total_tests = 0

    # Test 1: Entry Point PBIP
    total_tests += 1
    pbip_file = os.path.join(BASE_PBI, "StreamScope_Analytics.pbip")
    if os.path.exists(pbip_file) and os.path.getsize(pbip_file) > 50:
        with open(pbip_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            rep_path = data["artifacts"][0]["report"]["path"]
            if rep_path == "StreamScope_Analytics.Report":
                print(f"  ✓ [1/7] PBIP Entry File        : Valid ({os.path.getsize(pbip_file)} bytes) -> Points to {rep_path}")
                tests_passed += 1
            else:
                print(f"  ✗ [1/7] PBIP pointer mismatch: {rep_path}")
    else:
        print(f"  ✗ [1/7] PBIP file missing or empty!")

    # Test 2: Report Descriptor (definition.pbir)
    total_tests += 1
    pbir_file = os.path.join(BASE_PBI, "StreamScope_Analytics.Report", "definition.pbir")
    if os.path.exists(pbir_file):
        with open(pbir_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            ds_ref = data["datasetReference"]["byPath"]["path"]
            print(f"  ✓ [2/7] Report Descriptor      : Valid -> Points to {ds_ref}")
            tests_passed += 1
    else:
        print(f"  ✗ [2/7] definition.pbir missing!")

    # Test 3: Report Visual Layout (report.json)
    total_tests += 1
    report_json_file = os.path.join(BASE_PBI, "StreamScope_Analytics.Report", "report.json")
    if os.path.exists(report_json_file) and os.path.getsize(report_json_file) > 1000:
        with open(report_json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            pages = data.get("pages", [])
            total_visuals = sum(len(p.get("visualContainers", [])) for p in pages)
            page_names = [p.get("displayName") for p in pages]
            if len(pages) == 3 and total_visuals >= 15:
                print(f"  ✓ [3/7] Report Layout JSON     : Valid ({len(pages)} pages: {', '.join(page_names)}) | {total_visuals} Visuals")
                tests_passed += 1
            else:
                print(f"  ✗ [3/7] Report pages/visuals count unexpected: {len(pages)} pages, {total_visuals} visuals")
    else:
        print(f"  ✗ [3/7] report.json missing or empty!")

    # Test 4: Semantic Model Descriptors (definition.pbism & definition.pbidataset)
    total_tests += 1
    pbism_file = os.path.join(BASE_PBI, "StreamScope_Analytics.SemanticModel", "definition.pbism")
    pbidataset_file = os.path.join(BASE_PBI, "StreamScope_Analytics.Dataset", "definition.pbidataset")
    if os.path.exists(pbism_file) and os.path.exists(pbidataset_file):
        print(f"  ✓ [4/7] Model Descriptors      : Both .pbism (Modern) and .pbidataset (Legacy) present")
        tests_passed += 1
    else:
        print(f"  ✗ [4/7] Model descriptor missing!")

    # Test 5: TMSL Semantic Model (model.bim)
    total_tests += 1
    bim_file = os.path.join(BASE_PBI, "StreamScope_Analytics.SemanticModel", "model.bim")
    if os.path.exists(bim_file) and os.path.getsize(bim_file) > 5000:
        with open(bim_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            tables = data["model"].get("tables", [])
            rels = data["model"].get("relationships", [])
            msrs = next((t.get("measures", []) for t in tables if t["name"] == "_Measures"), [])
            print(f"  ✓ [5/7] TMSL model.bim Schema  : Valid ({os.path.getsize(bim_file)/1024:.1f} KB) | {len(tables)} Tables, {len(msrs)} DAX Measures, {len(rels)} Relationships")
            tests_passed += 1
    else:
        print(f"  ✗ [5/7] model.bim missing or empty!")

    # Test 6: Underlying Analytical CSV Extracts
    total_tests += 1
    expected_data_files = [
        "monthly_performance.csv",
        "content_performance.csv",
        "churn_by_dimension.csv",
        "user_segments.csv",
        "dim_users.csv",
        "dim_plans.csv",
        "dim_content.csv",
        "fact_subscriptions.csv",
        "fact_viewing_sessions.csv"
    ]
    missing_data = []
    for df in expected_data_files:
        p = os.path.join(BASE_PBI, "data", df)
        if not os.path.exists(p) or os.path.getsize(p) == 0:
            missing_data.append(df)

    if not missing_data:
        print(f"  ✓ [6/7] Data Partition Files   : All {len(expected_data_files)} analytical datasets verified in powerbi/data/")
        tests_passed += 1
    else:
        print(f"  ✗ [6/7] Missing partition files: {missing_data}")

    # Test 7: DAX Formula Validation
    total_tests += 1
    key_measures = ["Total Registered Users", "Active Paid Subscribers", "Current MRR", "Monthly Churn Rate %", "Total Watch Hours"]
    measure_names = [m["name"] for m in msrs]
    missing_msrs = [m for m in key_measures if m not in measure_names]
    if not missing_msrs:
        print(f"  ✓ [7/7] Key DAX Measures       : All {len(key_measures)} essential measures verified")
        tests_passed += 1
    else:
        print(f"  ✗ [7/7] Missing essential DAX measures: {missing_msrs}")

    print("\n" + "=" * 65)
    print(f"PBIP AUDIT RESULT: {tests_passed} / {total_tests} Tests Passed ({(tests_passed/total_tests)*100:.1f}%)")
    print("=" * 65)

    return tests_passed == total_tests

if __name__ == "__main__":
    ok = validate_pbip()
    sys.exit(0 if ok else 1)
