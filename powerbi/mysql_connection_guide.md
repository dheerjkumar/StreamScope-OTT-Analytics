# StreamScope Power BI - MySQL & Data Connection Guide

This guide provides exact, beginner-friendly instructions to connect Microsoft Power BI Desktop to your StreamScope analytics data.

---

## Connection Method A: Direct Connection to MySQL Database (Recommended)

### Step 1: Open Power BI Desktop
1. Launch **Power BI Desktop** from your Windows Start Menu.
2. In the opening splash screen, click **Get data** (or click **Home -> Get Data -> More...**).

### Step 2: Select the MySQL Database Connector
1. In the search box, type `MySQL`.
2. Select **MySQL database** and click **Connect**.

### Step 3: Specify Server & Database
1. In the dialog:
   - **Server**: `localhost:3306` (or `127.0.0.1:3306`)
   - **Database**: `streamscope`
   - **Data Connectivity mode**: Select **Import** (recommended for interactive slicing and fast performance).
2. Click **OK**.

### Step 4: Enter Database Credentials
1. When prompted for credentials:
   - Select the **Database** tab on the left.
   - **User name**: `root` (or your dedicated user, e.g., `streamscope_reader`).
   - **Password**: Enter your local MySQL root password.
   - Click **Connect**.
2. If an **Encryption Support** warning appears ("Unable to connect using an unencrypted connection"), click **OK** / **Proceed with unencrypted connection** (standard for local host connections).

> [!NOTE]
> **Troubleshooting Driver Requirement**:
> If Power BI displays: *"This connector requires one or more additional components to be installed before it can be used (MySQL Connector/NET)"*:
> - Download and run the official Oracle driver: [MySQL Connector/NET](https://dev.mysql.com/downloads/connector/net/).
> - Install with standard settings, restart Power BI Desktop, and retry.

### Step 5: Select Tables and Views in Navigator
In the Navigator window, expand the `streamscope` database:
- **Option 1 (Full Relational Model)**: Check `users`, `plans`, `subscriptions`, `content`, `viewing_sessions`, and `app_events`.
- **Option 2 (Pre-built Analytics Views)**: Check:
  - `vw_pbi_monthly_performance`
  - `vw_pbi_content_dashboard`
  - `vw_pbi_churn_by_dimension`
  - `v_user_engagement_segments`
- Click **Load**.

---

## Connection Method B: Standalone CSV Import (Zero-Configuration / Offline Alternative)

If you prefer to build and explore the dashboard immediately without configuring MySQL authentication or driver installations, you can load the verified CSV datasets directly:

1. In Power BI Desktop, click **Home -> Get Data -> Text/CSV**.
2. Navigate to your workspace directory:
   `c:\Users\Dheeraj Kumar\OneDrive\Desktop\Documents\StreamScope-OTT-Analytics\data\raw\`
3. Select the files one by one and click **Load**:
   - `users.csv`
   - `plans.csv`
   - `content.csv`
   - `subscriptions.csv`
   - `viewing_sessions.csv`
4. The data structure, data types, and column names are identical to the MySQL database tables.

---

## Model Relationships Configuration (Star Schema)

Navigate to the **Model view** tab (icon on the left sidebar) and verify the following relationships:

1. `users[user_id]` (1) to `subscriptions[user_id]` (*)  [Single direction, 1-to-Many]
2. `plans[plan_id]` (1) to `subscriptions[plan_id]` (*)  [Single direction, 1-to-Many]
3. `users[user_id]` (1) to `viewing_sessions[user_id]` (*) [Single direction, 1-to-Many]
4. `content[content_id]` (1) to `viewing_sessions[content_id]` (*) [Single direction, 1-to-Many]
5. `DimDate[Date]` (1) to `subscriptions[start_date]` (*) [Active]
6. `DimDate[Date]` (1) to `subscriptions[end_date]` (*) [Inactive, used via `USERELATIONSHIP`]
7. `DimDate[Date]` (1) to `viewing_sessions[started_at]` (*) [Active]

Once relationships are established, create a new measure table `_Measures` and copy in the DAX measures from `powerbi/dax_measures.md`!
