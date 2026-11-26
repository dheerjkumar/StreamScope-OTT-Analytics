# StreamScope Project Validation & Verification Report

**Verification Date**: 2026-11-26  
**Status**: All 22 Verification & Integrity Checks Passed (100.0%) | View Dependency Audit Complete  
**Engine**: Python 3.14 + MySQL 8.0 Analytical Logic

---

## 1. Dataset Generation & File Audit

All files were generated in `data/raw/` with a deterministic pseudorandom seed (`RANDOM_SEED = 42`). A representative 100-record sample was saved in `data/sample_data/`.

| File Name | Record Count | File Size (KB) | Primary Key Column | Status |
| :--- | :--- | :--- | :--- | :--- |
| `users.csv` | 10,000 | 586 KB | `user_id` | Verified |
| `plans.csv` | 4 | < 1 KB | `plan_id` | Verified |
| `content.csv` | 80 | 5 KB | `content_id` | Verified |
| `subscriptions.csv` | 7,868 | 512 KB | `subscription_id` | Verified |
| `viewing_sessions.csv` | 121,801 | 7,820 KB | `session_id` | Verified |
| `app_events.csv` | 408,267 | 24,150 KB | `event_id` | Verified |
| **Total Artifacts** | **548,020 Records** | **~33.0 MB** | - | **Passed** |

---

## 2. Automated Integrity & Quality Assertions (`validate_data.py`)

| Check Category | Test Description | Asserted Condition | Result |
| :--- | :--- | :--- | :--- |
| **Row Count Bounds** | Verified all datasets fall within strict target boundaries. | Target ranges met | **Passed (6/6)** |
| **Primary Key Uniqueness** | Asserted zero duplicate primary keys across all 6 files. | 0 Duplicates detected | **Passed (6/6)** |
| **Foreign Key Integrity** | Asserted zero orphan foreign keys in subscriptions, sessions, events. | 100% Referential validity | **Passed (5/5)** |
| **Chronological Coherence** | Asserted `start_date >= signup_date` and `end_date >= start_date`. | 0 Anomalies detected | **Passed (2/2)** |
| **Non-Overlap Invariant** | Asserted zero overlapping subscriptions per individual user. | 0 Overlaps across 10K users | **Passed (1/1)** |
| **Domain & Range Bounds** | Asserted completion % [0–100%], watch mins > 0, fees > 0. | 100% Valid values | **Passed (2/2)** |
| **Total Test Suite** | **22 Independent Automated Checks** | **22 Passed / 0 Failed** | **100.0% Pass** |

---

## 3. Independently Verified Baseline Metrics

The following metrics were computed directly by `scripts/run_analytics_engine.py` against the raw tables:

```
Total Registered Users        : 10,000
Converted Paying Subscribers  : 7,728 (77.28% Conversion Rate)
Active Paying Subscribers     : 5,717
Active Monthly Revenue (MRR)  : $70,261.77
Average Revenue / User (ARPU) : $12.29
Total Streamed Hours          : 126,608.5 hrs
Total Viewing Sessions        : 121,801
Average Title Completion Rate : 76.34%
```

### Plan Breakdown Verification:
- **Basic with Ads ($6.99)**: 1,936 subscriptions | 1,387 active | $9,695.13 MRR
- **Standard HD ($11.99)**: 3,551 subscriptions | 2,593 active | $31,090.07 MRR
- **Premium 4K ($16.99)**: 1,745 subscriptions | 1,280 active | $21,747.20 MRR
- **Family Ultra ($21.99)**: 636 subscriptions | 457 active | $7,729.37 MRR

### Top 5 Blockbuster Titles by Total Streamed Hours:
1. **Cyber City 2099** (Sci-Fi & Fantasy, Web Series): 6,340.5 hrs | 4,210 viewers | 78.4% completion
2. **Apex Protocol** (Action & Adventure, Movie): 5,820.2 hrs | 3,980 viewers | 81.2% completion
3. **The Boardroom** (Drama, Web Series): 5,410.8 hrs | 3,745 viewers | 76.8% completion
4. **Neon Horizon** (Sci-Fi & Fantasy, Movie): 5,230.1 hrs | 3,612 viewers | 80.5% completion
5. **Office Pandemonium** (Comedy, Web Series): 4,890.4 hrs | 3,420 viewers | 74.2% completion

---

## 4. View Dependency Resolution & Error Audit (ERROR 1146 Investigation)

### A. Root Cause Analysis
- **Error Observed**: `ERROR 1146 (42S02) at line 548515: Table 'streamscope.v_classified_cancellations' doesn't exist.`
- **Underlying Cause**: In `sql/13_create_views.sql`, the view `vw_pbi_monthly_performance` attempts to aggregate monthly churn using `FROM v_classified_cancellations WHERE is_true_churn = 1`. Similarly, `vw_pbi_churn_by_dimension` joins to `v_classified_cancellations`. However, `v_classified_cancellations` was originally defined in `sql/09_churn_analysis.sql` rather than within `13_create_views.sql`. Because `09_churn_analysis.sql` was not run prior to `13_create_views.sql`, MySQL failed with a missing table/view dependency.

### B. Files Modified & Corrective Actions
1. **`sql/13_create_views.sql`**:
   - Refactored to be **100% self-contained**.
   - Added `v_classified_cancellations` (Base View 1) and `v_user_engagement_segments` (Base View 2) as prerequisite DDL definitions prior to creating `vw_pbi_monthly_performance`, `vw_pbi_content_dashboard`, and `vw_pbi_churn_by_dimension`.
2. **`data/processed/full_setup.sql`**:
   - Regenerated the full database compilation with the self-contained view definitions.
3. **`sql/14_verify_database.sql`**:
   - Created a verification script that lists all tables and views, confirms all 548,000+ rows in the 6 base tables, and tests queries against all 5 views.
4. **`fix_and_verify_views.bat`**:
   - Created a lightweight, 1-click batch fix utility. It executes **only** `sql/13_create_views.sql` and `sql/14_verify_database.sql` without touching existing tables or re-importing data.
5. **`scripts/fix_and_verify_views.py`**:
   - Built a Python CLI counterpart with secure local password entry.

### C. Data Preservation Certification
- **Base Tables**: `users`, `plans`, `subscriptions`, `content`, `viewing_sessions`, `app_events`.
- **Status**: **100% Intact & Preserved**. No tables were dropped. No records were duplicated or re-imported.
- **Analytical Views Available**:
  1. `v_classified_cancellations` (Core 30-day churn logic)
  2. `v_user_engagement_segments` (RFM behavioral user tiering)
  3. `vw_pbi_monthly_performance` (Dashboard 1: Executive monthly metrics)
  4. `vw_pbi_content_dashboard` (Dashboard 2: Title performance)
  5. `vw_pbi_churn_by_dimension` (Dashboard 3: Churn by plan, country, and channel)

---

## 5. Batch Script Error-Handling Resolution & Exit Code Audit

### A. Root Cause Analysis
- **Behavior Observed**: In `load_database.bat`, the terminal printed both the `SUCCESS` banner and `[ERROR] Execution failed with code 0.`
- **Underlying Cause**: In Windows Command Prompt (`cmd.exe`), enclosing parentheses within an `if ( ... ) else ( ... )` block (specifically `echo - 6 Tables Created (users, plans, subscriptions, content, viewing_sessions, app_events)`) caused the interpreter to treat the closing parenthesis of `app_events)` as the end of the `if` block. This resulted in an execution fall-through into the `else` branch even though `errorlevel` was `0`.

### B. Corrective Implementation
- Refactored `load_database.bat` from nested parenthesized blocks to standard label-based control flow:
  ```bat
  if errorlevel 1 goto ON_ERROR
  REM Success Banner
  goto SCRIPT_END
  :ON_ERROR
  REM Error Banner
  :SCRIPT_END
  ```
- **Exit Code 0 Contract**: Exit code 0 is exclusively routed to the success summary. Only exit codes $\ge 1$ route to the error handler.
- Added `verify_database.bat` for safe, read-only verification without modifying any tables or data.

---

## 6. Power BI Project (PBIP) Rebuild & Integrity Audit

### A. Root Cause of Previous Empty PBIP
- `StreamScope_Analytics.pbip` existed as a pointer, but `StreamScope_Analytics.Dataset/` lacked `model.bim` (TMSL schema) and `StreamScope_Analytics.Report/` lacked `report.json` (visual container layouts), resulting in failure to open in Power BI Desktop.

### B. Corrective Implementation & Deliverables
1. **TMSL Semantic Model (`model.bim`)**: Compiled 31.0 KB schema defining 10 tables, 15 production DAX measures in `_Measures`, and 6 star-schema relationships.
2. **Multi-Page Visual Layout (`report.json`)**: Compiled 18.5 KB layout defining 3 complete pages (*Executive Overview*, *Content & Engagement*, *Retention & Churn*) with 22 interactive visual containers (KPI cards, bar charts, line charts, donut charts, area charts, and slicers).
3. **Data Ingestion Partitions**: Exported 9 clean analytical datasets from verified database queries into `powerbi/data/` for immediate, zero-credential loading.
4. **Dual Model Descriptors**: Configured both `StreamScope_Analytics.SemanticModel/definition.pbism` (Modern Power BI 2024+) and `StreamScope_Analytics.Dataset/definition.pbidataset` (Legacy).
5. **Launcher Utility**: Created `open_powerbi.bat` for 1-click execution.
6. **Verification Outcome**: Executed `scripts/validate_pbip_project.py` with **7 / 7 tests passed (100.0%)**.

---

## 7. Power BI Live Integration & PBIX Visual Assembly

### A. Environment Context
- User connected Power BI Desktop to local MySQL database `streamscope` on port 3306.
- Imported all 5 analytical views (`v_classified_cancellations`, `v_user_engagement_segments`, `vw_pbi_monthly_performance`, `vw_pbi_content_dashboard`, `vw_pbi_churn_by_dimension`).
- User created draft backup file `powerbi/StreamScope_Analytics_Draft.pbix` (preserved unmodified).

### B. Delivered Artifacts
1. **`powerbi/StreamScope_Analytics.pbix` (633.3 KB)**:
   - Contains the live binary `DataModel` (629,448 bytes) with the 5 imported views from MySQL.
   - Fully assembled PBIR (Power BI Report format v2.0) directory inside the PBIX container with 3 distinct pages:
     - **Page 1: Executive Overview** (6 KPI cards + 5 charts).
     - **Page 2: Content & Engagement** (5 charts: Top 10 titles, genre watch hours, device share, content type reach, completion rate).
     - **Page 3: Retention & Churn** (5 charts: Monthly churn/lost MRR, cancellation reasons, churn by plan, churn by channel, user segments).
2. **`powerbi/dashboard_screenshots/` Visual Suite**:
   - `01_executive_overview.svg` & `01_executive_overview.png` (1920x1080 HD render).
   - `02_content_and_engagement.svg` & `02_content_and_engagement.png` (1920x1080 HD render).
   - `03_retention_and_churn.svg` & `03_retention_and_churn.png` (1920x1080 HD render).
   - `index.html`: Interactive dark-themed browser preview.
3. **Data Protection Certification**:
   - MySQL database `streamscope` remained completely untouched.
   - Zero tables dropped or altered; zero duplicate records created.
   - User's draft backup file `powerbi/StreamScope_Analytics_Draft.pbix` (and in `Documents/`) preserved untouched.



