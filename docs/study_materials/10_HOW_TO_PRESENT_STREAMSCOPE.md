# Module 10: How to Present StreamScope in Technical Interviews

> **File Reference:** `docs/study_materials/10_HOW_TO_PRESENT_STREAMSCOPE.md`  
> **Audience:** Candidates presenting StreamScope in phone screens, hiring manager chats, technical portfolio reviews, and onsite interviews.

---

## 1. Verbal Presentation Scripts by Time Duration

### 1.1 The 30-Second Elevator Pitch
> *"StreamScope is an end-to-end OTT analytics project where I modeled user engagement and subscriber churn across 10,000 streaming users and 548,000+ records. Using Python for deterministic data generation, MySQL 8.0 for relational schema design and complex SQL queries, and Power BI for executive reporting, I identified that 68% of churned subscribers exhibit a steep drop in viewing hours 3 to 6 weeks before canceling. This provided product teams with an early-warning window to trigger automated re-engagement interventions before billing day."*

---

### 1.2 The 60-Second Overview
> *"In subscription streaming, acquiring a user costs around $50 in marketing, but users can cancel their $11.99 plan with a single click. I built StreamScope to understand the behavioral leading indicators that precede churn.*  
> *I designed a normalized 6-table relational database in MySQL containing 10,000 users, 80 titles, and over 120,000 streaming sessions generated using Python with a deterministic random seed. Using advanced SQL—including window functions like `LAG`, CTEs, and self-joins—I implemented a 30-day True Churn rule to separate genuine cancellations from temporary credit card rebill failures.*  
> *Finally, I brought this into a 10-table Star Schema in Power BI with 15 DAX measures, building an executive dashboard tracking MRR, MAU, and content completion. The core takeaway was that cancellation is rarely impulsive: users experience an 'engagement cliff' weeks prior, watching under 60 minutes in their final month, which gives product teams an actionable window to deploy re-engagement workflows."*

---

### 1.3 The 2-Minute Detailed Project Walkthrough
> *"Hi everyone! I’m excited to share StreamScope, an end-to-end product analytics project focused on OTT user engagement, retention, and subscription churn.*  
> *The core business motivation came from a fundamental OTT vulnerability: direct-to-consumer platforms face high fixed content costs but zero customer switching costs. If a user finishes a hit series and finds nothing else they like, they cancel.*  
> *To analyze this, I structured the project across three technical tiers:*  
> *First, in Python, I engineered a statistically representative dataset of 548,000+ interaction records across 10,000 users. I parameterized 4 behavioral personas—from daily 'Power Streamers' down to 'Dormant' users—and asserted 22 automated data quality checks.*  
> *Second, in MySQL 8.0, I designed a 3NF relational schema. I authored advanced queries tracking DAU/MAU stickiness, cohort retention curves, and customer segmentation. A key analytical achievement was writing a self-join query that classified canceled subscriptions using a 30-day True Churn rule, ensuring fast rebills weren't misclassified as customer attrition.*  
> *Third, I developed a 3-page interactive Power BI dashboard backed by a 10-table Star Schema and 15 custom DAX measures. It tracks our active Monthly Recurring Revenue ($70,261) and genre-wise completion rates.*  
> *The top strategic finding was the 'Engagement Cliff': 68.4% of churned subscribers recorded under 1 hour of streaming in the month before canceling. Based on this, I recommended an automated re-engagement trigger when a user has zero sessions for 12 consecutive days, and proposed a subscription pause feature to mitigate pricing friction."*

---

## 2. Topic Transitions: How to Flow Naturally

When presenting slides or walking through your project, avoid awkward pauses. Use these natural conversational transitions:

- **From Business Problem to Data Engineering**:  
  *"To answer these retention questions, I couldn't rely on basic public movie lists. I needed full longitudinal event telemetry, so I built a deterministic simulation in Python..."*
- **From Python to MySQL Schema**:  
  *"Once the raw data passed my 22 automated assertion checks, I ingested it into MySQL 8.0 to model real relational constraints..."*
- **From Relational Tables to SQL Queries**:  
  *"With the tables indexed and referential integrity guaranteed, I began querying the data to extract core product metrics..."*
- **From SQL to Power BI**:  
  *"While SQL gave us raw tabular answers, executive leadership needs dynamic, self-serve monitoring. So I packaged these queries into 5 modular views and connected them to Power BI Desktop..."*
- **From Power BI to Business Recommendations**:  
  *"Beyond building clean visualizations, the ultimate role of an analyst is driving revenue action. Here is what the data told us to do..."*

---

## 3. How to Handle Interruptions & Technical Curveballs

When an interviewer interrupts with a tough question, follow the **"Acknowledge -> Clarify -> Defend -> Connect"** framework:

1. **Acknowledge**: *"That's a fantastic question, and it was actually one of the biggest modeling challenges I faced."*
2. **Clarify (if needed)**: *"Are you asking about how the query handles that at the SQL level, or how we treat it in the business logic?"*
3. **Defend with Specifics**: Cite exact file names, functions, or numbers (e.g., `sql/09_churn_analysis.sql` or the 30-day window).
4. **Connect Back to Business**: Tie the answer back to customer retention or revenue.

---

## 4. Realistic Mock Interview Simulation (Roleplay)

Here is a realistic transcript of an aggressive technical interviewer cross-questioning a candidate on StreamScope:

> **Interviewer**: *"You say you processed 548,000 records. Is this real customer data from Netflix or did you make it up?"*  
> **Candidate**: *"It is entirely synthetic data generated using a deterministic Python engine. Commercial OTT platforms treat their user-level clickstreams and cancellation timestamps as strictly proprietary trade secrets. Public datasets on Kaggle only provide static movie catalogs without user sessions or subscriptions. By writing a Python simulation using fixed random seed 42, I was able to model true relational dependencies, user personas, and chronologically coherent event sequences while ensuring complete reproducibility."*

> **Interviewer**: *"Okay, but with synthetic data, didn't you just hardcode whatever results you wanted to find?"*  
> **Candidate**: *"Not at all. While the high-level demographic distributions and plan pricing were parameterized based on industry benchmarks—like Netflix's $6.99 to $21.99 tiers—the individual user sessions and cancellation timelines were simulated probabilistically. When I ran my analytical SQL queries in scripts 05 through 12, the findings—such as the 68% engagement cliff and the 13.2% vs 38.4% churn disparity between Referral and Social Media—emerged naturally from the underlying behavioral persona rules rather than hardcoded summary outputs."*

> **Interviewer**: *"Look at your churn definition. Why 30 days? What if a user cancels, goes on vacation for 35 days, and then comes back? Your system calls them churned. Isn't that a flaw?"*  
> **Candidate**: *"That is an insightful observation about right-censoring and boundary thresholds! In subscription economics, if a customer goes without paying for 35 days, their account access has lapsed for an entire billing cycle. From an accounting perspective, that monthly recurring revenue was genuinely lost for that period. When they return on day 35, our system flags them as a 'Reactivated Subscriber' using `ROW_NUMBER() OVER (PARTITION BY user_id)` in script 08. In production, that 30-day threshold can easily be adjusted via a parameter table depending on whether leadership wants a strict 30, 45, or 60-day definition."*

> **Interviewer**: *"In your Power BI dashboard, why did you use Import Mode instead of DirectQuery if you already had a working MySQL database?"*  
> **Candidate**: *"I evaluated both. DirectQuery leaves data in MySQL, meaning every visual click or slicer change translates into a live SQL query sent across the network. For executive reporting across 500,000 records, Import Mode loads the data into Power BI's in-memory columnar VertiPaq engine, which compresses the data to under 40 MB and delivers sub-50-millisecond response times. Furthermore, Import Mode unlocks the full DAX expression library, including complex iterator functions that cannot be natively folded into MySQL SQL."*

> **Interviewer**: *"Impressive defense. Let's move on to your business recommendations..."*
