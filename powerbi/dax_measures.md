# StreamScope Power BI - DAX Measures Library

This document contains all production Data Analysis Expressions (DAX) measures used across the StreamScope dashboards. Each measure is documented with its mathematical formula, business rationale, and DAX implementation.

---

## 1. Calendar Dimension Table (DAX Calculated Table)

Create this table in Power BI by navigating to **Modeling -> New Table**:

```dax
DimDate = 
VAR MinDate = DATE(2025, 1, 1)
VAR MaxDate = DATE(2026, 1, 31)
RETURN
ADDCOLUMNS (
    CALENDAR (MinDate, MaxDate),
    "Year", YEAR ( [Date] ),
    "YearMonthNumber", YEAR ( [Date] ) * 100 + MONTH ( [Date] ),
    "Year-Month", FORMAT ( [Date], "YYYY-MM" ),
    "MonthName", FORMAT ( [Date], "MMMM" ),
    "MonthShort", FORMAT ( [Date], "MMM" ),
    "Quarter", "Q" & FORMAT ( [Date], "Q" ),
    "DayOfWeek", FORMAT ( [Date], "dddd" ),
    "DayOfWeekNumber", WEEKDAY ( [Date], 2 ), -- Monday = 1, Sunday = 7
    "IsWeekend", IF ( WEEKDAY ( [Date], 2 ) IN {6, 7}, "Weekend", "Weekday" )
)
```

---

## 2. Executive & Core Volume Measures

### Measure: `[Total Registered Users]`
- **Purpose**: Total top-of-funnel accounts created on StreamScope.
- **DAX Formula**:
```dax
Total Registered Users = 
DISTINCTCOUNT ( users[user_id] )
```

### Measure: `[Converted Paying Subscribers]`
- **Purpose**: Unique users who have purchased at least one paid subscription.
- **DAX Formula**:
```dax
Converted Paying Subscribers = 
CALCULATE (
    DISTINCTCOUNT ( subscriptions[user_id] ),
    subscriptions[status] IN { "Active", "Canceled" }
)
```

### Measure: `[Conversion Rate %]`
- **Purpose**: Top-of-funnel conversion rate from free registration to paid subscription.
- **Formula**: `(Converted Paying Subscribers / Total Registered Users) * 100`
- **DAX Formula**:
```dax
Conversion Rate % = 
DIVIDE (
    [Converted Paying Subscribers],
    [Total Registered Users],
    0
) * 100
```

### Measure: `[Active Paid Subscribers]`
- **Purpose**: Current paying subscriber base who hold an ongoing subscription with no cancellation date or an active period encompassing the selected date.
- **DAX Formula**:
```dax
Active Paid Subscribers = 
CALCULATE (
    DISTINCTCOUNT ( subscriptions[user_id] ),
    subscriptions[status] = "Active"
)
```

### Measure: `[Current MRR]`
- **Purpose**: Estimated Monthly Recurring Revenue from all currently active subscriptions.
- **DAX Formula**:
```dax
Current MRR = 
CALCULATE (
    SUM ( subscriptions[monthly_fee] ),
    subscriptions[status] = "Active"
)
```

### Measure: `[ARPU (Average Revenue Per User)]`
- **Purpose**: Average monthly subscription contribution per active subscriber.
- **DAX Formula**:
```dax
ARPU = 
DIVIDE (
    [Current MRR],
    [Active Paid Subscribers],
    0
)
```

---

## 3. Streaming Engagement Measures

### Measure: `[Total Watch Hours]`
- **Purpose**: Cumulative viewing volume streamed across all titles and devices.
- **DAX Formula**:
```dax
Total Watch Hours = 
DIVIDE (
    SUM ( viewing_sessions[watch_minutes] ),
    60,
    0
)
```

### Measure: `[Total Viewing Sessions]`
- **Purpose**: Total playbacks / streaming sessions initiated.
- **DAX Formula**:
```dax
Total Viewing Sessions = 
COUNTROWS ( viewing_sessions )
```

### Measure: `[Monthly Active Viewers (MAU)]`
- **Purpose**: Unique users who completed at least one streaming session in the reporting period.
- **DAX Formula**:
```dax
Monthly Active Viewers = 
DISTINCTCOUNT ( viewing_sessions[user_id] )
```

### Measure: `[Average Session Duration (Mins)]`
- **Purpose**: Mean playback length of individual viewing sessions.
- **DAX Formula**:
```dax
Average Session Duration Mins = 
AVERAGE ( viewing_sessions[watch_minutes] )
```

### Measure: `[Platform Completion Rate %]`
- **Purpose**: Average percentage of title duration completed by viewers across all playback sessions.
- **DAX Formula**:
```dax
Platform Completion Rate % = 
AVERAGE ( viewing_sessions[completion_percentage] )
```

### Measure: `[DAU to MAU Stickiness %]`
- **Purpose**: Measure of daily user return frequency.
- **DAX Formula**:
```dax
DAU to MAU Stickiness % = 
VAR AvgDAU = 
    AVERAGEX (
        VALUES ( DimDate[Date] ),
        CALCULATE ( DISTINCTCOUNT ( viewing_sessions[user_id] ) )
    )
VAR MAU = [Monthly Active Viewers]
RETURN
DIVIDE ( AvgDAU, MAU, 0 ) * 100
```

---

## 4. Churn & Retention Measures

### Measure: `[True Churned Subscribers]`
- **Purpose**: Subscribers whose subscription ended and who did not restart within 30 days.
- **DAX Formula**:
```dax
True Churned Subscribers = 
CALCULATE (
    DISTINCTCOUNT ( subscriptions[user_id] ),
    subscriptions[status] = "Canceled",
    NOT ( ISBLANK ( subscriptions[end_date] ) )
)
```

### Measure: `[Monthly Churn Rate %]`
- **Purpose**: Percentage of the opening subscriber base that canceled in the specified month.
- **DAX Formula**:
```dax
Monthly Churn Rate % = 
VAR SelectedMonthStart = MIN ( DimDate[Date] )
VAR OpeningSubscribers = 
    CALCULATE (
        DISTINCTCOUNT ( subscriptions[user_id] ),
        subscriptions[start_date] < SelectedMonthStart,
        subscriptions[end_date] >= SelectedMonthStart || ISBLANK ( subscriptions[end_date] ),
        REMOVEFILTERS ( DimDate )
    )
VAR ChurnedInMonth = 
    CALCULATE (
        DISTINCTCOUNT ( subscriptions[user_id] ),
        subscriptions[status] = "Canceled",
        USERELATIONSHIP ( subscriptions[end_date], DimDate[Date] )
    )
RETURN
DIVIDE ( ChurnedInMonth, OpeningSubscribers, 0 ) * 100
```

### Measure: `[Lost MRR to Churn]`
- **Purpose**: Monthly recurring revenue lost to canceled subscriptions.
- **DAX Formula**:
```dax
Lost MRR to Churn = 
CALCULATE (
    SUM ( subscriptions[monthly_fee] ),
    subscriptions[status] = "Canceled",
    USERELATIONSHIP ( subscriptions[end_date], DimDate[Date] )
)
```

### Measure: `[Subscriber Retention Rate %]`
- **Purpose**: Complement of the churn rate (`100% - Churn Rate %`).
- **DAX Formula**:
```dax
Subscriber Retention Rate % = 
IF (
    NOT ( ISBLANK ( [Monthly Churn Rate %] ) ),
    100 - [Monthly Churn Rate %],
    BLANK ()
)
```

---

## 5. Visual Formatting Reference Table

| Measure | Display Format | Decimals | Prefix / Suffix |
| :--- | :--- | :--- | :--- |
| `[Total Registered Users]` | `#,##0` | 0 | None |
| `[Active Paid Subscribers]` | `#,##0` | 0 | None |
| `[Current MRR]` | `$#,##0` | 0 | `$` |
| `[ARPU]` | `$#,##0.00` | 2 | `$` |
| `[Total Watch Hours]` | `#,##0.0` | 1 | ` hrs` |
| `[Conversion Rate %]` | `0.0%` | 1 | `%` |
| `[Platform Completion Rate %]` | `0.0%` | 1 | `%` |
| `[Monthly Churn Rate %]` | `0.0%` | 1 | `%` |
