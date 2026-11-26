# Module 07: Power BI, DAX & Semantic Modeling Masterclass

> **File Reference:** `docs/study_materials/07_POWER_BI_AND_DAX.md`  
> **Source Directory:** `powerbi/` (`model.bim`, `definition/pages/`, `dax_measures.md`)  
> **Audience:** Power BI Developers, BI Analysts, Analytics Engineers

---

## 1. Power BI Core Architecture Concepts

### 1.1 What is Power BI Desktop & Modern PBIP / PBIR?
- **Power BI Desktop**: An enterprise business intelligence application combining data preparation (Power Query), semantic modeling (VertiPaq engine), analytical modeling (DAX), and data visualization.
- **PBIP (Power BI Project)**: Microsoft's Git-friendly, open developer format. Instead of saving a black-box binary `.pbix` file, PBIP saves the report and semantic model as human-readable JSON, TMDL, and BIM files.
- **PBIR (Power BI Enhanced Report Format)**: Modern folder-based report definition format where each page and visual is stored in individual JSON files (`definition/pages/<PageName>/visuals/<VisualName>/visual.json`), enabling true multi-developer Git branching and code reviews.
- **TMDL / BIM**: Tabular Model Definition Language and TMSL (`model.bim`) specifying table schemas, relationships, data partitions, and DAX measures.

### 1.2 Import Mode vs. DirectQuery: Why Import Mode Was Chosen
| Feature | Import Mode (StreamScope's Choice) | DirectQuery Mode |
|---|---|---|
| **Data Storage** | Data is compressed and loaded into memory (RAM) via the VertiPaq engine. | Data remains in MySQL; queries are translated to SQL on every visual click. |
| **Performance** | **Instantaneous (< 50 ms)** cross-filtering and measure calculations. | Dependent on network latency and MySQL database indexing performance. |
| **DAX Capabilities** | Full, unrestricted DAX functionality (time intelligence, iterative iterators). | Restricted DAX subset; many functions cannot be folded into native SQL. |
| **Verdict** | **Best for analytical reporting** across 500K records. | Better for multi-terabyte tables requiring real-time sub-second updates. |

---

## 2. Semantic Model: Tables, Cardinality & Relationships

The StreamScope semantic model connects 10 tables using a **Star Schema** architecture with strict referential integrity:

```
[ FactSubscriptions ]       (N:1) ---> [ DimUsers ] (user_id)
[ FactSubscriptions ]       (N:1) ---> [ DimPlans ] (plan_id)
[ FactViewingSessions ]     (N:1) ---> [ DimUsers ] (user_id)
[ FactViewingSessions ]     (N:1) ---> [ DimContent ] (content_id)
[ ChurnByDimension ]        (N:1) ---> [ DimUsers ] (user_id)
[ UserSegments ]            (1:1) <--> [ DimUsers ] (user_id)  [Both Directions]
```

### Critical Modeling Rules Applied:
1. **Active Relationships**: All 6 relationships are set to `isActive: true`.
2. **Cardinality**: Many-to-One (`fromCardinality: "many"`, `toCardinality: "one"`) ensures filter context flows smoothly from dimensions (`DimUsers`, `DimPlans`, `DimContent`) down to fact tables (`FactSubscriptions`, `FactViewingSessions`).
3. **Bi-Directional Exception (`rel_segments_users`)**: `UserSegments` has a 1:1 relationship with `DimUsers` and uses `bothDirections` cross-filtering so filtering by behavioral segment automatically slices user demographics and viewing sessions.

---

## 3. Row Context vs. Filter Context: The Core of DAX

To master DAX in an interview, you must clearly distinguish these two contexts:

1. **Row Context**: Exists during calculated columns or iterator functions (`SUMX`, `AVERAGEX`). It evaluates row-by-row on the current record.
2. **Filter Context**: The set of active filters applied to the model by visual axes, slicers, page filters, and `CALCULATE()` statements.
   - *Example*: In a card showing `[Active Paid Subscribers]`, the filter context is empty (evaluates to 5,717). When placed in a bar chart sliced by `DimPlans[plan_name]`, the filter context for the "Standard HD" bar restricts the calculation to `plan_name = 'Standard HD'` (evaluating to 2,593).

---

## 4. Deep Dive into the 15 Production DAX Measures

All measures reside in the dedicated `_Measures` table.

---

### Measure 1: `[Total Registered Users]`
```dax
Total Registered Users = DISTINCTCOUNT(DimUsers[user_id])
```
- **Context**: Aggregates distinct top-of-funnel accounts.
- **SQL Equivalent**: `SELECT COUNT(DISTINCT user_id) FROM users;`
- **Result**: `10,000`

---

### Measure 2: `[Converted Paying Subscribers]`
```dax
Converted Paying Subscribers = 
CALCULATE(
    DISTINCTCOUNT(FactSubscriptions[user_id]),
    FactSubscriptions[status] IN {"Active", "Canceled"}
)
```
- **Evaluation**: Modifies filter context using `CALCULATE()` to count users whose subscriptions were successfully charged, excluding free registration drop-offs.
- **Result**: `7,728` (77.28% Conversion Rate).

---

### Measure 3: `[Conversion Rate %]`
```dax
Conversion Rate % = 
DIVIDE([Converted Paying Subscribers], [Total Registered Users], 0) * 100
```
- **Safety**: `DIVIDE(num, denom, alternate)` prevents `#DIV/0!` errors by returning 0 if the denominator is null or zero.
- **Result**: `77.3%`

---

### Measure 4: `[Active Paid Subscribers]`
```dax
Active Paid Subscribers = 
CALCULATE(
    DISTINCTCOUNT(FactSubscriptions[user_id]),
    FactSubscriptions[status] = "Active"
)
```
- **Result**: `5,717`

---

### Measure 5: `[Current MRR]`
```dax
Current MRR = 
CALCULATE(
    SUM(FactSubscriptions[monthly_fee]),
    FactSubscriptions[status] = "Active"
)
```
- **Purpose**: Tracks active recurring run-rate.
- **Result**: `$70,261.77`

---

### Measure 6: `[ARPU]`
```dax
ARPU = DIVIDE([Current MRR], [Active Paid Subscribers], 0)
```
- **Result**: `$12.29`

---

### Measure 7: `[Total Watch Hours]`
```dax
Total Watch Hours = DIVIDE(SUM(FactViewingSessions[watch_minutes]), 60, 0)
```
- **Result**: `126,608.5 hrs`

---

### Measure 8: `[Total Viewing Sessions]`
```dax
Total Viewing Sessions = COUNTROWS(FactViewingSessions)
```
- **Why `COUNTROWS()`**: Faster than `COUNT(column)` because it scans metadata without evaluating column nullability.
- **Result**: `121,801`

---

### Measure 9: `[Monthly Active Viewers (MAU)]`
```dax
Monthly Active Viewers (MAU) = DISTINCTCOUNT(FactViewingSessions[user_id])
```
- **Result**: Varies dynamically depending on date/month slicers (platform-wide distinct: ~10,000).

---

### Measure 10: `[Platform Completion Rate %]`
```dax
Platform Completion Rate % = AVERAGE(FactViewingSessions[completion_percentage])
```
- **Result**: `76.34%`

---

### Measure 11: `[Average Watch Time Per Viewer]`
```dax
Average Watch Time Per Viewer = 
DIVIDE(SUM(FactViewingSessions[watch_minutes]), [Monthly Active Viewers (MAU)], 0)
```
- **Purpose**: Computes average minutes streamed per active user.

---

### Measure 12: `[True Churned Subscribers]`
```dax
True Churned Subscribers = 
CALCULATE(
    DISTINCTCOUNT(ChurnByDimension[user_id]),
    ChurnByDimension[is_true_churn] = 1
)
```
- **Logic**: Filters for genuine 30-day cancellations.
- **Result**: `2,011`

---

### Measure 13: `[Monthly Churn Rate %]`
```dax
Monthly Churn Rate % = 
DIVIDE([True Churned Subscribers], [Active Paid Subscribers], 0) * 100
```
- **Result**: ~2.8% – 3.4% across calendar months.

---

### Measure 14: `[Subscriber Retention Rate %]`
```dax
Subscriber Retention Rate % = 
IF(NOT(ISBLANK([Monthly Churn Rate %])), 100 - [Monthly Churn Rate %], BLANK())
```
- **Result**: ~97.2%

---

### Measure 15: `[Reactivated Subscribers]`
```dax
Reactivated Subscribers = 
CALCULATE(
    DISTINCTCOUNT(ChurnByDimension[user_id]),
    ChurnByDimension[is_reactivated] = 1
)
```
- **Result**: `268` subscribers who returned after >30 days.

---

## 5. Walkthrough of the Three Report Pages

```
+-----------------------------------------------------------------------------------+
| PAGE 1: EXECUTIVE OVERVIEW                                                        |
| [Total Users: 10K] [Active Subs: 5.7K] [MAU: ~5.2K] [Hours: 126.6K] [MRR: $70.3K] |
| --------------------------------------------------------------------------------- |
| [ Line: Monthly Active Viewers (MAU) Trend ]   [ Line: Monthly MRR Revenue Trend ]|
| --------------------------------------------------------------------------------- |
| [ Donut: Plan Distribution ]  [ Bar: New Signups MoM ] [ Bar: Users by Channel ] |
+-----------------------------------------------------------------------------------+
| PAGE 2: CONTENT & ENGAGEMENT                                                      |
| [ Slicer: Genre Dropdown (Sci-Fi, Action, Drama, Comedy, Thriller, Doc...)       ]|
| --------------------------------------------------------------------------------- |
| [ Horiz Bar: Top 10 Titles by Watch Hours ]   [ Col Chart: Genre-wise Hours ]    |
| --------------------------------------------------------------------------------- |
| [ Donut: Device Share ] [ Col: Avg Completion % by Genre ] [ Col: Movie vs Series]|
+-----------------------------------------------------------------------------------+
| PAGE 3: RETENTION & CHURN                                                         |
| --------------------------------------------------------------------------------- |
| [ Col: True Churn by Channel ]             [ Col: True Churn by Plan Tier ]       |
| --------------------------------------------------------------------------------- |
| [ Line: Monthly Churn Loss ($ MRR) ] [ Pie: Reasons ] [ Bar: Engagement Segments ]|
+-----------------------------------------------------------------------------------+
```

### Visual Specifications:
1. **Executive Cards**: Six single-metric cards providing instant operational KPI visibility.
2. **Top Content Horizontal Bar Chart (`chart_top_content`)**: Ranks titles by total streamed hours; horizontal orientation ensures long title names (*"Chronicles of Aethelgard"*) remain readable without truncation.
3. **Cancellation Reasons Pie Chart (`chart_reasons`)**: Visualizes stated exit friction (32.4% "Price too high", 24.1% "Lack of content").
4. **Engagement Segments Column Chart (`chart_segments`)**: Visualizes user counts across the 4 behavioral tiers, confirming that 21.8% of users drive 55% of all streaming hours.
