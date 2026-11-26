"""
StreamScope PBIR Visual Schema Rebuilder
========================================
Regenerates all 22 PBIR visual.json files in strict compliance with the
Microsoft Fabric visualContainer 1.4.0 schema:
1. /visual/query ONLY contains queryState
2. NO 'nativeSummaryFunction' in any projection
3. NO 'Version', 'From', 'Select' under /visual/query
4. Fully bound to SemanticModel entities and DAX measures
"""

import os
import sys
import json
import shutil

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORT_DIR = os.path.join(BASE_DIR, "powerbi", "StreamScope_Analytics.Report")
DEF_DIR = os.path.join(REPORT_DIR, "definition")
PAGES_DIR = os.path.join(DEF_DIR, "pages")

SCHEMA_URI = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.4.0/schema.json"

def make_projection(entity, prop, is_measure=False, agg_func=None):
    """Creates a projection object strictly adhering to visualContainer 1.4.0."""
    if is_measure:
        return {
            "field": {
                "Measure": {
                    "Expression": {
                        "SourceRef": {
                            "Entity": entity
                        }
                    },
                    "Property": prop
                }
            },
            "queryRef": f"{entity}.{prop}"
        }
    elif agg_func is not None:
        fn_code = 0 if agg_func == "Sum" else (5 if agg_func == "Count" else (1 if agg_func == "Average" else 0))
        return {
            "field": {
                "Aggregation": {
                    "Expression": {
                        "Column": {
                            "Expression": {
                                "SourceRef": {
                                    "Entity": entity
                                }
                            },
                            "Property": prop
                        }
                    },
                    "Function": fn_code
                }
            },
            "queryRef": f"{agg_func}({entity}.{prop})"
        }
    else:
        return {
            "field": {
                "Column": {
                    "Expression": {
                        "SourceRef": {
                            "Entity": entity
                        }
                    },
                    "Property": prop
                }
            },
            "queryRef": f"{entity}.{prop}"
        }

def make_visual_json(name, x, y, w, h, z, visual_type, title, query_state):
    """Builds a complete, valid visual.json object with NO illegal properties."""
    return {
        "$schema": SCHEMA_URI,
        "name": name,
        "position": {
            "x": float(x),
            "y": float(y),
            "z": float(z),
            "width": float(w),
            "height": float(h)
        },
        "visual": {
            "visualType": visual_type,
            "query": {
                "queryState": query_state
            },
            "objects": {
                "title": [
                    {
                        "properties": {
                            "show": {
                                "expr": {
                                    "Literal": {
                                        "Value": "true"
                                    }
                                }
                            },
                            "text": {
                                "expr": {
                                    "Literal": {
                                        "Value": f"'{title}'"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }

def build_all_visuals():
    pages = {
        "page_exec_overview": {
            "displayName": "Executive Overview",
            "visuals": {}
        },
        "page_content_engagement": {
            "displayName": "Content & Engagement",
            "visuals": {}
        },
        "page_retention_churn": {
            "displayName": "Retention & Churn",
            "visuals": {}
        }
    }

    # =========================================================================
    # PAGE 1: EXECUTIVE OVERVIEW (11 visuals)
    # =========================================================================
    p1 = pages["page_exec_overview"]["visuals"]

    # 6 Top KPI Cards
    kpis = [
        ("card_total_users", 30, 90, 290, 110, 1, "Total Users", "Total Registered Users"),
        ("card_active_subs", 340, 90, 290, 110, 2, "Active Paid Subscribers", "Active Paid Subscribers"),
        ("card_mau", 650, 90, 290, 110, 3, "Monthly Active Viewers (MAU)", "Monthly Active Viewers (MAU)"),
        ("card_watch_hours", 960, 90, 290, 110, 4, "Total Streamed Hours", "Total Watch Hours"),
        ("card_mrr", 1270, 90, 290, 110, 5, "Active Run-Rate (MRR)", "Current MRR"),
        ("card_churn", 1580, 90, 310, 110, 6, "Monthly Churn Rate %", "Monthly Churn Rate %")
    ]
    for v_id, x, y, w, h, z, title, measure_name in kpis:
        qs = {
            "Values": {
                "projections": [make_projection("_Measures", measure_name, is_measure=True)]
            }
        }
        p1[v_id] = make_visual_json(v_id, x, y, w, h, z, "card", title, qs)

    # Chart 1: Active Subscribers & MRR Growth (lineStackedColumnComboChart)
    qs_subs_mrr = {
        "Category": {
            "projections": [make_projection("MonthlyPerformance", "calendar_month")]
        },
        "Y": {
            "projections": [make_projection("MonthlyPerformance", "estimated_mrr", agg_func="Sum")]
        },
        "Y2": {
            "projections": [make_projection("MonthlyPerformance", "active_subscribers", agg_func="Sum")]
        }
    }
    p1["chart_subs_mrr"] = make_visual_json("chart_subs_mrr", 30, 220, 920, 390, 7, "lineStackedColumnComboChart", "Active Subscribers & Monthly Revenue Growth", qs_subs_mrr)

    # Chart 2: Subscribers by Plan Tier (donutChart)
    qs_plan_dist = {
        "Category": {
            "projections": [make_projection("DimPlans", "plan_name")]
        },
        "Values": {
            "projections": [make_projection("FactSubscriptions", "subscription_id", agg_func="Count")]
        }
    }
    p1["chart_plan_dist"] = make_visual_json("chart_plan_dist", 970, 220, 920, 390, 8, "donutChart", "Subscribers by Plan Tier", qs_plan_dist)

    # Chart 3: Monthly Active Viewers & Watch Hours (areaChart)
    qs_mau_hours = {
        "Category": {
            "projections": [make_projection("MonthlyPerformance", "calendar_month")]
        },
        "Y": {
            "projections": [
                make_projection("MonthlyPerformance", "total_watch_hours", agg_func="Sum"),
                make_projection("MonthlyPerformance", "active_viewers_mau", agg_func="Sum")
            ]
        }
    }
    p1["chart_mau_hours"] = make_visual_json("chart_mau_hours", 30, 630, 920, 410, 9, "areaChart", "Monthly Active Viewers (MAU) & Watch Hours Dynamics", qs_mau_hours)

    # Chart 4: Signups by Acquisition Channel (clusteredBarChart)
    qs_channel = {
        "Category": {
            "projections": [make_projection("DimUsers", "acquisition_channel")]
        },
        "Y": {
            "projections": [make_projection("DimUsers", "user_id", agg_func="Count")]
        }
    }
    p1["chart_channel_perf"] = make_visual_json("chart_channel_perf", 970, 630, 450, 410, 10, "clusteredBarChart", "Signups by Marketing Acquisition Channel", qs_channel)

    # Chart 5: New Registrations vs Churned Subscribers (lineStackedColumnComboChart)
    qs_signups_cancels = {
        "Category": {
            "projections": [make_projection("MonthlyPerformance", "calendar_month")]
        },
        "Y": {
            "projections": [make_projection("MonthlyPerformance", "new_registrations", agg_func="Sum")]
        },
        "Y2": {
            "projections": [make_projection("MonthlyPerformance", "churned_subscribers", agg_func="Sum")]
        }
    }
    p1["chart_signups_cancels"] = make_visual_json("chart_signups_cancels", 1440, 630, 450, 410, 11, "lineStackedColumnComboChart", "New Registrations vs Churned Subscribers", qs_signups_cancels)

    # =========================================================================
    # PAGE 2: CONTENT & ENGAGEMENT (6 visuals)
    # =========================================================================
    p2 = pages["Section_Content_Engagement"]["visuals"]

    # Visual 12: Top 10 Blockbuster Titles (clusteredBarChart)
    qs_top_content = {
        "Category": {
            "projections": [make_projection("ContentPerformance", "title")]
        },
        "Y": {
            "projections": [make_projection("ContentPerformance", "total_watch_hours", agg_func="Sum")]
        }
    }
    p2["chart_top_content"] = make_visual_json("chart_top_content", 30, 90, 920, 460, 12, "clusteredBarChart", "Top 10 Blockbuster Titles by Streamed Watch Hours", qs_top_content)

    # Visual 13: Watch Time by Genre (clusteredColumnChart)
    qs_genre_hours = {
        "Category": {
            "projections": [make_projection("ContentPerformance", "genre")]
        },
        "Y": {
            "projections": [make_projection("ContentPerformance", "total_watch_hours", agg_func="Sum")]
        }
    }
    p2["chart_genre_hours"] = make_visual_json("chart_genre_hours", 970, 90, 920, 460, 13, "clusteredColumnChart", "Total Streamed Watch Hours by Content Genre", qs_genre_hours)

    # Visual 14: Viewing Sessions by Device (donutChart)
    qs_device = {
        "Category": {
            "projections": [make_projection("FactViewingSessions", "device_type")]
        },
        "Values": {
            "projections": [make_projection("FactViewingSessions", "session_id", agg_func="Count")]
        }
    }
    p2["chart_device_share"] = make_visual_json("chart_device_share", 30, 570, 600, 470, 14, "donutChart", "Viewing Sessions by Hardware Device Type", qs_device)

    # Visual 15: Content Format Reach (clusteredColumnChart)
    qs_format = {
        "Category": {
            "projections": [make_projection("ContentPerformance", "content_type")]
        },
        "Y": {
            "projections": [
                make_projection("ContentPerformance", "unique_viewers", agg_func="Sum"),
                make_projection("ContentPerformance", "total_plays", agg_func="Sum")
            ]
        }
    }
    p2["chart_type_dynamics"] = make_visual_json("chart_type_dynamics", 650, 570, 600, 470, 15, "clusteredColumnChart", "Unique Viewers & Stream Plays by Content Format", qs_format)

    # Visual 16: Average Title Completion by Genre (clusteredBarChart)
    qs_completion = {
        "Category": {
            "projections": [make_projection("ContentPerformance", "genre")]
        },
        "Y": {
            "projections": [make_projection("ContentPerformance", "avg_completion_percentage", agg_func="Average")]
        }
    }
    p2["chart_completion_genre"] = make_visual_json("chart_completion_genre", 1270, 570, 620, 470, 16, "clusteredBarChart", "Average Title Completion Percentage by Genre", qs_completion)

    # Visual 17: Interactive Genre Slicer (slicer)
    qs_slicer = {
        "Values": {
            "projections": [make_projection("DimContent", "genre")]
        }
    }
    p2["slicer_genre"] = make_visual_json("slicer_genre", 30, 20, 420, 60, 17, "slicer", "Filter by Content Genre", qs_slicer)

    # =========================================================================
    # PAGE 3: RETENTION & CHURN (5 visuals)
    # =========================================================================
    p3 = pages["Section_Retention_Churn"]["visuals"]

    # Visual 18: Monthly Churn & Lost Revenue Trend (lineStackedColumnComboChart)
    qs_churn_loss = {
        "Category": {
            "projections": [make_projection("MonthlyPerformance", "calendar_month")]
        },
        "Y": {
            "projections": [make_projection("MonthlyPerformance", "lost_mrr", agg_func="Sum")]
        },
        "Y2": {
            "projections": [make_projection("MonthlyPerformance", "churned_subscribers", agg_func="Sum")]
        }
    }
    p3["chart_churn_loss"] = make_visual_json("chart_churn_loss", 30, 90, 920, 460, 18, "lineStackedColumnComboChart", "Monthly Churned Subscribers & Lost Revenue Trend", qs_churn_loss)

    # Visual 19: Cancellation Reasons Pareto (clusteredBarChart)
    qs_reasons = {
        "Category": {
            "projections": [make_projection("ChurnByDimension", "cancellation_reason")]
        },
        "Y": {
            "projections": [make_projection("ChurnByDimension", "subscription_id", agg_func="Count")]
        }
    }
    p3["chart_reasons"] = make_visual_json("chart_reasons", 970, 90, 920, 460, 19, "clusteredBarChart", "Primary Stated Cancellation Reasons (Pareto)", qs_reasons)

    # Visual 20: Cancellations by Subscription Plan Tier (clusteredColumnChart)
    qs_plan_churn = {
        "Category": {
            "projections": [make_projection("ChurnByDimension", "plan_name")]
        },
        "Y": {
            "projections": [make_projection("ChurnByDimension", "is_true_churn", agg_func="Sum")]
        }
    }
    p3["chart_plan_churn"] = make_visual_json("chart_plan_churn", 30, 570, 600, 470, 20, "clusteredColumnChart", "Cancellations by Subscription Plan Tier", qs_plan_churn)

    # Visual 21: Subscriber Churn Rate by Acquisition Channel (clusteredBarChart)
    qs_chan_churn = {
        "Category": {
            "projections": [make_projection("ChurnByDimension", "acquisition_channel")]
        },
        "Y": {
            "projections": [make_projection("ChurnByDimension", "is_true_churn", agg_func="Sum")]
        }
    }
    p3["chart_channel_churn"] = make_visual_json("chart_channel_churn", 650, 570, 600, 470, 21, "clusteredBarChart", "Subscriber Churn Rate by Marketing Acquisition Channel", qs_chan_churn)

    # Visual 22: Audience by Engagement Tier (donutChart)
    qs_segments = {
        "Category": {
            "projections": [make_projection("UserSegments", "engagement_segment")]
        },
        "Values": {
            "projections": [make_projection("UserSegments", "user_id", agg_func="Count")]
        }
    }
    p3["chart_segments"] = make_visual_json("chart_segments", 1270, 570, 620, 470, 22, "donutChart", "Customer Distribution by Engagement Behavioral Tier", qs_segments)

    return pages

def main():
    print("=" * 65)
    print("StreamScope PBIR Visual Schema Rebuilder")
    print("=" * 65)

    pages = build_all_visuals()
    page_order = list(pages.keys())

    # Write pages.json
    pages_manifest = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
        "pageOrder": page_order,
        "activePageName": page_order[0]
    }
    with open(os.path.join(PAGES_DIR, "pages.json"), "w", encoding="utf-8") as f:
        json.dump(pages_manifest, f, indent=2)
    print(f"✓ Updated pages.json ({len(page_order)} pages)")

    total_visuals = 0
    for page_id, p_info in pages.items():
        page_dir = os.path.join(PAGES_DIR, page_id)
        visuals_dir = os.path.join(page_dir, "visuals")

        # Clean old visuals directory completely
        if os.path.exists(visuals_dir):
            shutil.rmtree(visuals_dir)
        os.makedirs(visuals_dir, exist_ok=True)

        # Write page.json
        p_def = {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
            "name": page_id,
            "displayName": p_info["displayName"],
            "displayOption": "FitToPage",
            "height": 1080,
            "width": 1920
        }
        with open(os.path.join(page_dir, "page.json"), "w", encoding="utf-8") as f:
            json.dump(p_def, f, indent=2)

        # Write each visual.json
        for v_name, v_json in p_info["visuals"].items():
            v_sub_dir = os.path.join(visuals_dir, v_name)
            os.makedirs(v_sub_dir, exist_ok=True)
            v_file = os.path.join(v_sub_dir, "visual.json")
            with open(v_file, "w", encoding="utf-8") as f:
                json.dump(v_json, f, indent=2)
            total_visuals += 1

    print(f"✓ Successfully wrote all {total_visuals} compliant PBIR visual definitions!")
    print("=" * 65)

if __name__ == "__main__":
    main()
