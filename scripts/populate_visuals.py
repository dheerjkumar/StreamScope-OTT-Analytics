import json, pathlib, sys

# Mapping of visual IDs to desired query definitions
# The mapping uses the visual filename (without extension) as key.

# Helper to build a simple measure projection
def measure_proj(measure_name):
    return {
        "field": {"Measure": {"Expression": {"Literal": {"Value": f'[{measure_name}]'}}}},
        "queryRef": measure_name
    }

# Helper to build a simple column projection (for categories)
def column_proj(table, column, alias=None):
    alias = alias or column
    return {
        "field": {"Column": {"Expression": {"SourceRef": {"Entity": f'streamscope {table}'}}, "Property": column}},
        "queryRef": f"{table}.{column}"
    }

# Build visual queryState for cards (single measure)
def card_query(measure):
    return {"Values": {"projections": [measure_proj(measure)]}}

# Build bar chart query with Category and Y (measure)
def bar_chart_query(category_table, category_col, y_measure):
    return {
        "Category": {"projections": [column_proj(category_table, category_col)]},
        "Y": {"projections": [measure_proj(y_measure)]}
    }

# Build line chart for time series (Category = calendar_month from MonthlyPerformance)
def line_chart_query(y_measure):
    return {
        "Category": {"projections": [column_proj('MonthlyPerformance', 'calendar_month')]},
        "Y": {"projections": [measure_proj(y_measure)]}
    }

# Define visual specifications
visuals = {
    # Executive Overview cards
    "card_total_users": {"type": "card", "measure": "Total Registered Users"},
    "card_active_subs": {"type": "card", "measure": "Active Paid Subscribers"},
    "card_mau": {"type": "card", "measure": "Monthly Active Viewers (MAU)"},
    "card_watch_hours": {"type": "card", "measure": "Total Watch Hours"},
    "card_mrr": {"type": "card", "measure": "Current MRR"},
    "card_churn": {"type": "card", "measure": "Monthly Churn Rate %"},
    # Executive Overview charts
    "chart_mau_hours": {"type": "line", "y_measure": "Monthly Active Viewers (MAU)"},
    "chart_subs_mrr": {"type": "line", "y_measure": "Current MRR"},
    "chart_plan_dist": {"type": "donut", "category_table": "DimPlans", "category_col": "plan_name", "y_measure": "Converted Paying Subscribers"},
    "chart_signups_cancels": {"type": "bar", "category_table": "MonthlyPerformance", "category_col": "calendar_month", "y_measure": "new_registrations"},
    "chart_channel_perf": {"type": "line", "y_measure": "active_viewers_mau"},
    # Content & Engagement
    "chart_top_content": {"type": "bar", "category_table": "ContentPerformance", "category_col": "title", "y_measure": "total_watch_hours"},
    "chart_genre_hours": {"type": "bar", "category_table": "ContentPerformance", "category_col": "genre", "y_measure": "total_watch_hours"},
    "chart_device_share": {"type": "donut", "category_table": "FactViewingSessions", "category_col": "device_type", "y_measure": "total_plays"},
    "chart_completion_genre": {"type": "bar", "category_table": "ContentPerformance", "category_col": "genre", "y_measure": "avg_completion_percentage"},
    "chart_type_dynamics": {"type": "bar", "category_table": "ContentPerformance", "category_col": "content_type", "y_measure": "total_watch_hours"},
    "slicer_genre": {"type": "slicer", "category_table": "ContentPerformance", "category_col": "genre"},
    # Retention & Churn
    "chart_channel_churn": {"type": "line", "y_measure": "True Churned Subscribers"},
    "chart_churn_loss": {"type": "line", "y_measure": "lost_mrr"},
    "chart_plan_churn": {"type": "bar", "category_table": "DimPlans", "category_col": "plan_name", "y_measure": "True Churned Subscribers"},
    "chart_reasons": {"type": "pie", "category_table": "ChurnByDimension", "category_col": "cancellation_reason", "y_measure": "True Churned Subscribers"},
    "chart_segments": {"type": "bar", "category_table": "UserSegments", "category_col": "engagement_segment", "y_measure": "DistinctCount(UserSegments[user_id])"},
}

base_path = pathlib.Path('powerbi/StreamScope_Analytics.Report/definition/pages')

for page_dir in base_path.iterdir():
    if not page_dir.is_dir():
        continue
    visuals_dir = page_dir / 'visuals'
    if not visuals_dir.exists():
        continue
    for visual_folder in visuals_dir.iterdir():
        if not visual_folder.is_dir():
            continue
        visual_id = visual_folder.name
        visual_file = visual_folder / 'visual.json'
        if not visual_file.exists():
            continue
        spec = visuals.get(visual_id)
        if not spec:
            # No mapping – leave as is
            continue
        # Load existing JSON
        with open(visual_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Build queryState according to type
        if spec['type'] == 'card':
            query_state = card_query(spec['measure'])
        elif spec['type'] == 'line':
            query_state = line_chart_query(spec['y_measure'])
        elif spec['type'] == 'bar':
            query_state = bar_chart_query(spec['category_table'], spec['category_col'], spec['y_measure'])
        elif spec['type'] == 'donut' or spec['type'] == 'pie':
            # Use same as bar but visual type differs – schema uses Category and Values
            query_state = {
                "Category": {"projections": [column_proj(spec['category_table'], spec['category_col'])]},
                "Values": {"projections": [measure_proj(spec['y_measure'])]}
            }
        elif spec['type'] == 'slicer':
            query_state = {"Values": {"projections": [column_proj(spec['category_table'], spec['category_col'])]}}
        else:
            continue
        # Insert queryState
        if 'visual' not in data:
            data['visual'] = {}
        data['visual']['query'] = {"queryState": query_state}
        # Write back
        with open(visual_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f'Updated {visual_id}')

print('All done')
