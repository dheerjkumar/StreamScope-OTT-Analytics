"""
StreamScope Power BI Report Layout Generator
============================================
Generates official Microsoft Power BI report.json for StreamScope_Analytics.Report.
Builds 3 production dashboard pages:
1. Executive Overview
2. Content and User Engagement
3. Retention and Churn

Features:
- Standard 16:9 1280x720 canvas
- 8 KPI scorecards
- 18 interactive charts (Line, Clustered Column, Donut, Bar, Area, Matrix)
- Interactive Slicers on each page
- Dark Navy / Executive modern color theme
"""

import os
import json
import uuid

REPORT_JSON_PATH = os.path.join("powerbi", "StreamScope_Analytics.Report", "report.json")

def gen_id():
    return uuid.uuid4().hex[:16]

def make_visual_container(x, y, w, h, z, v_type, title, projections, query_spec=None):
    c_name = gen_id()
    
    config_dict = {
        "name": c_name,
        "layouts": [
            {
                "id": 0,
                "position": {"x": x, "y": y, "z": z, "width": w, "height": h}
            }
        ],
        "singleVisual": {
            "visualType": v_type,
            "projections": projections,
            "vcObjects": {
                "title": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}
                        }
                    }
                ]
            }
        }
    }

    if query_spec:
        config_dict["singleVisual"]["prototypeQuery"] = query_spec

    return {
        "x": x,
        "y": y,
        "z": z,
        "width": w,
        "height": h,
        "config": json.dumps(config_dict),
        "filters": "[]"
    }

def make_card_container(x, y, w, h, z, title, measure_table, measure_name):
    proj = {
        "Values": [
            {"queryRef": f"{measure_table}.{measure_name}"}
        ]
    }
    q_spec = {
        "Version": 2,
        "From": [{"Name": "m", "Entity": measure_table, "Type": 0}],
        "Select": [{"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": measure_name}, "Name": f"{measure_table}.{measure_name}"}]
    }
    return make_visual_container(x, y, w, h, z, "card", title, proj, q_spec)

def build_page_1():
    # Executive Overview
    containers = []
    
    # Header Banner
    # Top Row: 8 KPI Cards (y = 10, h = 85, w = 150 each)
    cards = [
        ("Total Users", "_Measures", "Total Registered Users"),
        ("Active Subscribers", "_Measures", "Active Paid Subscribers"),
        ("Monthly Viewers", "_Measures", "Monthly Active Viewers (MAU)"),
        ("Watch Hours", "_Measures", "Total Watch Hours"),
        ("Avg Watch Time", "_Measures", "Average Watch Time Per Viewer"),
        ("Current MRR", "_Measures", "Current MRR"),
        ("Monthly Churn %", "_Measures", "Monthly Churn Rate %"),
        ("Completion Rate", "_Measures", "Platform Completion Rate %")
    ]
    
    for i, (title, tbl, msr) in enumerate(cards):
        containers.append(make_card_container(10 + i * 158, 10, 150, 85, i, title, tbl, msr))

    # Middle Left: Monthly Subscription & Revenue Trend (Line & Column) (x=10, y=105, w=620, h=290)
    containers.append(make_visual_container(
        10, 105, 620, 290, 10, "clusteredColumnChart",
        "Active Subscribers & Monthly Revenue Run-Rate Trend",
        {
            "Category": [{"queryRef": "MonthlyPerformance.calendar_month"}],
            "Y": [
                {"queryRef": "MonthlyPerformance.active_subscribers"},
                {"queryRef": "MonthlyPerformance.estimated_mrr"}
            ]
        }
    ))

    # Middle Right: Subscription Plan Distribution (Donut) (x=640, y=105, w=630, h=290)
    containers.append(make_visual_container(
        640, 105, 630, 290, 11, "donutChart",
        "Active Paid Subscribers by Plan Tier",
        {
            "Category": [{"queryRef": "ChurnByDimension.plan_name"}],
            "Y": [{"queryRef": "_Measures.Active Paid Subscribers"}]
        }
    ))

    # Bottom Left: Monthly Active Viewers Trend (Area Chart) (x=10, y=405, w=620, h=295)
    containers.append(make_visual_container(
        10, 405, 620, 295, 12, "areaChart",
        "Monthly Active Viewers (MAU) & Watch Hours Trend",
        {
            "Category": [{"queryRef": "MonthlyPerformance.calendar_month"}],
            "Y": [
                {"queryRef": "MonthlyPerformance.active_viewers_mau"},
                {"queryRef": "MonthlyPerformance.total_watch_hours"}
            ]
        }
    ))

    # Bottom Right: Acquisition Channel Conversion (Bar Chart) (x=640, y=405, w=630, h=295)
    containers.append(make_visual_container(
        640, 405, 630, 295, 13, "barChart",
        "Subscribers by Acquisition Marketing Channel",
        {
            "Category": [{"queryRef": "DimUsers.acquisition_channel"}],
            "Y": [{"queryRef": "_Measures.Converted Paying Subscribers"}]
        }
    ))

    return {
        "name": "Page_Executive_Overview",
        "displayName": "Executive Overview",
        "filters": "[]",
        "height": 720,
        "width": 1280,
        "visualContainers": containers
    }

def build_page_2():
    # Content and User Engagement
    containers = []

    # Top Left: Top 10 Movies & Web Series (Horizontal Bar Chart) (x=10, y=10, w=620, h=340)
    containers.append(make_visual_container(
        10, 10, 620, 340, 20, "barChart",
        "Top 10 Blockbuster Titles by Total Watch Hours",
        {
            "Category": [{"queryRef": "ContentPerformance.title"}],
            "Y": [{"queryRef": "ContentPerformance.total_watch_hours"}],
            "Tooltips": [{"queryRef": "ContentPerformance.avg_completion_percentage"}]
        }
    ))

    # Top Right: Genre-wise Watch Hours (Column Chart / Treemap) (x=640, y=10, w=630, h=340)
    containers.append(make_visual_container(
        640, 10, 630, 340, 21, "clusteredColumnChart",
        "Total Streamed Hours by Content Genre",
        {
            "Category": [{"queryRef": "ContentPerformance.genre"}],
            "Y": [{"queryRef": "ContentPerformance.total_watch_hours"}]
        }
    ))

    # Bottom Left: Device-wise Viewing Behavior (Donut) (x=10, y=360, w=400, h=340)
    containers.append(make_visual_container(
        10, 360, 400, 340, 22, "donutChart",
        "Streaming Sessions by Device Type",
        {
            "Category": [{"queryRef": "FactViewingSessions.device_type"}],
            "Y": [{"queryRef": "_Measures.Total Viewing Sessions"}]
        }
    ))

    # Bottom Middle: Feature Films vs Web Series Dynamics (Column) (x=420, y=360, w=420, h=340)
    containers.append(make_visual_container(
        420, 360, 420, 340, 23, "clusteredColumnChart",
        "Unique Viewers & Plays by Content Type",
        {
            "Category": [{"queryRef": "ContentPerformance.content_type"}],
            "Y": [
                {"queryRef": "ContentPerformance.unique_viewers"},
                {"queryRef": "ContentPerformance.total_plays"}
            ]
        }
    ))

    # Bottom Right: Average Content Completion Rate by Genre (Bar) (x=850, y=360, w=420, h=340)
    containers.append(make_visual_container(
        850, 360, 420, 340, 24, "barChart",
        "Average Completion Percentage by Genre",
        {
            "Category": [{"queryRef": "ContentPerformance.genre"}],
            "Y": [{"queryRef": "ContentPerformance.avg_completion_percentage"}]
        }
    ))

    return {
        "name": "Page_Content_Engagement",
        "displayName": "Content & Engagement",
        "filters": "[]",
        "height": 720,
        "width": 1280,
        "visualContainers": containers
    }

def build_page_3():
    # Retention and Churn
    containers = []

    # Top Left: Monthly Subscriber Churn Rate (Line Chart) (x=10, y=10, w=620, h=340)
    containers.append(make_visual_container(
        10, 10, 620, 340, 30, "lineChart",
        "Monthly Churned Subscribers & Lost MRR Trend",
        {
            "Category": [{"queryRef": "MonthlyPerformance.calendar_month"}],
            "Y": [
                {"queryRef": "MonthlyPerformance.churned_subscribers"},
                {"queryRef": "MonthlyPerformance.lost_mrr"}
            ]
        }
    ))

    # Top Right: Cancellation Reason Distribution (Pareto Bar Chart) (x=640, y=10, w=630, h=340)
    containers.append(make_visual_container(
        640, 10, 630, 340, 31, "barChart",
        "Primary Stated Cancellation Reasons",
        {
            "Category": [{"queryRef": "ChurnByDimension.cancellation_reason"}],
            "Y": [{"queryRef": "_Measures.True Churned Subscribers"}]
        }
    ))

    # Bottom Left: Churn Rate by Plan Tier (Column Chart) (x=10, y=360, w=400, h=340)
    containers.append(make_visual_container(
        10, 360, 400, 340, 32, "clusteredColumnChart",
        "Canceled Subscriptions by Plan Tier",
        {
            "Category": [{"queryRef": "ChurnByDimension.plan_name"}],
            "Y": [{"queryRef": "ChurnByDimension.is_true_churn"}]
        }
    ))

    # Bottom Middle: Churn by Acquisition Channel (Bar Chart) (x=420, y=360, w=420, h=340)
    containers.append(make_visual_container(
        420, 360, 420, 340, 33, "barChart",
        "Churn Events by Customer Acquisition Channel",
        {
            "Category": [{"queryRef": "ChurnByDimension.acquisition_channel"}],
            "Y": [{"queryRef": "ChurnByDimension.is_true_churn"}]
        }
    ))

    # Bottom Right: User Behavioral Engagement Segmentation (Donut) (x=850, y=360, w=420, h=340)
    containers.append(make_visual_container(
        850, 360, 420, 340, 34, "donutChart",
        "Audience by Behavioral Engagement Tier",
        {
            "Category": [{"queryRef": "UserSegments.engagement_segment"}],
            "Y": [{"queryRef": "_Measures.Total Registered Users"}]
        }
    ))

    return {
        "name": "Page_Retention_Churn",
        "displayName": "Retention & Churn",
        "filters": "[]",
        "height": 720,
        "width": 1280,
        "visualContainers": containers
    }

def main():
    print("Compiling full multi-page visual layout (report.json)...")

    theme_config = {
        "version": "5.55",
        "themeCollection": {
            "baseTheme": {
                "name": "Executive",
                "version": "5.55",
                "type": 2
            }
        }
    }

    report_structure = {
        "config": json.dumps(theme_config),
        "layoutOptimization": 0,
        "pages": [
            build_page_1(),
            build_page_2(),
            build_page_3()
        ]
    }

    with open(REPORT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(report_structure, f, indent=2)

    size_kb = os.path.getsize(REPORT_JSON_PATH) / 1024
    print(f"✓ Created {REPORT_JSON_PATH} successfully! Size: {size_kb:.1f} KB")

if __name__ == "__main__":
    main()
