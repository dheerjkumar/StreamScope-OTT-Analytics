# Module 11: Master Project Numbers, Constants & Metric Cheat Sheet

> **File Reference:** `docs/study_materials/11_PROJECT_NUMBERS_AND_VALUES.md`  
> **Audience:** Data Analysts, Interview Candidates  
> **Purpose:** Comprehensive source of truth for every exact constant, parameter, and calculated metric in the repository.

---

## 1. Master Metric & Numerical Taxonomy Table

| Parameter / Metric | Exact Value | Where Defined? | Category | Business / Technical Explanation |
|---|---|---|---|---|
| **Total Platform Records** | `548,020` | `scripts/generate_data.py`, `data/raw/` | **Calculated Artifact** | Cumulative sum across all 6 generated tables: Users (10K) + Plans (4) + Content (80) + Subscriptions (7,868) + Sessions (121,801) + Events (408,267). |
| **Total Registered Users** | `10,000` | `scripts/generate_data.py:29` (`NUM_USERS`) | **Technical Configuration** | Sized to ensure statistical significance across demographic cohorts while allowing sub-second SQL queries locally. |
| **Subscription Plan Tiers** | `4 Tiers` | `scripts/generate_data.py:50` (`plans_data`) | **Business Definition** | Modeled after US streaming industry tiers: Basic w/ Ads ($6.99), Standard ($11.99), Premium ($16.99), Family ($21.99). |
| **Content Catalog Titles** | `80 Titles` | `scripts/generate_data.py:30` (`NUM_CONTENT`) | **Demonstration Assumption** | Balanced catalog of 10 titles across 8 genres (5 movies, 5 series each) for visual clarity in dashboard charts. |
| **Total Subscription Records** | `7,868` | `data/raw/subscriptions.csv` | **Simulated Transaction** | Covers initial signups, renewals, cancellations, and subsequent reactivations across 2025. |
| **Converted Paying Subscribers**| `7,728 (77.28%)` | `sql/05_user_acquisition.sql`, DAX | **Calculated Metric** | Unique users who purchased $\ge 1$ paid plan. ~22.7% of users registered but dropped off before paying. |
| **Active Paid Subscribers** | `5,717` | `sql/08_subscription_analysis.sql`, DAX | **Calculated Metric** | Paying subscribers with active billing status at the end of the 2025 observation window. |
| **Active Monthly Revenue (MRR)**| `$70,261.77` | `sql/08_subscription_analysis.sql`, DAX | **Calculated Financial** | Sum of `monthly_fee` across all 5,717 currently active subscriptions. |
| **Average Revenue / User (ARPU)**| `$12.29` | `sql/08_subscription_analysis.sql`, DAX | **Calculated Financial** | `Current MRR / Active Subscribers` ($70,261.77 / 5,717). |
| **Total Streamed Hours** | `126,608.5 hrs` | `sql/06_user_engagement.sql`, DAX | **Calculated Volume** | Total platform playback hours across 121,801 sessions. |
| **Total Viewing Sessions** | `121,801` | `data/raw/viewing_sessions.csv` | **Simulated Interaction** | Stream playback sessions initiated by users. |
| **Average Completion Rate** | `76.34%` | `sql/06_user_engagement.sql`, DAX | **Calculated Quality** | Average percentage of title duration watched per playback session. |
| **Total App Telemetry Events** | `408,267` | `data/raw/app_events.csv` | **Simulated Telemetry** | User in-app UI interactions (`app_open`, `search`, `content_click`, `pause`, `cancel_click`). |
| **Relational Database Tables** | `6 Tables` | `sql/02_create_tables.sql` | **Technical Architecture**| Normalized 3NF tables: `users`, `plans`, `content`, `subscriptions`, `viewing_sessions`, `app_events`. |
| **Analytical Reporting Views** | `5 Views` | `sql/13_create_views.sql` | **Analytical Engineering**| Encapsulates business logic: `v_classified_cancellations`, `v_user_engagement_segments`, `vw_pbi_*` (3 views). |
| **Power BI Semantic Tables** | `10 Tables` | `powerbi/.../model.bim` | **BI Data Modeling** | 6 relational tables + 3 analytical view tables + 1 `_Measures` table. |
| **Power BI DAX Measures** | `15 Measures` | `powerbi/dax_measures.md` | **BI Analytics** | Production DAX formulas calculating executive KPIs, conversions, churn, retention, and ARPU. |
| **Power BI Report Pages** | `3 Pages` | `powerbi/.../pages.json` | **BI Visual Delivery** | Executive Overview, Content & Engagement, Retention & Churn. |
| **Power BI Visualizations** | `22 Visuals` | `powerbi/.../visuals/` | **BI Visual Delivery** | 6 KPI cards, 2 line charts, 8 bar/column charts, 3 donut charts, 2 pie charts, 1 slicer. |
| **Random Seed** | `42` | `scripts/generate_data.py:22` | **Technical Configuration**| Fixed pseudorandom seed guaranteeing 100% deterministic reproducibility. |
| **Observation Window** | `2025-01-01` to `2025-12-31` | `scripts/generate_data.py:25` | **Business Definition** | 12 full calendar months for seasonal trends and annual reporting. |
| **Follow-up Grace Period** | `2026-01-31` | `scripts/generate_data.py:27` | **Analytical Design** | 30-day grace period preventing right-censoring bias on December cancellations. |
| **True Churn Threshold** | `30 Days` | `sql/09_churn_analysis.sql:39` | **Business Rule** | Gap threshold separating temporary payment lapses ($\le 30$ days) from permanent subscriber churn (> 30 days). |
| **Highly Engaged Cutoff** | `30 hrs & 20 sess`| `sql/11_customer_segmentation.sql` | **Analysis-Supported** | Identifies top 21.8% daily-habit "Power Streamers". |
| **Moderately Engaged Cutoff** | `10 hrs & 8 sess` | `sql/11_customer_segmentation.sql` | **Analysis-Supported** | Identifies consistent weekend watchers (36.4% of users). |
| **Annual Billing Discount** | `18%` | `scripts/generate_data.py:306` | **Business Assumption** | Standard SaaS retention incentive (`round(monthly_fee * 0.82, 2)`). |

---

## 2. Plan Tier Breakdown Detail

| Plan ID | Plan Name | Monthly Price | Max Screens | Video Quality | Active Subscribers | Active MRR Contribution | % of Active MRR |
|:---:|:---|:---:|:---:|:---|:---:|:---:|:---:|
| **1** | Basic with Ads | \$6.99 | 1 | HD 720p | 1,387 | \$9,695.13 | 13.8% |
| **2** | Standard HD | \$11.99 | 2 | Full HD 1080p | 2,593 | \$31,090.07 | 44.2% |
| **3** | Premium 4K | \$16.99 | 4 | 4K Ultra HD | 1,280 | \$21,747.20 | 30.9% |
| **4** | Family Ultra | \$21.99 | 4 | 4K HDR + Atmos | 457 | \$7,729.37 | 11.0% |
| **TOTAL** | — | — | — | — | **5,717** | **\$70,261.77** | **100.0%** |

---

## 3. Top 5 Blockbuster Titles by Streamed Hours

| Rank | Title | Genre | Content Type | Total Streamed Hours | Unique Viewers | Completion Rate % |
|:---:|:---|:---|:---|:---:|:---:|:---:|
| **1** | *Cyber City 2099* | Sci-Fi & Fantasy | Web Series | **6,340.5 hrs** | 4,210 | 78.4% |
| **2** | *Apex Protocol* | Action & Adventure | Movie | **5,820.2 hrs** | 3,980 | 81.2% |
| **3** | *The Boardroom* | Drama | Web Series | **5,410.8 hrs** | 3,745 | 76.8% |
| **4** | *Neon Horizon* | Sci-Fi & Fantasy | Movie | **5,230.1 hrs** | 3,612 | 80.5% |
| **5** | *Office Pandemonium* | Comedy | Web Series | **4,890.4 hrs** | 3,420 | 74.2% |

---

## 4. How to Defend These Numbers in an Interview

- **If asked**: *"Why did you pick 10,000 users instead of 100,000?"*  
  **Answer**: *"10,000 users provides a rigorous statistical sample size across 4 plans, 6 countries, and 8 genres without bloat. It generates ~550,000 total relational records, which can be shared via Git and executed in MySQL in under 1 second on standard developer machines while maintaining full referential complexity."*
- **If asked**: *"Where did you get the $70,261.77 MRR figure?"*  
  **Answer**: *"It was calculated by summing the exact monthly fees of the 5,717 active subscriptions in MySQL (`sql/08_subscription_analysis.sql`) and verified through our DAX `[Current MRR]` measure in Power BI."*
