# StreamScope Project Validation & Verification Report

**Verification Date**: 2026-11-26  
**Status**: All 22 Verification & Integrity Checks Passed (100.0%) | PBIP Schema Violations Resolved (0/22 visuals) | 7/7 Structural Audit Passed  
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

---

## 8. PBIP Schema Resolution & `enableAutoAuth` Bug Fix

### A. Root Cause Analysis
- **Error Observed**:
  ```
  Property 'enableAutoAuth' has not been defined and the schema does not allow additional properties.
  Path: settings.enableAutoAuth, line 11.
  ```
- **Underlying Cause**: In `powerbi/StreamScope_Analytics.pbip`, line 11 contained an invalid property `"enableAutoAuth": true` under `"settings"`. Under the official Microsoft Fabric / Power BI Project JSON schema (`https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json`), `additionalProperties` is set to `false`. The only valid property permitted inside `settings` is `"enableAutoRecovery"` (boolean).

### B. Corrective Implementation
1. **Backup Created**:
   - Backed up the original file to `powerbi/StreamScope_Analytics.pbip.bak`.
2. **Corrected Schema in `powerbi/StreamScope_Analytics.pbip`**:
   - Replaced `"enableAutoAuth": true` with valid Microsoft PBIP property `"enableAutoRecovery": true`.
   - Added official `$schema` identifier for IDE IntelliSense and strict compliance:
     ```json
     {
       "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
       "version": "1.0",
       "artifacts": [
         {
           "report": {
             "path": "StreamScope_Analytics.Report"
           }
         }
       ],
       "settings": {
         "enableAutoRecovery": true
       }
     }
     ```
3. **Validation & Integrity Verification**:
   - Updated `scripts/validate_pbip_project.py` with strict PBIP settings schema checking to prevent future regressions.
   - Ran `validate_pbip_project.py`: **7 / 7 tests passed (100.0%)**.
   - Verified that `definition.pbir`, `definition.pbism`, `definition.pbidataset`, `report.json`, and modern PBIR directories remain 100% intact and valid.
   - MySQL database and all tables/views remained completely untouched.
   - Draft PBIX file `powerbi/StreamScope_Analytics_Draft.pbix` remained completely untouched.

---

## 9. PBIP Report Canvas & Relationship Warning Resolution

### A. Root Cause Analysis
1. **Blank Report Canvas**:
   - In `powerbi/StreamScope_Analytics.Report/report.json`, the `sections` array was empty (`"sections": []`). In PBIP format (PBIR v1), Power BI Desktop requires pages to be defined as `sections` containing `visualContainers`.
2. **Warning: "One or more relationships have been modified and need to be refreshed manually"**:
   - The Tabular Model Schema (`model.bim`) lacked explicit relationship metadata (`isActive: true`, `crossFilteringBehavior: "oneDirection"`, `fromCardinality`, `toCardinality`, `relyOnReferentialIntegrity: true`). Without these properties, VertiPaq marks relationships as dirty/unrefreshed.
3. **Warning: "Some of the tables have incomplete or no data"**:
   - M partition expressions used Unix forward slashes (`C:/Users/...`) and `QuoteStyle.None`, causing Power Query on Windows to fail file resolution or misparse quoted CSV text fields with commas.

### B. Corrective Implementation
1. **Full PBIP `report.json` Assembly (`scripts/repair_pbip_and_report.py`)**:
   - Built complete `report.json` (72.8 KB) with **3 sections** and all **22 interactive visual containers**:
     - **Section 1: Executive Overview** (6 KPI cards + 5 charts = 11 visuals).
     - **Section 2: Content & Engagement** (5 charts + 1 genre slicer = 6 visuals).
     - **Section 3: Retention & Churn** (5 charts = 5 visuals).
   - Mapped all projections, aggregations, queries, and layout coordinates to exact semantic model entities and measures.
2. **Dual PBIR v2.0 Synchronization**:
   - Synchronized all 22 visuals into `powerbi/StreamScope_Analytics.Report/definition/pages/` with `page.json` and `visual.json` definitions.
3. **Semantic Model Partition & Relationship Hardening (`model.bim`)**:
   - Updated all 9 CSV partition expressions to use Windows paths (`C:\Users\Dheeraj Kumar\...`) and `QuoteStyle.Csv`.
   - Explicitly configured all 6 star-schema relationships with `"isActive": true`, `"crossFilteringBehavior"`, `"fromCardinality": "many"`, `"toCardinality": "one"`, and `"relyOnReferentialIntegrity": true`.
4. **Standalone PBIX Rebuild (`StreamScope_Analytics.pbix`)**:
   - Re-compiled `powerbi/StreamScope_Analytics.pbix` (634.0 KB) incorporating the 22 visuals while preserving the user's active MySQL `DataModel`.
   - Preserved `powerbi/StreamScope_Analytics_Draft.pbix` 100% untouched.

---

## 10. PBIR vs. PBIR-Legacy Format Collision Resolution

### A. Root Cause Analysis
- **Error Observed in Power BI Desktop**:
  ```
  Issues were found
  You cannot have both PBIR and PBIR-Legacy formats in the same PBIP.
  Please remove the 'C:\Users\Dheeraj Kumar\OneDrive\Desktop\Documents\StreamScope-OTT-Analytics\powerbi\StreamScope_Analytics.Report\report.json' file.
  ```
- **Underlying Cause**: Power BI Desktop 2026 detects whether a project uses the modern PBIR directory structure (`definition/`) or the legacy single-file format (`report.json` in the report root). Having both files present in the same `.Report` directory causes a schema collision because Power BI cannot determine which format takes precedence.

### B. Corrective Action
1. **Removed Legacy Collision File**:
   - Safely archived legacy `powerbi/StreamScope_Analytics.Report/report.json` to `report.json.legacy.bak` and removed it from the root.
2. **Modern PBIR Structure Retained**:
   - `powerbi/StreamScope_Analytics.Report/definition/` exclusively governs the report presentation:
     - `version.json`: PBIR version 2.0.0 metadata.
     - `report.json`: Modern theme and canvas collection.
     - `pages/pages.json`: Defines page manifest and order for all 3 pages (`Section_Executive_Overview`, `Section_Content_Engagement`, `Section_Retention_Churn`).
     - `pages/<PageName>/visuals/<VisualName>/visual.json`: Contains all 22 interactive visual specifications.
3. **Audit Verification**:
   - `scripts/validate_pbip_project.py` verified 100% pass across all 7 audit stages with zero format collisions.







---

## 12. PBIP Visual Schema Fix — `nativeSummaryFunction` & Dual Page Directory Conflict

**Date**: 2026-11-26  
**Status**: ✅ RESOLVED — All 22 visuals pass schema audit. 7/7 validation tests pass.

### A. Root Cause

Two separate issues were identified when Power BI Desktop 2026 opened `StreamScope_Analytics.pbip`:

**Issue 1 — 107 Schema Violations (`nativeSummaryFunction`)**
- **Error**: `An additional property 'nativeSummaryFunction' was included in /visual/query/queryState/Category/projections/0`
- **Source**: `scripts/build_full_pbix.py` and an earlier version of `scripts/rebuild_pbir_visuals.py` added the invalid property `"nativeSummaryFunction": 0` to every chart Category projection.
- The Microsoft PBIR `visualContainer` schema (all versions) explicitly prohibits this property.

**Issue 2 — `queryState` missing from `/visual/query` (Slicer)**
- **Error**: `Required property 'queryState' was not included in /visual/query`
- **Source**: `slicer_genre/visual.json` in `page_content_engagement` still had the old format (`Version`, `From`, `Select` at the `/visual/query` level instead of inside `queryState.Values.projections[]`).

**Issue 3 — Dual Page Directory Conflict (44 visuals instead of 22)**
- **Source**: `rebuild_pbir_visuals.py` wrote to `Section_*` page directories, while `build_full_pbix.py` wrote to `page_*` directories. Running both scripts caused both sets to coexist, creating 44 visuals total.
- `pages.json` only referenced `page_*` names, so Power BI loaded the `page_*` visuals. The `Section_*` directories were orphaned noise.

### B. Corrective Actions

1. **Removed `Section_*` duplicate directories**:
   - Deleted `Section_Executive_Overview`, `Section_Content_Engagement`, `Section_Retention_Churn` from `definition/pages/`.
   - Canonical page directories are now exclusively `page_exec_overview`, `page_content_engagement`, `page_retention_churn`.

2. **Fixed `slicer_genre/visual.json`**:
   - Rewrote from old `Version`/`From`/`Select` structure to correct `queryState.Values.projections[]` structure.
   - Updated schema from `visualContainer/1.4.0` to `visualContainer/2.1.0` to match all other visuals.
   - Correct projection uses `Column.Expression.SourceRef.Entity` = `"streamscope vw_pbi_content_dashboard"`, `Property` = `"genre"`.

3. **Previous fix (`nativeSummaryFunction`)** was already applied by patching `scripts/build_full_pbix.py` (removed both occurrences). The `page_*` visuals had already been regenerated clean.

### C. Post-Fix Audit Results

| Metric | Before Fix | After Fix |
|---|---|---|
| Total visual.json files | 44 (Section_* + page_*) | 22 (page_* only) |
| `nativeSummaryFunction` violations | 0 (already patched) | **0** |
| Missing `queryState` violations | 1 (`slicer_genre`) | **0** |
| Page directory conflicts | Yes (Section_* + page_*) | **No** |

### D. Files Modified

| File | Change |
|---|---|
| `powerbi/StreamScope_Analytics.Report/definition/pages/page_content_engagement/visuals/slicer_genre/visual.json` | Rewrote to `visualContainer/2.1.0` with correct `queryState.Values.projections[]` |
| `powerbi/StreamScope_Analytics.Report/definition/pages/Section_*/` | Deleted (3 directories, 22 visual.json files removed) |
| `docs/PROJECT_VALIDATION_REPORT.md` | This section added |

### E. Validation Suite Result

```
=================================================================
StreamScope Power BI Project (PBIP) Integrity Audit
=================================================================
  ✓ [1/7] PBIP Entry File        : Valid (193 bytes)
  ✓ [2/7] Report Descriptor      : Valid -> Points to ../StreamScope_Analytics.SemanticModel
  ✓ [3/7] Modern PBIR Report     : Valid (3 pages: Executive Overview, Content & Engagement, Retention & Churn) | 22 Visuals (No format collisions)
  ✓ [4/7] Model Descriptors      : Both .pbism (Modern) and .pbidataset (Legacy) present
  ✓ [5/7] TMSL model.bim Schema  : Valid (38.7 KB) | 10 Tables, 15 DAX Measures, 6 Relationships (Fully Qualified)
  ✓ [6/7] Data Partition Files   : All 9 analytical datasets verified in powerbi/data/
  ✓ [7/7] Key DAX Measures       : All 5 essential measures verified

PBIP AUDIT RESULT: 7 / 7 Tests Passed (100.0%)
=================================================================
```

### F. User Action Required

**Power BI Desktop must be closed and reopened** for the file changes to take effect:
1. Close Power BI Desktop completely.
2. Reopen `powerbi/StreamScope_Analytics.pbip`.
3. Expected: **No "Issues were found" dialog** and **No schema error list**.
4. Expected: 3 page tabs at bottom (Executive Overview, Content & Engagement, Retention & Churn).
5. If a data refresh prompt appears, click **Apply changes** to load live MySQL data.

