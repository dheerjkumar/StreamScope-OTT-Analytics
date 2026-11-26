"""
StreamScope Power BI PBIR Visual Repair Script
===============================================
ROOT CAUSE:
  All Measure projections used wrong structure:
    "Measure": {"Expression": {"Literal": {"Value": "[MeasureName]"}}}
  
  Correct PBIR 2.15.0 syntax is:
    "Measure": {"Expression": {"SourceRef": {"Entity": "TableName"}}, "Property": "MeasureName"}

  Additionally, some column-only visuals (line charts using raw columns) work correctly
  with SourceRef+Entity, but chart_channel_churn was set up incorrectly.

STRATEGY:
  - Rewrite ALL 22 visual.json files from scratch using verified table/column names
  - Use correct PBIR Measure, Column, and Aggregation field structures
  - Every visual gets a complete, schema-valid queryState
  - No Literal wrappers for Measure references
  - Measures live in the "_Measures" table
  - Column fields reference their actual table via SourceRef.Entity

VERIFIED TABLES AND COLUMNS:
  _Measures (DAX measures):
    - Total Registered Users
    - Converted Paying Subscribers
    - Conversion Rate %
    - Active Paid Subscribers
    - Current MRR
    - ARPU
    - Total Watch Hours
    - Total Viewing Sessions
    - Monthly Active Viewers (MAU)
    - Platform Completion Rate %
    - Average Watch Time Per Viewer
    - True Churned Subscribers
    - Monthly Churn Rate %
    - Subscriber Retention Rate %
    - Reactivated Subscribers

  MonthlyPerformance columns:
    calendar_month, new_registrations, active_subscribers, estimated_mrr,
    active_viewers_mau, total_sessions, total_watch_hours, churned_subscribers, lost_mrr

  ContentPerformance columns:
    content_id, title, genre, release_year, content_type, duration_minutes,
    unique_viewers, total_plays, total_watch_hours, avg_completion_percentage

  ChurnByDimension columns:
    subscription_id, user_id, country, acquisition_channel, preferred_device,
    plan_name, monthly_price, start_date, end_date, status, billing_cycle,
    monthly_fee, cancellation_reason, is_true_churn, is_reactivated

  UserSegments columns:
    user_id, signup_date, country, acquisition_channel, preferred_device,
    total_sessions, total_watch_hours, avg_completion_pct, last_streamed_at,
    engagement_segment

  DimUsers: user_id, signup_date, country, age_group, acquisition_channel, preferred_device
  DimPlans: plan_id, plan_name, monthly_price, max_screens, video_quality
  DimContent: content_id, title, genre, release_year, content_type, duration_minutes
  FactSubscriptions: subscription_id, user_id, plan_id, start_date, end_date,
                     status, billing_cycle, monthly_fee, cancellation_reason
  FactViewingSessions: session_id, user_id, content_id, started_at,
                       watch_minutes, completion_percentage, device_type
"""

import json, pathlib

SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.15.0/schema.json"
MEASURES_TABLE = "_Measures"

BASE = pathlib.Path("powerbi/StreamScope_Analytics.Report/definition/pages")

# ------------------------------------------------------------------
# FIELD BUILDERS  (PBIR 2.15.0 correct syntax)
# ------------------------------------------------------------------

def measure_field(measure_name: str, table: str = MEASURES_TABLE) -> dict:
    """Correct PBIR Measure field: Entity SourceRef + Property."""
    return {
        "field": {
            "Measure": {
                "Expression": {"SourceRef": {"Entity": table}},
                "Property": measure_name
            }
        },
        "queryRef": f"{table}.{measure_name}"
    }

def column_field(table: str, column: str) -> dict:
    """Column field for dimensions/categories."""
    return {
        "field": {
            "Column": {
                "Expression": {"SourceRef": {"Entity": table}},
                "Property": column
            }
        },
        "queryRef": f"{table}.{column}"
    }

def agg_field(table: str, column: str, func: int = 0) -> dict:
    """Aggregation field. func=0=Sum, func=5=Count."""
    return {
        "field": {
            "Aggregation": {
                "Expression": {
                    "Column": {
                        "Expression": {"SourceRef": {"Entity": table}},
                        "Property": column
                    }
                },
                "Function": func
            }
        },
        "queryRef": f"Agg({table}.{column})"
    }

def title(text: str) -> dict:
    return {"title": [{"properties": {
        "show": {"expr": {"Literal": {"Value": "true"}}},
        "text": {"expr": {"Literal": {"Value": f"'{text}'"}}}
    }}]}

def card_visual(name: str, pos: dict, measure: str, label: str) -> dict:
    return {
        "$schema": SCHEMA,
        "name": name,
        "position": pos,
        "visual": {
            "visualType": "card",
            "query": {"queryState": {"Values": {"projections": [measure_field(measure)]}}},
            "visualContainerObjects": title(label)
        }
    }

def line_visual(name: str, pos: dict, x_table: str, x_col: str,
                y_measure: str, label: str) -> dict:
    return {
        "$schema": SCHEMA,
        "name": name,
        "position": pos,
        "visual": {
            "visualType": "lineChart",
            "query": {"queryState": {
                "Category": {"projections": [column_field(x_table, x_col)]},
                "Y": {"projections": [measure_field(y_measure)]}
            }},
            "visualContainerObjects": title(label)
        }
    }

def bar_visual(name: str, pos: dict, cat_table: str, cat_col: str,
               y_measure: str, label: str, horizontal: bool = False) -> dict:
    vtype = "barChart" if horizontal else "columnChart"
    return {
        "$schema": SCHEMA,
        "name": name,
        "position": pos,
        "visual": {
            "visualType": vtype,
            "query": {"queryState": {
                "Category": {"projections": [column_field(cat_table, cat_col)]},
                "Y": {"projections": [measure_field(y_measure)]}
            }},
            "visualContainerObjects": title(label)
        }
    }

def bar_col_visual(name: str, pos: dict, cat_table: str, cat_col: str,
                   val_table: str, val_col: str, label: str, horizontal: bool = False) -> dict:
    """Bar chart with a column aggregate (not a DAX measure)."""
    vtype = "barChart" if horizontal else "columnChart"
    return {
        "$schema": SCHEMA,
        "name": name,
        "position": pos,
        "visual": {
            "visualType": vtype,
            "query": {"queryState": {
                "Category": {"projections": [column_field(cat_table, cat_col)]},
                "Y": {"projections": [agg_field(val_table, val_col, 0)]}
            }},
            "visualContainerObjects": title(label)
        }
    }

def donut_visual(name: str, pos: dict, cat_table: str, cat_col: str,
                 y_measure: str, label: str) -> dict:
    return {
        "$schema": SCHEMA,
        "name": name,
        "position": pos,
        "visual": {
            "visualType": "donutChart",
            "query": {"queryState": {
                "Category": {"projections": [column_field(cat_table, cat_col)]},
                "Y": {"projections": [measure_field(y_measure)]}
            }},
            "visualContainerObjects": title(label)
        }
    }

def pie_visual(name: str, pos: dict, cat_table: str, cat_col: str,
               y_measure: str, label: str) -> dict:
    return {
        "$schema": SCHEMA,
        "name": name,
        "position": pos,
        "visual": {
            "visualType": "pieChart",
            "query": {"queryState": {
                "Category": {"projections": [column_field(cat_table, cat_col)]},
                "Y": {"projections": [measure_field(y_measure)]}
            }},
            "visualContainerObjects": title(label)
        }
    }

def slicer_visual(name: str, pos: dict, table: str, col: str, label: str) -> dict:
    return {
        "$schema": SCHEMA,
        "name": name,
        "position": pos,
        "visual": {
            "visualType": "slicer",
            "query": {"queryState": {
                "Values": {"projections": [column_field(table, col)]}
            }},
            "visualContainerObjects": title(label)
        }
    }

# ------------------------------------------------------------------
# VISUAL DEFINITIONS  (all 22 visuals)
# ------------------------------------------------------------------

visuals = {

    # ===============================================================
    # PAGE 1: Executive Overview
    # ===============================================================

    "page_exec_overview/visuals/card_total_users": card_visual(
        "card_total_users",
        {"x": 30, "y": 20, "z": 1, "width": 290, "height": 110},
        "Total Registered Users", "Total Registered Users"
    ),

    "page_exec_overview/visuals/card_active_subs": card_visual(
        "card_active_subs",
        {"x": 340, "y": 20, "z": 2, "width": 290, "height": 110},
        "Active Paid Subscribers", "Active Paid Subscribers"
    ),

    "page_exec_overview/visuals/card_mau": card_visual(
        "card_mau",
        {"x": 650, "y": 20, "z": 3, "width": 290, "height": 110},
        "Monthly Active Viewers (MAU)", "Monthly Active Viewers (MAU)"
    ),

    "page_exec_overview/visuals/card_watch_hours": card_visual(
        "card_watch_hours",
        {"x": 960, "y": 20, "z": 4, "width": 290, "height": 110},
        "Total Watch Hours", "Total Watch Hours"
    ),

    "page_exec_overview/visuals/card_mrr": card_visual(
        "card_mrr",
        {"x": 1270, "y": 20, "z": 5, "width": 290, "height": 110},
        "Current MRR", "Estimated MRR"
    ),

    "page_exec_overview/visuals/card_churn": card_visual(
        "card_churn",
        {"x": 1580, "y": 20, "z": 6, "width": 290, "height": 110},
        "Monthly Churn Rate %", "Monthly Churn Rate"
    ),

    "page_exec_overview/visuals/chart_mau_hours": line_visual(
        "chart_mau_hours",
        {"x": 30, "y": 150, "z": 7, "width": 920, "height": 400},
        "MonthlyPerformance", "calendar_month",
        "Monthly Active Viewers (MAU)", "Monthly Active Viewers Trend"
    ),

    "page_exec_overview/visuals/chart_subs_mrr": line_visual(
        "chart_subs_mrr",
        {"x": 970, "y": 150, "z": 8, "width": 920, "height": 400},
        "MonthlyPerformance", "calendar_month",
        "Current MRR", "Monthly Revenue (MRR) Trend"
    ),

    "page_exec_overview/visuals/chart_plan_dist": donut_visual(
        "chart_plan_dist",
        {"x": 30, "y": 570, "z": 9, "width": 600, "height": 490},
        "DimPlans", "plan_name",
        "Active Paid Subscribers", "Subscription Plan Distribution"
    ),

    "page_exec_overview/visuals/chart_signups_cancels": bar_col_visual(
        "chart_signups_cancels",
        {"x": 650, "y": 570, "z": 10, "width": 630, "height": 490},
        "MonthlyPerformance", "calendar_month",
        "MonthlyPerformance", "new_registrations",
        "Monthly New Registrations"
    ),

    "page_exec_overview/visuals/chart_channel_perf": bar_visual(
        "chart_channel_perf",
        {"x": 1300, "y": 570, "z": 11, "width": 590, "height": 490},
        "DimUsers", "acquisition_channel",
        "Total Registered Users", "Users by Acquisition Channel"
    ),

    # ===============================================================
    # PAGE 2: Content & Engagement
    # ===============================================================

    "page_content_engagement/visuals/slicer_genre": slicer_visual(
        "slicer_genre",
        {"x": 30, "y": 20, "z": 20, "width": 420, "height": 60},
        "ContentPerformance", "genre", "Filter by Genre"
    ),

    "page_content_engagement/visuals/chart_top_content": {
        "$schema": SCHEMA,
        "name": "chart_top_content",
        "position": {"x": 30, "y": 100, "z": 21, "width": 920, "height": 460},
        "visual": {
            "visualType": "barChart",
            "query": {"queryState": {
                "Category": {"projections": [column_field("ContentPerformance", "title")]},
                "Y": {"projections": [agg_field("ContentPerformance", "total_watch_hours", 0)]}
            }},
            "visualContainerObjects": title("Top Titles by Total Streamed Hours")
        }
    },

    "page_content_engagement/visuals/chart_genre_hours": {
        "$schema": SCHEMA,
        "name": "chart_genre_hours",
        "position": {"x": 970, "y": 100, "z": 22, "width": 920, "height": 460},
        "visual": {
            "visualType": "columnChart",
            "query": {"queryState": {
                "Category": {"projections": [column_field("ContentPerformance", "genre")]},
                "Y": {"projections": [agg_field("ContentPerformance", "total_watch_hours", 0)]}
            }},
            "visualContainerObjects": title("Genre-wise Watch Hours")
        }
    },

    "page_content_engagement/visuals/chart_device_share": donut_visual(
        "chart_device_share",
        {"x": 30, "y": 580, "z": 23, "width": 450, "height": 460},
        "FactViewingSessions", "device_type",
        "Total Viewing Sessions", "Device-wise Engagement Share"
    ),

    "page_content_engagement/visuals/chart_completion_genre": {
        "$schema": SCHEMA,
        "name": "chart_completion_genre",
        "position": {"x": 500, "y": 580, "z": 24, "width": 700, "height": 460},
        "visual": {
            "visualType": "columnChart",
            "query": {"queryState": {
                "Category": {"projections": [column_field("ContentPerformance", "genre")]},
                "Y": {"projections": [agg_field("ContentPerformance", "avg_completion_percentage", 4)]}
            }},
            "visualContainerObjects": title("Avg Completion Rate by Genre")
        }
    },

    "page_content_engagement/visuals/chart_type_dynamics": {
        "$schema": SCHEMA,
        "name": "chart_type_dynamics",
        "position": {"x": 1220, "y": 580, "z": 25, "width": 670, "height": 460},
        "visual": {
            "visualType": "columnChart",
            "query": {"queryState": {
                "Category": {"projections": [column_field("ContentPerformance", "content_type")]},
                "Y": {"projections": [agg_field("ContentPerformance", "total_watch_hours", 0)]}
            }},
            "visualContainerObjects": title("Watch Hours by Content Type (Movie vs Series)")
        }
    },

    # ===============================================================
    # PAGE 3: Retention & Churn
    # ===============================================================

    "page_retention_churn/visuals/chart_channel_churn": bar_visual(
        "chart_channel_churn",
        {"x": 30, "y": 20, "z": 30, "width": 900, "height": 460},
        "ChurnByDimension", "acquisition_channel",
        "True Churned Subscribers", "True Churn by Acquisition Channel"
    ),

    "page_retention_churn/visuals/chart_plan_churn": bar_visual(
        "chart_plan_churn",
        {"x": 950, "y": 20, "z": 31, "width": 940, "height": 460},
        "DimPlans", "plan_name",
        "True Churned Subscribers", "True Churn by Subscription Plan"
    ),

    "page_retention_churn/visuals/chart_churn_loss": line_visual(
        "chart_churn_loss",
        {"x": 30, "y": 500, "z": 32, "width": 900, "height": 400},
        "MonthlyPerformance", "calendar_month",
        "True Churned Subscribers", "Monthly Churn Trend"
    ),

    "page_retention_churn/visuals/chart_reasons": pie_visual(
        "chart_reasons",
        {"x": 950, "y": 500, "z": 33, "width": 500, "height": 400},
        "ChurnByDimension", "cancellation_reason",
        "True Churned Subscribers", "Cancellation Reasons"
    ),

    "page_retention_churn/visuals/chart_segments": bar_visual(
        "chart_segments",
        {"x": 1470, "y": 500, "z": 34, "width": 420, "height": 400},
        "UserSegments", "engagement_segment",
        "Active Paid Subscribers", "User Engagement Segments"
    ),
}

# ------------------------------------------------------------------
# WRITE ALL VISUALS
# ------------------------------------------------------------------
updated = 0
errors = []

for rel_path, definition in visuals.items():
    target = BASE / rel_path / "visual.json"
    if not target.parent.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(target, "w", encoding="utf-8") as f:
            json.dump(definition, f, indent=2, ensure_ascii=False)
        updated += 1
        print(f"  OK  {rel_path.split('/')[-1]}")
    except Exception as e:
        errors.append((rel_path, str(e)))
        print(f"  ERR {rel_path}: {e}")

print(f"\nResult: {updated}/22 visuals written. Errors: {len(errors)}")

# ------------------------------------------------------------------
# QUICK SCHEMA AUDIT
# ------------------------------------------------------------------
print("\nSchema audit:")
all_files = list(BASE.rglob("visual.json"))
bad_literal = 0
bad_no_qs   = 0
for vf in all_files:
    content = vf.read_text(encoding="utf-8")
    j = json.loads(content)
    q = j.get("visual", {}).get("query", {})
    if not q.get("queryState"):
        bad_no_qs += 1
        print(f"  NO_QS : {vf.name}  ({vf.parent.parent.name})")
    # Detect Measure->Literal pattern
    if '"Literal"' in content and '"Measure"' in content:
        import re
        if re.search(r'"Measure"\s*:\s*\{[^}]*"Literal"', content, re.DOTALL):
            bad_literal += 1
            print(f"  LITERAL_MEASURE: {vf.parent.name}")

print(f"\nAudit: {len(all_files)} visuals | Measure-Literal errors: {bad_literal} | Missing queryState: {bad_no_qs}")
if bad_literal == 0 and bad_no_qs == 0:
    print("ALL VISUALS PASS SCHEMA AUDIT")
