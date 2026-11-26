# Module 08: Technical Decisions, Trade-Offs & Architectural Scalability

> **File Reference:** `docs/study_materials/08_TECHNICAL_DECISIONS_AND_TRADEOFFS.md`  
> **Audience:** Senior Data Analysts, Analytics Engineers, Hiring Managers

---

## 1. Master Architectural Decision Matrix

Every engineering decision involves trade-offs. An exceptional analyst justifies their choices by articulating **why alternatives were rejected** and **under what future conditions they would become preferable**:

| Decision Domain | Implemented Choice | Why Chosen? | Alternative Considered | Why Alternative Was Less Suitable Here | When Alternative Becomes Superior |
|---|---|---|---|---|---|
| **Programming Language** | **Python 3.14 (Standard Libs)** | Zero external dependencies; native datetime and pseudo-random seed determinism. | **R or Julia** | Slower adoption across cross-functional engineering teams; weaker data warehousing integrations. | If doing pure econometric modeling or advanced biostatistical survival analysis. |
| **Relational Database** | **MySQL 8.0 (InnoDB)** | ACID compliance, native window functions, ubiquitous enterprise support, low local resource footprint. | **MongoDB (NoSQL Document Store)** | Lacks native joins and relational integrity; difficult to guarantee non-overlapping subscriptions. | When ingesting unstructured semi-structured JSON telemetry from millions of smart TVs. |
| **Data Architecture** | **Star Schema (Facts & Dims)** | Decouples dimensions (Users, Plans, Content) from facts (Sessions, Events, Subscriptions); optimizes Power BI VertiPaq. | **Single Wide Table (One Big Table / OBT)** | High data redundancy; updating a plan price requires updating millions of historical rows (update anomalies). | In cloud MPP warehouses (BigQuery/ClickHouse) where columnar storage neutralizes repetition. |
| **Analytical Layer** | **SQL Views (`13_create_views.sql`)** | Encapsulates complex logic (30-day churn rule) centrally so all downstream BI tools receive identical data. | **Ad-Hoc SQL inside Power BI / Power Query** | Logic is trapped inside PBIX; changes cannot be tested in MySQL or shared with other tools. | When rapid prototyping without database write permissions. |
| **Dataset Scale** | **10,000 Users / 548,020 Rows** | Statistically significant sample size; executes sub-second on standard local laptops; instant Git commits. | **10 Million Rows** | Bloats local repositories; requires cloud infrastructure; slows local validation cycles. | In enterprise production testing where distributed shuffle performance must be benchmarked. |
| **Observation Window** | **2025 Calendar + 30-Day Follow-Up** | 12 full months for seasonal MoM comparisons; follow-up window prevents right-censoring of December cancellations. | **Rolling 90-Day Window** | Fails to capture full annual subscription renewals and long-term cohort decay. | When analyzing daily operational fire-drills or short-term marketing sprint tests. |
| **Churn Rule** | **30-Day True Churn Rule** | Excludes temporary credit card failures and fast rebills (< 30 days) from inflating churn rates. | **Immediate Cancellation Churn** | Inflates churn by 15–20% by counting temporary billing interruptions as permanent losses. | If analyzing immediate app uninstalls or subscription cancellation clicks. |
| **BI Tool** | **Power BI Desktop (PBIP/PBIR)** | Modern Git integration (text-based JSON files); lightning-fast in-memory VertiPaq engine; expressive DAX. | **Tableau Desktop** | Proprietary XML workbook format; merge conflicts in Git are notoriously difficult to resolve. | In organizations with pre-existing Tableau Server investments or advanced geospatial mapping needs. |
| **Data Ingestion Mode** | **Power BI Import Mode** | Delivers < 50ms interactive cross-filtering; supports full DAX calculation libraries. | **DirectQuery Mode** | Sluggish dashboard interaction; queries get translated to SQL on every click; limited DAX support. | When the dataset exceeds 50 GB and live, second-by-second data updates are legally mandated. |

---

## 2. Scalability Architecture: How Would the System Evolve?

An interviewer will frequently ask: *"Your project works great for 10,000 users. How would you redesign this architecture for 100,000 users? What about 10 million users?"*

Use this progressive 3-tier scaling blueprint to demonstrate senior architectural maturity:

```
[ Tier 1: Current StreamScope (10K Users) ]
Python Generator -> MySQL 8.0 (Single Node) -> SQL Views -> Power BI Desktop (Import Mode)

[ Tier 2: Mid-Market Scale (100K - 1M Users) ]
PostgreSQL / AWS RDS -> dbt (Data Build Tool) -> Airflow DAGs -> Power BI Service (Incremental Refresh)

[ Tier 3: Enterprise Netflix Scale (10M - 100M+ Users) ]
Kafka Stream -> Apache Flink / Spark Streaming -> Snowflake / Delta Lake -> Semantic Layer (Cube/Looker) -> Power BI (Aggregations + DirectLake)
```

### 2.1 Evolution to 100,000 Users (Scale Factor: 10x)
- **Bottleneck**: MySQL `app_events` table reaches ~4.5 million rows; full-table joins slow down to 4–8 seconds.
- **Architectural Changes**:
  1. **dbt (Data Build Tool)**: Replace manual SQL script execution with a dbt project. Materialize `vw_pbi_monthly_performance` and `vw_pbi_content_dashboard` as physical summary tables (nightly batch transformations) rather than dynamic views.
  2. **Table Partitioning**: Implement native MySQL RANGE partitioning on `viewing_sessions` by `started_at` year/month.
  3. **Power BI Incremental Refresh**: Configure Power BI to refresh only the most recent month of viewing data, archiving the prior 11 months in VertiPaq memory.

### 2.2 Evolution to 10 Million Users (Scale Factor: 1,000x)
- **Bottleneck**: Single-node RDBMS fails under write concurrency; streaming telemetry exceeds 500 million events per month.
- **Architectural Changes**:
  1. **Event Streaming**: Ingest user clickstream events via **Apache Kafka** or **AWS Kinesis**.
  2. **Cloud MPP Lakehouse**: Transition from MySQL to **Snowflake, Databricks Delta Lake, or Google BigQuery**. Columnar storage enables petabyte-scale aggregations across billions of playback timestamps in seconds.
  3. **Orchestration**: Deploy **Apache Airflow** or **Prefect** to automate daily DAG pipelines with automated SLA monitoring and alerting.
  4. **Power BI Composite Models (DirectLake / Hybrid)**: High-level executive KPIs query in-memory aggregated tables, while granular session-level drill-throughs query Snowflake directly via DirectQuery or Microsoft Fabric DirectLake.
