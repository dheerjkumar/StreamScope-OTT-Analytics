# StreamScope Limitations, Analytical Assumptions & Edge Cases

An essential trait of a Senior Product / Data Analyst is transparency regarding data constraints, modeling assumptions, and analytical boundaries. This document outlines the explicit assumptions and methodological limitations of the StreamScope analytics project.

---

## 1. Synthetic Dataset Disclosure & Reproducibility
- **Synthetic Nature**: All records (users, subscriptions, viewing sessions, events) are synthetically generated using a deterministic Python engine. While the distributions, correlations, and behaviors reflect realistic streaming economics, they do not represent proprietary internal data from any commercial streaming service.
- **Reproducibility**: The dataset was produced using a fixed pseudorandom seed (`RANDOM_SEED = 42`). Any analyst executing `py scripts/generate_data.py` will generate the exact identical 10,000 user profiles, 7,868 subscription records, and 121,801 viewing sessions.

---

## 2. Key Analytical Assumptions

### A. 30-Day Churn Definition
- **Assumption**: A paid subscriber is classified as **churned** only when their subscription access lapses and they do not restart a paid subscription within **30 calendar days**.
- **Rationale**: In real-world OTT businesses, many cancellations occur due to temporary credit card expiration, banking holds, or short-term travel. Counting immediate rebills as churn would inflate churn rates and distort lifetime value calculations.
- **Limitation**: Users who cancel with no intention of returning but are gifted a reactivation on day 29 are classified as continuous renewals.

### B. Currency & Pricing Normalization
- **Assumption**: All financial figures are denominated in US Dollars ($ USD) based on standardized tier pricing ($6.99, $11.99, $16.99, $21.99).
- **Limitation**: In global operations (e.g., India, UK, Germany), local purchasing power parity (PPP), currency fluctuations, and localized tier pricing (e.g., mobile-only plans in INR) would introduce foreign exchange variances that are abstracted here.

### C. Observation Window & Right-Censoring
- **Observation Window**: January 1, 2025 to December 31, 2025.
- **Follow-up Grace Window**: Extended to January 31, 2026.
- **Right-Censoring Management**:
  - The additional 30-day follow-up period ensures that users canceling in December 2025 have a full 30-day window to evaluate true churn vs fast reactivation.
  - Cohort retention for later cohorts (e.g., October–December 2025) is acknowledged as incomplete for Month 6 retention calculations and marked accordingly.

---

## 3. Correlation vs. Causation Caveat

In product analytics, confusing correlation with causation is a frequent error:
- **Observation**: Highly engaged viewers (30+ hours/month) experience a near-zero churn rate (< 3%).
- **Flawed Conclusion**: *"If we force or trick low-engagement users into streaming more hours, they will stop churning."*
- **Analytical Truth**: High viewing hours are a **symptom of high customer perceived value**, not the root cause itself. Churn mitigation requires improving content discovery, onboarding alignment, and catalog depth so that users naturally *want* to watch more.

---

## 4. Boundary & Edge Case Handling in SQL

| Edge Case | How It Is Handled | SQL / Architectural Logic |
| :--- | :--- | :--- |
| **Multiple Subscriptions per User** | Prevented duplicate counting. | Uses `COUNT(DISTINCT user_id)` and isolates first subscription using `MIN(start_date)`. |
| **Overlapping Subscriptions** | Prevented during data generation. | Confirmed via `validate_data.py` and `04_data_quality_checks.sql` (0 overlaps found). |
| **Active Subscriptions with NULL End Dates** | Handled in active subscriber and MRR queries. | Condition: `s.start_date <= Date AND (s.end_date IS NULL OR s.end_date > Date)`. |
| **Orphan Sessions / Events** | Foreign key constraints enforced. | All foreign keys enforce referential integrity to `users` and `content`. |
