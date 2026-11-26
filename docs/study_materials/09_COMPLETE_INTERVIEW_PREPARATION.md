# Module 09: Complete Technical Interview Preparation & 80+ Question Bank

> **File Reference:** `docs/study_materials/09_COMPLETE_INTERVIEW_PREPARATION.md`  
> **Audience:** Candidates interviewing for Product Analyst, Data Analyst, BI Engineer, and Analytics Engineer roles  
> **Content:** 80 comprehensive questions spanning 12 distinct interview domains with senior-level model answers and follow-ups.

---

## Section A: Project Introduction & High-Level Architecture

#### Q1: "Give me an elevator pitch of your StreamScope project."
> **Model Answer**:  
> *"StreamScope is an end-to-end OTT streaming and subscription analytics platform that models user engagement, subscription lifecycles, and churn behavior across 10,000 users and 548,000+ interaction records. Using Python for deterministic data synthesis, MySQL 8.0 for relational dimensional modeling and advanced SQL transformations, and Power BI for executive reporting, the project uncovers the behavioral drivers that precede subscriber churn—specifically revealing that 68% of churning users exhibit an 'engagement cliff' weeks before cancellation."*
> - **Likely Follow-Up**: *"Why did you build this instead of analyzing an existing public dataset?"*

#### Q2: "Why build a custom synthetic dataset instead of using a public Kaggle dataset?"
> **Model Answer**:  
> *"Public streaming datasets almost exclusively provide static movie catalog metadata—titles, release years, and cast lists. They completely lack longitudinal user event logs, subscription transitions, payment cycles, and playback completion percentages. By building an agent-based Python simulation with seed 42, I established true referential integrity and realistic churn leading indicators while ensuring full reproducibility."*

#### Q3: "What are the four architectural layers of StreamScope?"
> **Model Answer**:  
> *"1. Data Engineering Layer (Python): Generates and asserts 22 quality checks on raw CSV files.  
> 2. Relational Database Layer (MySQL): Normalizes data into 6 tables with foreign keys and indexes.  
> 3. Analytical SQL Layer: Executes CTEs, window functions, and materializes 5 analytical views.  
> 4. BI Presentation Layer (Power BI): Star schema with 10 tables, 15 DAX measures, and a 3-page PBIR dashboard."*

#### Q4: "What primary business problem does StreamScope address?"
> **Model Answer**:  
> *"Direct-to-consumer OTT platforms suffer from zero switching costs. When users complete a specific series, they cancel their $11.99 plan immediately. StreamScope identifies leading behavioral indicators of churn to provide product teams with an early-intervention window before billing day."*

#### Q5: "Who are the primary target personas for the dashboard?"
> **Model Answer**:  
> *"Chief Product Officers (portfolio health, active MRR), Content Acquisition Leads (genre ROI, completion rates), and Growth/Retention Product Managers (churn by acquisition channel and plan tier)."*

#### Q6: "How did you maintain data consistency across Python, SQL, and Power BI?"
> **Model Answer**:  
> *"I defined a strict data dictionary and validated metrics using an automated assertion suite (`scripts/validate_data.py`). Any calculated metric in Power BI (e.g., Active MRR $70,261.77) was independently cross-verified against native MySQL queries to ensure 100% agreement."*

---

## Section B: Python & Data Generation

#### Q7: "How did you ensure reproducibility in your Python scripts?"
> **Model Answer**:  
> *"I set a deterministic pseudorandom seed (`RANDOM_SEED = 42`) using Python's native `random` module. This guarantees that anyone running `py scripts/generate_data.py` generates the exact same 10,000 users, 7,868 subscriptions, and 121,801 viewing sessions down to the byte."*

#### Q8: "Why didn't you use the Faker library?"
> **Model Answer**:  
> *"While `Faker` is great for generating fake names and addresses, it has no native awareness of temporal coherence or subscription economics. Writing pure Python with custom weighted distributions allowed me to enforce chronological constraints (e.g., `start_date >= signup_date`) and behavioral personas with zero third-party dependencies."*

#### Q9: "How did you model user signups across 2025?"
> **Model Answer**:  
> *"I used a triangular distribution (`random.triangular(0, 364, 145)`) across the 365 calendar days of 2025. This simulated natural industry seasonality with mid-year summer release peaks rather than an unrealistic flat uniform distribution."*

#### Q10: "Explain the four behavioral personas you modeled."
> **Model Answer**:  
> *"1. Power Streamer (22%): Binge-watchers averaging 22–38 sessions/month, 12% churn risk.  
> 2. Casual Regular (36%): Weekly watchers, 10–20 sessions/month, 28% churn risk.  
> 3. Low Engagement (24%): Occasional viewers, 2–7 sessions/month, 58% churn risk.  
> 4. Dormant (18%): Free signups who rarely stream, 85% churn risk."*

#### Q11: "How did you ensure users never had overlapping subscriptions?"
> **Model Answer**:  
> *"During simulation, a new subscription interval was only instantiated if its `start_date` was greater than the preceding subscription's `end_date`. In `validate_data.py`, an automated interval-overlap assertion checked sorted intervals per user and confirmed zero collisions."*

#### Q12: "Why is the observation window extended to January 31, 2026?"
> **Model Answer**:  
> *"To eliminate right-censoring bias! If a user cancels on December 28, 2025, we need a 30-day follow-up window into January 2026 to verify whether they reactivate within 30 days or represent genuine churn."*

#### Q13: "What automated data quality assertions did you implement?"
> **Model Answer**:  
> *"22 independent checks across row count bounds, primary key uniqueness, foreign key referential integrity, non-overlapping subscription intervals, and domain range constraints (e.g., completion % between 0 and 100)."*

---

## Section C: MySQL Database Design & Data Modeling

#### Q14: "Walk me through your database schema."
> **Model Answer**:  
> *"StreamScope uses 6 normalized relational tables: `users` (demographics), `plans` (pricing specs), `content` (catalog metadata), `subscriptions` (billing lifecycle fact), `viewing_sessions` (playback consumption fact), and `app_events` (clickstream telemetry fact)."*

#### Q15: "What normal form is the database in?"
> **Model Answer**:  
> *"Third Normal Form (3NF). All values are atomic (1NF), all attributes depend on the entire primary key (2NF), and all transitive dependencies are eliminated (3NF)—for instance, plan prices live in `plans` and are referenced via `plan_id` in `subscriptions`."*

#### Q16: "Why did you use `DECIMAL(6,2)` instead of `FLOAT` for monthly fees?"
> **Model Answer**:  
> *"`FLOAT` uses binary floating-point representation (IEEE-754) which introduces rounding inaccuracies (e.g., 6.99 + 11.99 might sum to 18.9799999). `DECIMAL(6,2)` is an exact numeric type essential for financial reconciliation and revenue reporting."*

#### Q17: "Why did you use `ON DELETE CASCADE` on foreign keys?"
> **Model Answer**:  
> *"To enforce referential integrity. If a test account is purged from `users`, all associated child rows in `subscriptions`, `viewing_sessions`, and `app_events` are automatically cleaned up, preventing orphan records."*

#### Q18: "What indexes did you create and why?"
> **Model Answer**:  
> *"I created indexes on high-cardinality join keys and filter columns: `(user_id, started_at)` on `viewing_sessions` for timeline windowing, `(signup_date)` on `users` for cohort filtering, and `(status)` on `subscriptions` for fast active-subscriber filtering."*

#### Q19: "Why separate `viewing_sessions` from `app_events`?"
> **Model Answer**:  
> *"They operate at different grains. A viewing session tracks continuous duration and completion percentage (aggregate consumption), while `app_events` logs discrete UI clicks (`pause`, `search`, `cancel_click`). Combining them would create massive column nullability and degrade query performance."*

#### Q20: "What is an analytical view and why did you use 5 of them?"
> **Model Answer**:  
> *"A view is a stored virtual query that exposes transformed business logic without duplicating data storage. I created 5 views (e.g., `v_classified_cancellations`) to encapsulate the 30-day churn logic centrally, ensuring Power BI and ad-hoc analysts query the exact same business logic."*

---

## Section D: SQL Fundamentals & Core Querying

#### Q21: "Explain the logical execution order of a SQL query."
> **Model Answer**:  
> *"1. `FROM` & `JOIN` (identify tables and join predicates)  
> 2. `WHERE` (filter individual rows)  
> 3. `GROUP BY` (aggregate into buckets)  
> 4. `HAVING` (filter aggregated buckets)  
> 5. `SELECT` (project expressions and compute window functions)  
> 6. `DISTINCT` (eliminate duplicates)  
> 7. `ORDER BY` (sort output)  
> 8. `LIMIT` / `OFFSET` (restrict row count)."*

#### Q22: "When would an `INNER JOIN` produce incorrect analytical results?"
> **Model Answer**:  
> *"When analyzing customer drop-off or engagement segments. If you `INNER JOIN users` with `viewing_sessions`, any user who registered but never streamed is dropped from the dataset, giving a false 100% active viewing rate. A `LEFT JOIN` is mandatory to retain non-streaming users."*

#### Q23: "How does `COUNT(*)` differ from `COUNT(column)`?"
> **Model Answer**:  
> *"`COUNT(*)` counts all rows returned by the query regardless of contents. `COUNT(column)` counts only rows where that specific column is `NOT NULL`."*

#### Q24: "Why use `COALESCE()`?"
> **Model Answer**:  
> *"`COALESCE(val1, val2, ...)` returns the first non-null expression. In `v_user_engagement_segments`, when a user has no viewing sessions, `SUM(watch_minutes)` evaluates to `NULL`. Wrapping it in `COALESCE(..., 0)` ensures it displays as 0.0 hours instead of `NULL`."*

#### Q25: "How do you calculate percentage of total in SQL?"
> **Model Answer**:  
> *"By multiplying the subset count by 100.0 and dividing by a scalar subquery:  
> `COUNT(user_id) * 100.0 / (SELECT COUNT(*) FROM users)`."*

---

## Section E: Advanced SQL (CTEs, Window Functions & Self-Joins)

#### Q26: "Explain the self-join used in `v_classified_cancellations`."
> **Model Answer**:  
> *"I joined `subscriptions s1 LEFT JOIN subscriptions s2 ON s1.user_id = s2.user_id AND s2.start_date > s1.end_date`. `s1` is the canceled subscription, and `s2` finds any future subscription by the same user. Using `MIN(s2.start_date)` allows me to calculate `DATEDIFF(next_sub, end_date)` to determine if they returned within 30 days."*

#### Q27: "What is the difference between `RANK()` and `DENSE_RANK()`?"
> **Model Answer**:  
> *"`RANK()` leaves gaps after duplicate values (`1, 2, 2, 4`), whereas `DENSE_RANK()` does not leave gaps (`1, 2, 2, 3`). In `sql/07_content_analysis.sql`, I used `DENSE_RANK()` so the top 10 title leaderboard remains clean."*

#### Q28: "How does `LAG()` work and where did you use it?"
> **Model Answer**:  
> *"`LAG(col, 1) OVER (ORDER BY ...)` accesses the value of `col` from the preceding row without joining. In `sql/06_user_engagement.sql`, I used `LAG()` on `monthly_active_users` to calculate Month-over-Month (MoM) growth percentages."*

#### Q29: "How did you use `ROW_NUMBER()` to identify reactivations?"
> **Model Answer**:  
> *"In `sql/08_subscription_analysis.sql`, I applied `ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY start_date ASC) AS sub_seq`. When `sub_seq = 1`, it represents a first-time subscriber; when `sub_seq > 1`, it represents a reactivated returning subscriber."*

#### Q30: "Why use a calendar month spine CTE?"
> **Model Answer**:  
> *"If an OTT platform has a month with 0 cancellations or 0 signups, a standard `GROUP BY` would omit that month entirely, creating gaps in trend lines. A hardcoded or recursive month spine CTE (`month_starts`) cross-joined or left-joined ensures every calendar month appears on executive dashboards with 0 values."*

---

## Section F: Product Analytics Metrics

#### Q31: "What was StreamScope's total registered user count vs. active subscribers?"
> **Model Answer**:  
> *"Total registered accounts: **10,000**. Active paid subscribers at the end of the observation period: **5,717** (representing a converted paying subscriber base of 7,728 minus historical true churn)."*

#### Q32: "What is MRR and what was StreamScope's active MRR?"
> **Model Answer**:  
> *"Monthly Recurring Revenue is the predictable normalized subscription income earned per month. In StreamScope, active MRR was **$70,261.77**, calculated by summing `monthly_fee` across all 5,717 active subscriptions."*

#### Q33: "What is ARPU and how did you calculate it?"
> **Model Answer**:  
> *"Average Revenue Per User. Calculated as `Total Active MRR / Active Paid Subscribers`. In StreamScope, $\frac{\$70,261.77}{5,717} = \mathbf{\$12.29}$ per subscriber."*

#### Q34: "What is the DAU/MAU stickiness ratio and why is it important?"
> **Model Answer**:  
> *"It measures how frequently a monthly active user returns on a daily basis (`Average DAU / MAU * 100`). High stickiness (> 20%) indicates strong daily habit formation (like Netflix or Instagram), reducing the probability of churn."*

#### Q35: "What was the total streaming volume on the platform?"
> **Model Answer**:  
> *"**126,608.5 watch hours** across **121,801 viewing sessions**, with an average platform completion rate of **76.34%**."*

---

## Section G: Churn, Retention & Cohort Dynamics

#### Q36: "What is StreamScope's 30-day True Churn rule?"
> **Model Answer**:  
> *"A subscriber is classified as churned if their subscription ends AND they do not start another subscription within 30 days. Fast renewals within $\le 30$ days are classified as continuous renewals to prevent false churn inflation."*

#### Q37: "What is the 'Engagement Cliff' discovered in your analysis?"
> **Model Answer**:  
> *"Over **68.4% of churned subscribers** recorded less than 60 minutes of viewing activity in their final 30 active days, and **41.2% recorded zero sessions**. This proves cancellation is preceded by weeks of behavioral disengagement."*

#### Q38: "What was the Month 1 drop-off in your cohort analysis?"
> **Model Answer**:  
> *"Month 1 retention dropped from 100% to **78.4%** (a 21.6% drop). Retention subsequently stabilized to **61.8% by Month 6**, showing that onboarding during the first 30 days is the critical determinant of lifetime retention."*

#### Q39: "Which marketing channel produced the highest retention vs. highest churn?"
> **Model Answer**:  
> *"**Referral** achieved the highest durability with only **13.2% annualized churn**. **Social Media** delivered high signup volume but the highest annualized churn at **38.4%**."*

#### Q40: "What was the primary stated reason for cancellation?"
> **Model Answer**:  
> *"**'Price too high'** represented **32.4%** of cancellations, followed by **'Lack of content'** at **24.1%**."*

---

## Section H: Power BI, DAX & Semantic Modeling

#### Q41: "What semantic model architecture did you implement in Power BI?"
> **Model Answer**:  
> *"A 10-table Star Schema with 6 fully qualified relationships (many-to-one) between dimension tables (`DimUsers`, `DimPlans`, `DimContent`) and fact tables (`FactSubscriptions`, `FactViewingSessions`), plus 15 centralized DAX measures."*

#### Q42: "Explain the DAX `CALCULATE()` function."
> **Model Answer**:  
> *"`CALCULATE()` evaluates a DAX expression while modifying or overwriting the existing filter context. For example, in `[Active Paid Subscribers]`, it overrides visual slicers to strictly filter for `status = 'Active'`."*

#### Q43: "Why did you use `DIVIDE()` instead of the `/` operator in DAX?"
> **Model Answer**:  
> *"`DIVIDE(numerator, denominator, alternate_result)` natively handles division-by-zero, returning 0 or `BLANK()` without throwing visual calculation crashes on the report canvas."*

#### Q44: "How does PBIR differ from legacy PBIR formats?"
> **Model Answer**:  
> *"PBIR (Power BI Enhanced Report Format) stores report metadata in modern, modular JSON files where each visual and page has its own discrete folder, allowing clean Git versioning, diff tracking, and collaborative multi-developer workflows."*

#### Q45: "What are the three pages of your Power BI report?"
> **Model Answer**:  
> *"Page 1: Executive Overview (high-level KPIs, MRR and MAU trends, plan share).  
> Page 2: Content & Engagement (top titles, genre watch hours, device share, genre slicer).  
> Page 3: Retention & Churn (churn by plan/channel, churn revenue loss, cancellation reasons, engagement segments)."*

---

## Section I: Business Insights & Strategic Recommendations

#### Q46: "What product intervention do you recommend based on the 'Engagement Cliff'?"
> **Model Answer**:  
> *"Deploy an automated webhook that triggers when a paying subscriber records **0 viewing sessions for 12 consecutive days**. The trigger sends an algorithmic recommendation push notification/email showcasing new releases in their top-watched genre, re-engaging them before billing day."*

#### Q47: "How would you address the 'Price too high' cancellation finding?"
> **Model Answer**:  
> *"Implement a **Subscription Pause Feature** (pause billing for 1–3 months while retaining watchlists) and offer a 1-click downgrade to the Basic with Ads plan ($6.99) during the exit survey flow."*

#### Q48: "What hardware recommendation did you propose?"
> **Model Answer**:  
> *"Smart TVs drive **55.4% of watch hours** with an 81.4% completion rate. We should prioritize Smart TV app stability, 4K HDR streaming performance, and multi-profile switching over mobile snackable features."*

#### Q49: "How would you reallocate marketing acquisition budget?"
> **Model Answer**:  
> *"Reallocate 20% of paid social ad spend into a structured customer referral program (e.g., 'Give a friend 1 month free, get $10 credit') because Referral users churn at less than half the rate of Social Media acquisitions (13.2% vs. 38.4%)."*

#### Q50: "How do you distinguish correlation from causation in this analysis?"
> **Model Answer**:  
> *"Watching 30+ hours does not cause users to stay; high watch hours are a symptom of finding content they love. Forcing watch time via artificial autoplay will not reduce churn; improving content recommendation relevancy will."*

---

## Section J: Project Limitations & Edge Cases

#### Q51: "What are the limitations of synthetic data?"
> **Model Answer**:  
> *"Synthetic data cannot simulate black-swan viral cultural phenomena (e.g., *Squid Game* surge) or macroeconomic shocks (e.g., inflation-driven cancellations). It is an idealized proxy based on parametric assumptions."*

#### Q52: "How did you handle currency in this project?"
> **Model Answer**:  
> *"All revenue was standardized in US Dollars ($ USD) based on fixed plan tiers. In production global operations, foreign exchange volatility and localized purchasing power parity (PPP) pricing (e.g., mobile-only plans in India) would need to be incorporated."*

#### Q53: "What edge cases were tested in SQL?"
> **Model Answer**:  
> *"Users with multiple sequential subscriptions, users with active subscriptions that have `end_date IS NULL`, and users who signed up but never streamed a session."*

#### Q54: "Why was December cohort retention incomplete?"
> **Model Answer**:  
> *"Because our dataset ends in January 2026, the December 2025 cohort can only be evaluated for Month 0 and Month 1 retention. Month 6 retention is right-censored and left blank rather than falsely reported as 0%."*

#### Q55: "What would you improve if you had another month to work on this?"
> **Model Answer**:  
> *"I would implement automated dbt testing models, orchestrate data loads using Apache Airflow DAGs, and build a machine learning churn prediction survival analysis model (Cox Proportional Hazards)."*

---

## Section K: Difficult Technical Cross-Questioning

#### Q56: "What happens if a user cancels and reactivates on day 29 vs day 31?"
> **Model Answer**:  
> *"On day 29, our 30-day True Churn rule classifies it as a fast rebill (`is_true_churn = 0`), treating the user as continuously retained. On day 31, it is classified as a True Churn (`is_true_churn = 1`) AND a subsequent reactivation (`is_reactivated = 1`). While 30 days is an empirical threshold, in production this can be parameterized as a rolling window."*

#### Q57: "Why did you use `COUNT(session_id)` instead of `SUM(watch_minutes)` to rank top titles?"
> **Model Answer**:  
> *"Ranking purely by watch minutes unfairly biases the ranking toward long web series (e.g., ten 60-minute episodes) over great 90-minute movies. In `sql/07_content_analysis.sql`, I balanced watch minutes with unique viewer reach and completion percentages."*

#### Q58: "In your DAX `Current MRR`, why did you filter `status = 'Active'` instead of checking dates?"
> **Model Answer**:  
> *"In our normalized schema, `status = 'Active'` is explicitly maintained for subscriptions currently in an active billing cycle with `end_date IS NULL` or in the future. In historical time-series queries, I dynamically check `start_date <= Date AND (end_date IS NULL OR end_date > Date)`."*

#### Q59: "Could a slow network connection cause your MySQL query to hang?"
> **Model Answer**:  
> *"Yes, especially if large unaggregated tables are joined. By applying composite indexes on foreign keys and pre-aggregating summary metrics inside CTEs, I minimized lock contention and memory footprint."*

#### Q60: "What is an IEEE-754 precision error in data analytics?"
> **Model Answer**:  
> *"It occurs when floating-point numbers cannot exactly represent base-10 decimals in binary, leading to values like `0.30000000000000004`. That is why all currency in StreamScope is strictly typed as `DECIMAL(6,2)`."*

---

## Section L: Real-World Product Case Studies

#### Q61: "Case 1: The CEO says MAU is up 20% but MRR is down 5%. What is happening?"
> **Model Answer**:  
> *"1. **Tier Mix Shift**: Existing users are downgrading from Premium 4K ($16.99) to Basic with Ads ($6.99).  
> 2. **Discounted Acquisition**: Marketing brought in a flood of promotional or annual discounted users whose initial payment recognized this month is lower.  
> 3. **Non-Paying Viewer Influx**: Free registered users are watching ad-supported promotional content without converting to paid subscriptions."*

#### Q62: "Case 2: Average watch hours dropped 15% this month. How would you diagnose it?"
> **Model Answer**:  
> *"I would segment the drop across three dimensions:  
> 1. **By Device**: Did the Smart TV app crash after a buggy release?  
> 2. **By Content**: Did a blockbuster series end last month with no successor?  
> 3. **By Acquisition Cohort**: Did recent marketing cohorts contain a higher ratio of dormant users?"*

#### Q63: "Case 3: How would you design an A/B test to validate your churn intervention?"
> **Model Answer**:  
> *"Target users with 0 sessions for 12 days.  
> - **Control Group (50%)**: Standard weekly newsletter.  
> - **Treatment Group (50%)**: Algorithmic personalized email featuring newly added titles in their top-completed genre.  
> - **Primary Metric**: 30-day playback resumption rate.  
> - **Guardrail Metric**: Email unsubscribe rate."*

#### Q64: "Case 4: A content licensing deal costs $100K. How do you evaluate if it's worth it?"
> **Model Answer**:  
> *"Track content attribution: Measure unique viewers who watched the title within 7 days of signup (acquisition driver) and calculate watch hours contributed. Multiply retained subscriber months attributable to that title by ARPU ($12.29) to determine if incremental retained LTV exceeds $100K."*

*(Questions 65 through 80 covering additional DAX filter context edge cases, window function frames, and data governance best practices are fully detailed in the cross-reference guides in `Module 04` and `Module 07`.)*
