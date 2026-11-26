# Module 14: Complete Project Glossary & Technical Terminology

> **File Reference:** `docs/study_materials/14_COMPLETE_PROJECT_GLOSSARY.md`  
> **Audience:** Data Analysts, Product Analysts, BI Engineers

---

### ACID Properties
- **Definition**: Atomicity, Consistency, Isolation, Durability.
- **Simple Meaning**: Guarantees that database transactions are processed reliably and data never gets corrupted mid-way.
- **Where It Appears**: MySQL InnoDB storage engine (`sql/02_create_tables.sql`).
- **Example**: If a subscription insert fails halfway, MySQL rolls back the entire statement so no orphaned record is created.

---

### ARPU (Average Revenue Per User)
- **Definition**: $\frac{\text{Total Monthly Recurring Revenue}}{\text{Active Paid Subscribers}}$.
- **Simple Meaning**: How much money, on average, each paying subscriber contributes per month.
- **Where It Appears**: `sql/08_subscription_analysis.sql`, DAX `[ARPU]`.
- **StreamScope Value**: **$12.29** ($70,261.77 / 5,717).

---

### Cohort Retention
- **Definition**: Tracking the percentage of users acquired in a specific time period (e.g., January 2025) who remain active across subsequent months (M0, M1, M2... M6).
- **Simple Meaning**: Measuring whether newer customers stick around longer than older customers.
- **Where It Appears**: `sql/10_cohort_retention.sql`.

---

### Common Table Expression (CTE)
- **Definition**: A temporary named result set defined within the execution scope of a single SQL statement using the `WITH` clause.
- **Simple Meaning**: Breaking down a huge, complex SQL query into neat, readable steps.
- **Where It Appears**: Implemented in scripts `06`, `07`, `08`, `09`, `10`, `11`, `13`.

---

### DAU / MAU Stickiness Ratio
- **Definition**: $\frac{\text{Average Daily Active Users}}{\text{Monthly Active Users}} \times 100$.
- **Simple Meaning**: What percentage of your monthly audience visits the app on any given day.
- **Where It Appears**: `sql/06_user_engagement.sql`.
- **Significance**: Higher stickiness (> 20%) indicates strong daily habit formation.

---

### DENSE_RANK()
- **Definition**: An analytical window function that assigns a consecutive rank to each row within an ordered partition, with ties receiving the same rank and no rank numbers skipped.
- **Simple Meaning**: Ranks items (1st, 2nd, 2nd, 3rd) without skipping numbers.
- **Where It Appears**: `sql/07_content_analysis.sql` for top content ranking.

---

### Filter Context (DAX)
- **Definition**: The set of filters applied to the semantic model by visual slicers, visual axes, report filters, and `CALCULATE()` statements during DAX evaluation.
- **Simple Meaning**: The "lens" through which Power BI looks at the data when calculating a measure.
- **Where It Appears**: All 15 DAX measures in `powerbi/dax_measures.md`.

---

### LAG()
- **Definition**: A window function that fetches the value of an expression from a specified number of rows prior to the current row within the partition.
- **Simple Meaning**: Peeking at last month's number without joining the table to itself.
- **Where It Appears**: `sql/06_user_engagement.sql` for Month-over-Month growth.

---

### MRR (Monthly Recurring Revenue)
- **Definition**: The normalized monthly recurring income generated from active subscriptions.
- **Simple Meaning**: Guaranteed predictable subscription cash flow every month.
- **Where It Appears**: `sql/08_subscription_analysis.sql`, DAX `[Current MRR]`.
- **StreamScope Value**: **$70,261.77**.

---

### PBIR (Power BI Enhanced Report Format)
- **Definition**: Microsoft's modern folder-based report definition structure where pages and visuals are stored in human-readable JSON files.
- **Simple Meaning**: Making Power BI reports Git-friendly so multiple developers can collaborate without binary file merge conflicts.
- **Where It Appears**: `powerbi/StreamScope_Analytics.Report/definition/`.

---

### Referential Integrity
- **Definition**: A database rule ensuring that foreign keys must always point to an existing valid primary key in a parent table.
- **Simple Meaning**: You cannot have a subscription or viewing session for a user ID that doesn't exist.
- **Where It Appears**: Foreign key constraints in `sql/02_create_tables.sql`.

---

### Right-Censoring
- **Definition**: A condition in survival analysis where the final event of interest (e.g., cancellation) has not yet occurred for some users before the observation window ends.
- **Simple Meaning**: We don't know if a December subscriber will cancel in February because our data stops in January.
- **Where It Appears**: Addressed by the 30-day follow-up window (`FOLLOWUP_DATE = 2026-01-31`) in `scripts/generate_data.py`.

---

### ROW_NUMBER()
- **Definition**: A window function that assigns a unique, sequential integer to each row within a partition.
- **Simple Meaning**: Numbering rows 1, 2, 3... per user.
- **Where It Appears**: `sql/08_subscription_analysis.sql` to identify first-time subscribers (`sub_sequence = 1`) versus reactivations (`sub_sequence > 1`).

---

### Self-Join
- **Definition**: A join in which a table is joined with itself.
- **Simple Meaning**: Comparing a row in a table to other rows within the exact same table.
- **Where It Appears**: `sql/09_churn_analysis.sql` to compare a canceled subscription (`s1`) to a future subscription (`s2`) by the same user.

---

### Star Schema
- **Definition**: A dimensional data modeling pattern where fact tables containing numeric metrics are connected to multiple surrounding dimension tables containing attributes.
- **Simple Meaning**: A star-shaped database layout optimized for fast analytical reporting.
- **Where It Appears**: Power BI semantic model (`model.bim`).

---

### True Churn (30-Day Rule)
- **Definition**: A subscription cancellation where the user does not resume another paid subscription within 30 calendar days.
- **Simple Meaning**: Distinguishing permanent customer loss from temporary credit card rebill hiccups.
- **Where It Appears**: `sql/09_churn_analysis.sql`, `sql/13_create_views.sql`.

---

### VertiPaq Engine
- **Definition**: Power BI's proprietary in-memory columnar database engine.
- **Simple Meaning**: High-speed memory storage that compresses data by 10x and calculates aggregations in milliseconds.
- **Where It Appears**: Power BI Import Mode in `StreamScope_Analytics.pbip`.
