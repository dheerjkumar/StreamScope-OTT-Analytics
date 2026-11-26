"""
StreamScope Full Power BI Dashboard Builder
===========================================
Reconstructs the complete 3-page interactive Power BI report:
1. Injects complete PBIR structure (pages, visualContainers, field projections, visual formatting)
   into powerbi/StreamScope_Analytics.pbix while preserving the live MySQL DataModel intact.
2. Updates powerbi/StreamScope_Analytics.Report/ for full PBIP project compatibility.
3. Implements 3 comprehensive pages:
   - Page 1: Executive Overview (KPI Cards, MRR Trend, Viewer Trend, Plan Mix, Acquisition Channels)
   - Page 2: Content and Engagement (Top 10 Titles, Genre Hours, Completion Rates, Device Mix, Content Types)
   - Page 3: Retention and Churn (Monthly Churn & Lost MRR, Cancellation Reasons, Plan Churn, Channel Churn, User Segments)
"""

import os
import json
import zipfile
import shutil

DRAFT_PBIX = os.path.join("powerbi", "StreamScope_Analytics_Draft.pbix")
FINAL_PBIX = os.path.join("powerbi", "StreamScope_Analytics.pbix")
PBIP_REPORT_DIR = os.path.join("powerbi", "StreamScope_Analytics.Report")

def create_visual_json(visual_id, x, y, w, h, z, visual_type, title, query_state):
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.1.0/schema.json",
        "name": visual_id,
        "position": {
            "x": x,
            "y": y,
            "z": z,
            "width": w,
            "height": h
        },
        "visual": {
            "visualType": visual_type,
            "query": {
                "queryState": query_state
            },
            "visualContainerObjects": {
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

def make_card(visual_id, x, y, w, h, z, title, entity, prop, func_name=0):
    query_state = {
        "Values": {
            "projections": [
                {
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
                            "Function": func_name
                        }
                    },
                    "queryRef": f"{func_name}({entity}.{prop})"
                }
            ]
        }
    }
    return create_visual_json(visual_id, x, y, w, h, z, "card", title, query_state)

def make_category_y_chart(visual_id, x, y, w, h, z, visual_type, title, cat_entity, cat_prop, val_entity, val_prop, func_name=0):
    query_state = {
        "Category": {
            "projections": [
                {
                    "field": {
                        "Column": {
                            "Expression": {
                                "SourceRef": {
                                    "Entity": cat_entity
                                }
                            },
                            "Property": cat_prop
                        }
                    },
                    "queryRef": f"{cat_entity}.{cat_prop}",
                    "nativeSummaryFunction": 0
                }
            ]
        },
        "Y": {
            "projections": [
                {
                    "field": {
                        "Aggregation": {
                            "Expression": {
                                "Column": {
                                    "Expression": {
                                        "SourceRef": {
                                            "Entity": val_entity
                                        }
                                    },
                                    "Property": val_prop
                                }
                            },
                            "Function": func_name
                        }
                    },
                    "queryRef": f"{func_name}({val_entity}.{val_prop})"
                }
            ]
        }
    }
    return create_visual_json(visual_id, x, y, w, h, z, visual_type, title, query_state)

def make_multi_y_chart(visual_id, x, y, w, h, z, visual_type, title, cat_entity, cat_prop, val_specs):
    # val_specs: list of (val_entity, val_prop, func_name)
    y_projections = []
    for ve, vp, fn in val_specs:
        y_projections.append({
            "field": {
                "Aggregation": {
                    "Expression": {
                        "Column": {
                            "Expression": {
                                "SourceRef": {
                                    "Entity": ve
                                }
                            },
                            "Property": vp
                        }
                    },
                    "Function": fn
                }
            },
            "queryRef": f"{fn}({ve}.{vp})"
        })

    query_state = {
        "Category": {
            "projections": [
                {
                    "field": {
                        "Column": {
                            "Expression": {
                                "SourceRef": {
                                    "Entity": cat_entity
                                }
                            },
                            "Property": cat_prop
                        }
                    },
                    "queryRef": f"{cat_entity}.{cat_prop}",
                    "nativeSummaryFunction": 0
                }
            ]
        },
        "Y": {
            "projections": y_projections
        }
    }
    return create_visual_json(visual_id, x, y, w, h, z, visual_type, title, query_state)

def build_pages_and_visuals():
    pages_dict = {}

    # -------------------------------------------------------------
    # PAGE 1: Executive Overview
    # -------------------------------------------------------------
    p1_id = "page_exec_overview"
    p1_visuals = {}

    # KPI Cards
    p1_visuals["card_total_users"] = make_card("card_total_users", 30, 20, 290, 110, 1, "Total Registered Users", "streamscope vw_pbi_churn_by_dimension", "user_id", func_name=5)
    p1_visuals["card_active_subs"] = make_card("card_active_subs", 340, 20, 290, 110, 2, "Active Paid Subscribers", "streamscope vw_pbi_monthly_performance", "active_subscribers", func_name=2)
    p1_visuals["card_mau"] = make_card("card_mau", 650, 20, 290, 110, 3, "Monthly Active Viewers (MAU)", "streamscope vw_pbi_monthly_performance", "active_viewers_mau", func_name=2)
    p1_visuals["card_watch_hours"] = make_card("card_watch_hours", 960, 20, 290, 110, 4, "Total Streamed Watch Hours", "streamscope vw_pbi_monthly_performance", "total_watch_hours", func_name=0)
    p1_visuals["card_mrr"] = make_card("card_mrr", 1270, 20, 290, 110, 5, "Monthly Recurring Revenue (MRR)", "streamscope vw_pbi_monthly_performance", "estimated_mrr", func_name=2)
    p1_visuals["card_churn"] = make_card("card_churn", 1580, 20, 310, 110, 6, "Total Churned Subscribers", "streamscope vw_pbi_monthly_performance", "churned_subscribers", func_name=0)

    # Chart 1: Active Subscribers & Recurring Revenue Run-Rate Trend (x=30, y=150, w=920, h=440)
    p1_visuals["chart_subs_mrr"] = make_multi_y_chart(
        "chart_subs_mrr", 30, 150, 920, 440, 7, "clusteredColumnChart",
        "Active Subscribers & Monthly Revenue Run-Rate Trend",
        "streamscope vw_pbi_monthly_performance", "calendar_month",
        [
            ("streamscope vw_pbi_monthly_performance", "active_subscribers", 0),
            ("streamscope vw_pbi_monthly_performance", "estimated_mrr", 0)
        ]
    )

    # Chart 2: Monthly Active Viewers (MAU) & Watch Hours Trend (x=970, y=150, w=920, h=440)
    p1_visuals["chart_mau_hours"] = make_multi_y_chart(
        "chart_mau_hours", 970, 150, 920, 440, 8, "lineChart",
        "Monthly Active Viewers (MAU) & Streamed Hours Trend",
        "streamscope vw_pbi_monthly_performance", "calendar_month",
        [
            ("streamscope vw_pbi_monthly_performance", "active_viewers_mau", 0),
            ("streamscope vw_pbi_monthly_performance", "total_watch_hours", 0)
        ]
    )

    # Chart 3: Active Paid Subscribers by Plan Tier (x=30, y=610, w=600, h=440)
    p1_visuals["chart_plan_dist"] = make_category_y_chart(
        "chart_plan_dist", 30, 610, 600, 440, 9, "donutChart",
        "Subscribers by Subscription Plan Tier",
        "streamscope vw_pbi_churn_by_dimension", "plan_name",
        "streamscope vw_pbi_churn_by_dimension", "subscription_id", func_name=5
    )

    # Chart 4: Monthly New Signups vs Cancellations (x=650, y=610, w=630, h=440)
    p1_visuals["chart_signups_cancels"] = make_multi_y_chart(
        "chart_signups_cancels", 650, 610, 630, 440, 10, "clusteredColumnChart",
        "Monthly New Registrations vs Subscriber Cancellations",
        "streamscope vw_pbi_monthly_performance", "calendar_month",
        [
            ("streamscope vw_pbi_monthly_performance", "new_registrations", 0),
            ("streamscope vw_pbi_monthly_performance", "churned_subscribers", 0)
        ]
    )

    # Chart 5: Acquisition Channel Performance (x=1300, y=610, w=590, h=440)
    p1_visuals["chart_channel_perf"] = make_category_y_chart(
        "chart_channel_perf", 1300, 610, 590, 440, 11, "barChart",
        "Customer Acquisition by Marketing Channel",
        "streamscope vw_pbi_churn_by_dimension", "acquisition_channel",
        "streamscope vw_pbi_churn_by_dimension", "user_id", func_name=5
    )

    pages_dict[p1_id] = {
        "displayName": "Executive Overview",
        "visuals": p1_visuals
    }

    # -------------------------------------------------------------
    # PAGE 2: Content and Engagement
    # -------------------------------------------------------------
    p2_id = "page_content_engagement"
    p2_visuals = {}

    # Chart 1: Top 10 Movies & Web Series by Total Watch Hours (x=30, y=30, w=920, h=500)
    p2_visuals["chart_top_content"] = make_category_y_chart(
        "chart_top_content", 30, 30, 920, 500, 20, "barChart",
        "Top Blockbuster Titles by Total Streamed Hours",
        "streamscope vw_pbi_content_dashboard", "title",
        "streamscope vw_pbi_content_dashboard", "total_watch_hours", func_name=0
    )

    # Chart 2: Total Streamed Hours by Genre (x=970, y=30, w=920, h=500)
    p2_visuals["chart_genre_hours"] = make_category_y_chart(
        "chart_genre_hours", 970, 30, 920, 500, 21, "clusteredColumnChart",
        "Total Streamed Watch Hours by Content Genre",
        "streamscope vw_pbi_content_dashboard", "genre",
        "streamscope vw_pbi_content_dashboard", "total_watch_hours", func_name=0
    )

    # Chart 3: Device-wise Viewing Preference (x=30, y=550, w=590, h=500)
    p2_visuals["chart_device_share"] = make_category_y_chart(
        "chart_device_share", 30, 550, 590, 500, 22, "donutChart",
        "Audience Share by Preferred Streaming Device",
        "streamscope v_user_engagement_segments", "preferred_device",
        "streamscope v_user_engagement_segments", "user_id", func_name=5
    )

    # Chart 4: Feature Films vs Web Series Reach & Plays (x=640, y=550, w=630, h=500)
    p2_visuals["chart_type_dynamics"] = make_multi_y_chart(
        "chart_type_dynamics", 640, 550, 630, 500, 23, "clusteredColumnChart",
        "Unique Viewers & Total Plays by Content Type",
        "streamscope vw_pbi_content_dashboard", "content_type",
        [
            ("streamscope vw_pbi_content_dashboard", "unique_viewers", 0),
            ("streamscope vw_pbi_content_dashboard", "total_plays", 0)
        ]
    )

    # Chart 5: Average Completion Rate by Genre (x=1290, y=550, w=600, h=500)
    p2_visuals["chart_completion_genre"] = make_category_y_chart(
        "chart_completion_genre", 1290, 550, 600, 500, 24, "barChart",
        "Average Title Completion Rate by Genre",
        "streamscope vw_pbi_content_dashboard", "genre",
        "streamscope vw_pbi_content_dashboard", "avg_completion_percentage", func_name=1
    )

    pages_dict[p2_id] = {
        "displayName": "Content & Engagement",
        "visuals": p2_visuals
    }

    # -------------------------------------------------------------
    # PAGE 3: Retention and Churn
    # -------------------------------------------------------------
    p3_id = "page_retention_churn"
    p3_visuals = {}

    # Chart 1: Monthly Subscriber Churn Volume & Lost MRR (x=30, y=30, w=920, h=500)
    p3_visuals["chart_churn_loss"] = make_multi_y_chart(
        "chart_churn_loss", 30, 30, 920, 500, 30, "lineChart",
        "Monthly Churned Subscribers & Lost Recurring Revenue Trend",
        "streamscope vw_pbi_monthly_performance", "calendar_month",
        [
            ("streamscope vw_pbi_monthly_performance", "churned_subscribers", 0),
            ("streamscope vw_pbi_monthly_performance", "lost_mrr", 0)
        ]
    )

    # Chart 2: Stated Cancellation Reasons Distribution (x=970, y=30, w=920, h=500)
    p3_visuals["chart_reasons"] = make_category_y_chart(
        "chart_reasons", 970, 30, 920, 500, 31, "barChart",
        "Primary Stated Customer Cancellation Reasons",
        "streamscope vw_pbi_churn_by_dimension", "cancellation_reason",
        "streamscope vw_pbi_churn_by_dimension", "subscription_id", func_name=5
    )

    # Chart 3: Churn Events by Subscription Plan (x=30, y=550, w=590, h=500)
    p3_visuals["chart_plan_churn"] = make_category_y_chart(
        "chart_plan_churn", 30, 550, 590, 500, 32, "clusteredColumnChart",
        "True Churn Events by Subscription Plan Tier",
        "streamscope vw_pbi_churn_by_dimension", "plan_name",
        "streamscope vw_pbi_churn_by_dimension", "is_true_churn", func_name=0
    )

    # Chart 4: Churn Events by Acquisition Channel (x=640, y=550, w=630, h=500)
    p3_visuals["chart_channel_churn"] = make_category_y_chart(
        "chart_channel_churn", 640, 550, 630, 500, 33, "barChart",
        "True Churn Events by Customer Acquisition Channel",
        "streamscope vw_pbi_churn_by_dimension", "acquisition_channel",
        "streamscope vw_pbi_churn_by_dimension", "is_true_churn", func_name=0
    )

    # Chart 5: Audience by Behavioral Engagement Segment (x=1290, y=550, w=600, h=500)
    p3_visuals["chart_segments"] = make_category_y_chart(
        "chart_segments", 1290, 550, 600, 500, 34, "donutChart",
        "Customer Distribution by Engagement Behavioral Tier",
        "streamscope v_user_engagement_segments", "engagement_segment",
        "streamscope v_user_engagement_segments", "user_id", func_name=5
    )

    pages_dict[p3_id] = {
        "displayName": "Retention & Churn",
        "visuals": p3_visuals
    }

    return pages_dict

def main():
    print("=" * 65)
    print("StreamScope Power BI Dashboard Rebuilder")
    print("=" * 65)

    if not os.path.exists(DRAFT_PBIX):
        print(f"Error: {DRAFT_PBIX} not found.")
        return False

    pages_data = build_pages_and_visuals()
    page_order = list(pages_data.keys())

    # Build PBIR pages.json
    pages_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
        "pageOrder": page_order,
        "activePageName": page_order[0]
    }

    # Open draft pbix and inject new PBIR structure
    print(f"\n[1/3] Reading base structure and live DataModel from {DRAFT_PBIX}...")
    with zipfile.ZipFile(DRAFT_PBIX, "r") as z_in:
        namelist = z_in.namelist()

        # Files to keep from draft: everything except old Report/definition/pages/
        files_to_copy = {}
        for name in namelist:
            if not name.startswith("Report/definition/pages/"):
                files_to_copy[name] = z_in.read(name)

    # Add new pages and visualContainer JSONs
    print(f"\n[2/3] Generating 3 complete dashboard pages and 21 visual containers...")
    new_files = {}

    # pages.json
    new_files["Report/definition/pages/pages.json"] = json.dumps(pages_json, indent=2).encode("utf-8")

    # Each page and its visuals
    for page_id, p_info in pages_data.items():
        page_def = {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
            "name": page_id,
            "displayName": p_info["displayName"],
            "displayOption": "FitToPage",
            "height": 1080,
            "width": 1920
        }
        new_files[f"Report/definition/pages/{page_id}/page.json"] = json.dumps(page_def, indent=2).encode("utf-8")

        for v_id, v_json in p_info["visuals"].items():
            path = f"Report/definition/pages/{page_id}/visuals/{v_id}/visual.json"
            new_files[path] = json.dumps(v_json, indent=2).encode("utf-8")

    # Combine all into final pbix
    print(f"\n[3/3] Assembling and saving completed report to {FINAL_PBIX}...")
    with zipfile.ZipFile(FINAL_PBIX, "w", zipfile.ZIP_DEFLATED) as z_out:
        for fname, data in files_to_copy.items():
            z_out.writestr(fname, data)
        for fname, data in new_files.items():
            z_out.writestr(fname, data)

    final_size_kb = os.path.getsize(FINAL_PBIX) / 1024
    print(f"✓ Saved {FINAL_PBIX} successfully! ({final_size_kb:.1f} KB)")

    # Also sync definition files into powerbi/StreamScope_Analytics.Report/definition/ for PBIP
    report_def_dir = os.path.join(PBIP_REPORT_DIR, "definition")
    os.makedirs(report_def_dir, exist_ok=True)

    # Sync version.json and report.json if present
    if "Report/definition/version.json" in files_to_copy:
        with open(os.path.join(report_def_dir, "version.json"), "wb") as f:
            f.write(files_to_copy["Report/definition/version.json"])
    if "Report/definition/report.json" in files_to_copy:
        with open(os.path.join(report_def_dir, "report.json"), "wb") as f:
            f.write(files_to_copy["Report/definition/report.json"])

    # Sync pages
    pages_fs_dir = os.path.join(report_def_dir, "pages")
    os.makedirs(pages_fs_dir, exist_ok=True)
    with open(os.path.join(pages_fs_dir, "pages.json"), "wb") as f:
        f.write(new_files["Report/definition/pages/pages.json"])

    for page_id, p_info in pages_data.items():
        p_dir = os.path.join(pages_fs_dir, page_id)
        v_dir = os.path.join(p_dir, "visuals")
        os.makedirs(v_dir, exist_ok=True)

        with open(os.path.join(p_dir, "page.json"), "wb") as f:
            f.write(new_files[f"Report/definition/pages/{page_id}/page.json"])

        for v_id, v_json in p_info["visuals"].items():
            vis_sub_dir = os.path.join(v_dir, v_id)
            os.makedirs(vis_sub_dir, exist_ok=True)
            with open(os.path.join(vis_sub_dir, "visual.json"), "w", encoding="utf-8") as f:
                json.dump(v_json, f, indent=2)

    print(f"✓ Synchronized PBIR definition into {PBIP_REPORT_DIR}/definition/ successfully!")
    print("\n" + "=" * 65)
    print("POWER BI DASHBOARD REBUILD COMPLETE: 3 PAGES & 21 VISUAL CONTAINERS")
    print("=" * 65)
    return True

if __name__ == "__main__":
    main()
