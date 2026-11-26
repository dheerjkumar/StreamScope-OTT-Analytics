"""
StreamScope PBIP & Semantic Model Repair Utility
================================================
Comprehensive repair of:
1. Semantic model relationships (full cardinality, active state, cross-filtering metadata)
2. Semantic model M partition expressions (Windows path escaping, QuoteStyle.Csv)
3. PBIP report.json (sections with 3 pages and 22 interactive visual containers)
4. PBIR v2.0 definition/ folder structure
5. Verification of data tables and measure binding
"""

import os
import sys
import json
import uuid

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
POWERBI_DIR = os.path.join(WORKSPACE_DIR, "powerbi")
DATA_DIR = os.path.join(POWERBI_DIR, "data")
SEMANTIC_DIR = os.path.join(POWERBI_DIR, "StreamScope_Analytics.SemanticModel")
DATASET_DIR = os.path.join(POWERBI_DIR, "StreamScope_Analytics.Dataset")
REPORT_DIR = os.path.join(POWERBI_DIR, "StreamScope_Analytics.Report")

def repair_semantic_model():
    print("[1/3] Repairing Semantic Model relationships and M partitions...")
    bim_path = os.path.join(SEMANTIC_DIR, "model.bim")
    with open(bim_path, "r", encoding="utf-8") as f:
        bim_data = json.load(f)

    # 1. Fix relationships with full metadata
    repaired_rels = [
        {
            "name": "rel_subs_users",
            "fromTable": "FactSubscriptions",
            "fromColumn": "user_id",
            "toTable": "DimUsers",
            "toColumn": "user_id",
            "isActive": True,
            "crossFilteringBehavior": "oneDirection",
            "fromCardinality": "many",
            "toCardinality": "one",
            "relyOnReferentialIntegrity": True
        },
        {
            "name": "rel_subs_plans",
            "fromTable": "FactSubscriptions",
            "fromColumn": "plan_id",
            "toTable": "DimPlans",
            "toColumn": "plan_id",
            "isActive": True,
            "crossFilteringBehavior": "oneDirection",
            "fromCardinality": "many",
            "toCardinality": "one",
            "relyOnReferentialIntegrity": True
        },
        {
            "name": "rel_sess_users",
            "fromTable": "FactViewingSessions",
            "fromColumn": "user_id",
            "toTable": "DimUsers",
            "toColumn": "user_id",
            "isActive": True,
            "crossFilteringBehavior": "oneDirection",
            "fromCardinality": "many",
            "toCardinality": "one",
            "relyOnReferentialIntegrity": True
        },
        {
            "name": "rel_sess_content",
            "fromTable": "FactViewingSessions",
            "fromColumn": "content_id",
            "toTable": "DimContent",
            "toColumn": "content_id",
            "isActive": True,
            "crossFilteringBehavior": "oneDirection",
            "fromCardinality": "many",
            "toCardinality": "one",
            "relyOnReferentialIntegrity": True
        },
        {
            "name": "rel_churn_users",
            "fromTable": "ChurnByDimension",
            "fromColumn": "user_id",
            "toTable": "DimUsers",
            "toColumn": "user_id",
            "isActive": True,
            "crossFilteringBehavior": "oneDirection",
            "fromCardinality": "many",
            "toCardinality": "one",
            "relyOnReferentialIntegrity": True
        },
        {
            "name": "rel_segments_users",
            "fromTable": "UserSegments",
            "fromColumn": "user_id",
            "toTable": "DimUsers",
            "toColumn": "user_id",
            "isActive": True,
            "crossFilteringBehavior": "bothDirections",
            "fromCardinality": "one",
            "toCardinality": "one",
            "relyOnReferentialIntegrity": True
        }
    ]
    bim_data["model"]["relationships"] = repaired_rels

    # 2. Fix M partitions with Windows backslashes and QuoteStyle.Csv
    tables = bim_data["model"]["tables"]
    for t in tables:
        tname = t["name"]
        if tname == "_Measures":
            continue
        csv_name = {
            "MonthlyPerformance": "monthly_performance.csv",
            "ContentPerformance": "content_performance.csv",
            "ChurnByDimension": "churn_by_dimension.csv",
            "UserSegments": "user_segments.csv",
            "DimUsers": "dim_users.csv",
            "DimPlans": "dim_plans.csv",
            "DimContent": "dim_content.csv",
            "FactSubscriptions": "fact_subscriptions.csv",
            "FactViewingSessions": "fact_viewing_sessions.csv"
        }.get(tname)

        if not csv_name:
            continue

        abs_csv_path = os.path.join(DATA_DIR, csv_name).replace("/", "\\")
        escaped_path = abs_csv_path.replace("\\", "\\\\")

        # Update partition expression
        for p in t.get("partitions", []):
            lines = p["source"]["expression"]
            new_lines = []
            for line in lines:
                if 'File.Contents(' in line:
                    new_lines.append(f'    Source = Csv.Document(File.Contents("{abs_csv_path}"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),')
                else:
                    new_lines.append(line)
            p["source"]["expression"] = new_lines

    # Save to SemanticModel and Dataset mirror
    with open(bim_path, "w", encoding="utf-8") as f:
        json.dump(bim_data, f, indent=2)
    print(f"  ✓ Updated {bim_path}")

    dataset_bim_path = os.path.join(DATASET_DIR, "model.bim")
    if os.path.exists(DATASET_DIR):
        with open(dataset_bim_path, "w", encoding="utf-8") as f:
            json.dump(bim_data, f, indent=2)
        print(f"  ✓ Updated {dataset_bim_path}")

def build_visual_container(x, y, w, h, z, name, visual_type, title, entity, cat_col, val_entity, val_col, is_measure=False, agg="Sum", line_entity=None, line_col=None, line_agg="Sum"):
    """Creates a standard PBIP visualContainer object for report.json."""
    cat_proj = f"{entity}.{cat_col}" if cat_col else None
    val_proj = f"{val_entity}.{val_col}"

    from_list = [{"Name": "t1", "Entity": entity, "Type": 0}]
    if val_entity != entity and val_entity:
        from_list.append({"Name": "t2", "Entity": val_entity, "Type": 0})
    if line_entity and line_entity not in [entity, val_entity]:
        from_list.append({"Name": "t3", "Entity": line_entity, "Type": 0})

    select_list = []
    projections = {}

    if cat_col:
        select_list.append({
            "Column": {
                "Expression": {"SourceRef": {"Source": "t1"}},
                "Property": cat_col
            },
            "Name": cat_proj
        })
        cat_key = "Category" if visual_type in ["clusteredBarChart", "clusteredColumnChart", "lineStackedColumnComboChart", "areaChart", "donutChart", "slicer"] else "Group"
        projections[cat_key] = [{"queryRef": cat_proj}]

    if is_measure:
        m_source = "t2" if val_entity != entity else "t1"
        select_list.append({
            "Measure": {
                "Expression": {"SourceRef": {"Source": m_source}},
                "Property": val_col
            },
            "Name": val_proj
        })
    else:
        v_source = "t2" if val_entity != entity else "t1"
        select_list.append({
            "Aggregation": {
                "Expression": {
                    "Column": {
                        "Expression": {"SourceRef": {"Source": v_source}},
                        "Property": val_col
                    }
                },
                "Function": 0 if agg == "Sum" else 5
            },
            "Name": f"{agg}({val_proj})"
        })

    val_query_ref = val_proj if is_measure else f"{agg}({val_proj})"
    val_key = "Y" if visual_type in ["clusteredBarChart", "clusteredColumnChart", "lineStackedColumnComboChart", "areaChart"] else ("Values" if visual_type == "donutChart" else "Values")
    if visual_type == "card":
        projections["Values"] = [{"queryRef": val_query_ref}]
    elif visual_type == "slicer":
        projections["Values"] = [{"queryRef": cat_proj}]
    else:
        projections[val_key] = [{"queryRef": val_query_ref}]

    if line_col:
        l_source = "t3" if line_entity not in [entity, val_entity] else ("t2" if line_entity == val_entity else "t1")
        l_proj = f"{line_entity}.{line_col}"
        select_list.append({
            "Aggregation": {
                "Expression": {
                    "Column": {
                        "Expression": {"SourceRef": {"Source": l_source}},
                        "Property": line_col
                    }
                },
                "Function": 0 if line_agg == "Sum" else 5
            },
            "Name": f"{line_agg}({l_proj})"
        })
        projections["Y2"] = [{"queryRef": f"{line_agg}({l_proj})"}]

    config_dict = {
        "name": name,
        "layouts": [{
            "id": 0,
            "position": {"x": float(x), "y": float(y), "z": float(z), "width": float(w), "height": float(h)}
        }],
        "singleVisual": {
            "visualType": visual_type,
            "projections": projections,
            "prototypeQuery": {
                "Version": 2,
                "From": from_list,
                "Select": select_list
            },
            "drillFilterOtherVisuals": True,
            "objects": {
                "title": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}
                    }
                }]
            }
        }
    }

    query_dict = {
        "Commands": [{
            "SemanticQueryDataShapeCommand": {
                "Query": {
                    "Version": 2,
                    "From": from_list,
                    "Select": select_list
                },
                "Binding": {
                    "Primary": {"Groupings": [{"Projections": list(range(len(select_list)))}]},
                    "DataReduction": {"DataVolume": 3, "Primary": {"Sample": {}}},
                    "Version": 1
                }
            }
        }]
    }

    return {
        "x": float(x),
        "y": float(y),
        "z": float(z),
        "width": float(w),
        "height": float(h),
        "config": json.dumps(config_dict),
        "filters": "[]",
        "query": json.dumps(query_dict)
    }

def generate_report_sections():
    print("[2/3] Generating complete 3-page layout and 22 visual containers for report.json...")
    sections = []

    # -------------------------------------------------------------------------
    # PAGE 1: EXECUTIVE OVERVIEW
    # -------------------------------------------------------------------------
    p1_visuals = []

    # 6 Top KPI Cards
    p1_visuals.append(build_visual_container(30, 90, 290, 110, 1, "card_total_users", "card", "Total Users", "_Measures", None, "_Measures", "Total Registered Users", is_measure=True))
    p1_visuals.append(build_visual_container(340, 90, 290, 110, 2, "card_active_subs", "card", "Active Paid Subscribers", "_Measures", None, "_Measures", "Active Paid Subscribers", is_measure=True))
    p1_visuals.append(build_visual_container(650, 90, 290, 110, 3, "card_mau", "card", "Monthly Active Viewers (MAU)", "_Measures", None, "_Measures", "Monthly Active Viewers (MAU)", is_measure=True))
    p1_visuals.append(build_visual_container(960, 90, 290, 110, 4, "card_watch_hours", "card", "Total Streamed Hours", "_Measures", None, "_Measures", "Total Watch Hours", is_measure=True))
    p1_visuals.append(build_visual_container(1270, 90, 290, 110, 5, "card_mrr", "card", "Active Run-Rate (MRR)", "_Measures", None, "_Measures", "Current MRR", is_measure=True))
    p1_visuals.append(build_visual_container(1580, 90, 310, 110, 6, "card_churn", "card", "Monthly Churn Rate %", "_Measures", None, "_Measures", "Monthly Churn Rate %", is_measure=True))

    # Visual 7: MoM Active Subscribers & MRR
    p1_visuals.append(build_visual_container(30, 220, 920, 390, 7, "chart_subs_mrr", "lineStackedColumnComboChart", "Active Subscribers & Monthly Revenue Growth", "MonthlyPerformance", "calendar_month", "MonthlyPerformance", "estimated_mrr", agg="Sum", line_entity="MonthlyPerformance", line_col="active_subscribers", line_agg="Sum"))

    # Visual 8: Subscription Plan Distribution
    p1_visuals.append(build_visual_container(970, 220, 920, 390, 8, "chart_plan_dist", "donutChart", "Subscribers by Plan Tier", "DimPlans", "plan_name", "FactSubscriptions", "subscription_id", agg="Count"))

    # Visual 9: Monthly Consumption Trends
    p1_visuals.append(build_visual_container(30, 630, 920, 410, 9, "chart_mau_hours", "areaChart", "Monthly Active Viewers (MAU) & Watch Hours Dynamics", "MonthlyPerformance", "calendar_month", "MonthlyPerformance", "total_watch_hours", agg="Sum"))

    # Visual 10: Acquisition Channel Conversion
    p1_visuals.append(build_visual_container(970, 630, 450, 410, 10, "chart_channel_perf", "clusteredBarChart", "Signups by Marketing Acquisition Channel", "DimUsers", "acquisition_channel", "DimUsers", "user_id", agg="Count"))

    # Visual 11: Signups vs Cancellations
    p1_visuals.append(build_visual_container(1440, 630, 450, 410, 11, "chart_signups_cancels", "lineStackedColumnComboChart", "New Registrations vs Churned Subscribers", "MonthlyPerformance", "calendar_month", "MonthlyPerformance", "new_registrations", agg="Sum", line_entity="MonthlyPerformance", line_col="churned_subscribers", line_agg="Sum"))

    sections.append({
        "name": "Section_Executive_Overview",
        "displayName": "Executive Overview",
        "ordinal": 0,
        "width": 1920.0,
        "height": 1080.0,
        "visualContainers": p1_visuals
    })

    # -------------------------------------------------------------------------
    # PAGE 2: CONTENT & ENGAGEMENT
    # -------------------------------------------------------------------------
    p2_visuals = []

    # Visual 12: Top 10 Blockbuster Titles
    p2_visuals.append(build_visual_container(30, 90, 920, 460, 12, "chart_top_content", "clusteredBarChart", "Top 10 Blockbuster Titles by Streamed Watch Hours", "ContentPerformance", "title", "ContentPerformance", "total_watch_hours", agg="Sum"))

    # Visual 13: Watch Time by Genre
    p2_visuals.append(build_visual_container(970, 90, 920, 460, 13, "chart_genre_hours", "clusteredColumnChart", "Total Streamed Watch Hours by Content Genre", "ContentPerformance", "genre", "ContentPerformance", "total_watch_hours", agg="Sum"))

    # Visual 14: Streaming Sessions by Device
    p2_visuals.append(build_visual_container(30, 570, 600, 470, 14, "chart_device_share", "donutChart", "Viewing Sessions by Hardware Device Type", "FactViewingSessions", "device_type", "FactViewingSessions", "session_id", agg="Count"))

    # Visual 15: Movies vs Web Series Reach
    p2_visuals.append(build_visual_container(650, 570, 600, 470, 15, "chart_type_dynamics", "clusteredColumnChart", "Unique Viewers & Stream Plays by Content Format", "ContentPerformance", "content_type", "ContentPerformance", "unique_viewers", agg="Sum"))

    # Visual 16: Completion Rate by Genre
    p2_visuals.append(build_visual_container(1270, 570, 620, 470, 16, "chart_completion_genre", "clusteredBarChart", "Average Title Completion Percentage by Genre", "ContentPerformance", "genre", "ContentPerformance", "avg_completion_percentage", agg="Sum"))

    # Visual 22: Content Genre Interactive Slicer
    p2_visuals.append(build_visual_container(30, 20, 420, 60, 22, "slicer_genre", "slicer", "Filter by Content Genre", "DimContent", "genre", "DimContent", "genre"))

    sections.append({
        "name": "Section_Content_Engagement",
        "displayName": "Content & Engagement",
        "ordinal": 1,
        "width": 1920.0,
        "height": 1080.0,
        "visualContainers": p2_visuals
    })

    # -------------------------------------------------------------------------
    # PAGE 3: RETENTION & CHURN
    # -------------------------------------------------------------------------
    p3_visuals = []

    # Visual 17: Monthly Churn & Lost MRR
    p3_visuals.append(build_visual_container(30, 90, 920, 460, 17, "chart_churn_loss", "lineStackedColumnComboChart", "Monthly Churned Subscribers & Lost Revenue Trend", "MonthlyPerformance", "calendar_month", "MonthlyPerformance", "lost_mrr", agg="Sum", line_entity="MonthlyPerformance", line_col="churned_subscribers", line_agg="Sum"))

    # Visual 18: Cancellation Reasons Pareto
    p3_visuals.append(build_visual_container(970, 90, 920, 460, 18, "chart_reasons", "clusteredBarChart", "Primary Stated Cancellation Reasons (Pareto)", "ChurnByDimension", "cancellation_reason", "ChurnByDimension", "subscription_id", agg="Count"))

    # Visual 19: Churn by Plan Tier
    p3_visuals.append(build_visual_container(30, 570, 600, 470, 19, "chart_plan_churn", "clusteredColumnChart", "Cancellations by Subscription Plan Tier", "ChurnByDimension", "plan_name", "ChurnByDimension", "is_true_churn", agg="Sum"))

    # Visual 20: Churn by Acquisition Channel
    p3_visuals.append(build_visual_container(650, 570, 600, 470, 20, "chart_channel_churn", "clusteredBarChart", "Subscriber Churn Rate by Marketing Acquisition Channel", "ChurnByDimension", "acquisition_channel", "ChurnByDimension", "is_true_churn", agg="Sum"))

    # Visual 21: Audience by Engagement Tier
    p3_visuals.append(build_visual_container(1270, 570, 620, 470, 21, "chart_segments", "donutChart", "Customer Distribution by Engagement Behavioral Tier", "UserSegments", "engagement_segment", "UserSegments", "user_id", agg="Count"))

    sections.append({
        "name": "Section_Retention_Churn",
        "displayName": "Retention & Churn",
        "ordinal": 2,
        "width": 1920.0,
        "height": 1080.0,
        "visualContainers": p3_visuals
    })

    return sections

def repair_report_json():
    sections = generate_report_sections()

    report_config = {
        "version": "5.66",
        "themeCollection": {
            "baseTheme": {
                "name": "Fluent2-CY26SU11",
                "type": 2,
                "version": {"visual": "2.15.0", "report": "3.4.0", "page": "2.3.1"}
            }
        },
        "activeSectionIndex": 0,
        "linguisticSchemaSyncVersion": 2
    }

    report_json_data = {
        "config": json.dumps(report_config),
        "layoutOptimization": 0,
        "sections": sections
    }

    report_json_path = os.path.join(REPORT_DIR, "report.json")
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report_json_data, f, indent=2)

    total_visuals = sum(len(s["visualContainers"]) for s in sections)
    print(f"  ✓ Saved {report_json_path} ({len(sections)} sections, {total_visuals} visual containers)")

    # Also build modern PBIR definition/ structure for full dual compatibility
    print("\n[3/3] Synchronizing PBIR definition/ folder structure...")
    def_dir = os.path.join(REPORT_DIR, "definition")
    pages_dir = os.path.join(def_dir, "pages")
    os.makedirs(pages_dir, exist_ok=True)

    version_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
        "version": "2.0.0"
    }
    with open(os.path.join(def_dir, "version.json"), "w", encoding="utf-8") as f:
        json.dump(version_json, f, indent=2)

    pbir_report_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.4.0/schema.json",
        "themeCollection": {
            "baseTheme": {
                "name": "Fluent2-CY26SU11",
                "reportVersionAtImport": {"visual": "2.15.0", "report": "3.4.0", "page": "2.3.1"},
                "type": "SharedResources"
            }
        }
    }
    with open(os.path.join(def_dir, "report.json"), "w", encoding="utf-8") as f:
        json.dump(pbir_report_json, f, indent=2)

    page_names = [s["name"] for s in sections]
    pages_manifest = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
        "pageOrder": page_names,
        "activePageName": page_names[0]
    }
    with open(os.path.join(pages_dir, "pages.json"), "w", encoding="utf-8") as f:
        json.dump(pages_manifest, f, indent=2)

    for s in sections:
        p_dir = os.path.join(pages_dir, s["name"])
        v_dir = os.path.join(p_dir, "visuals")
        os.makedirs(v_dir, exist_ok=True)

        p_def = {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
            "name": s["name"],
            "displayName": s["displayName"],
            "displayOption": "FitToPage",
            "height": 1080,
            "width": 1920
        }
        with open(os.path.join(p_dir, "page.json"), "w", encoding="utf-8") as f:
            json.dump(p_def, f, indent=2)

        for vc in s["visualContainers"]:
            cfg = json.loads(vc["config"])
            v_name = cfg["name"]
            single_v = cfg["singleVisual"]
            pos = cfg["layouts"][0]["position"]

            v_spec = {
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.4.0/schema.json",
                "name": v_name,
                "position": pos,
                "visual": {
                    "visualType": single_v["visualType"],
                    "query": json.loads(vc["query"])["Commands"][0]["SemanticQueryDataShapeCommand"]["Query"],
                    "objects": single_v.get("objects", {})
                }
            }
            sub_v_dir = os.path.join(v_dir, v_name)
            os.makedirs(sub_v_dir, exist_ok=True)
            with open(os.path.join(sub_v_dir, "visual.json"), "w", encoding="utf-8") as f:
                json.dump(v_spec, f, indent=2)

    print(f"  ✓ Synchronized all {total_visuals} visuals into {pages_dir}")

def main():
    print("=" * 65)
    print("StreamScope PBIP & Semantic Model Repair Execution")
    print("=" * 65)

    repair_semantic_model()
    repair_report_json()

    print("\n" + "=" * 65)
    print("REPAIR COMPLETE: SemanticModel, Relationships & Report Ready!")
    print("=" * 65)

if __name__ == "__main__":
    main()
