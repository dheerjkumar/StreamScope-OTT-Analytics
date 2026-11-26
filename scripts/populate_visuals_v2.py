import json, pathlib, sys, re

# Helper to build projection for a measure (DAX) or column

def measure_proj(measure_name):
    return {
        "field": {"Measure": {"Expression": {"Literal": {"Value": f'[{measure_name}]'}}}},
        "queryRef": measure_name
    }

def column_proj(table, column):
    return {
        "field": {"Column": {"Expression": {"SourceRef": {"Entity": f'streamscope {table}'}}, "Property": column}},
        "queryRef": f"{table}.{column}"
    }

# Load model to discover columns per table
model_path = pathlib.Path('powerbi/StreamScope_Analytics.SemanticModel/model.bim')
model = json.load(open(model_path, 'r', encoding='utf-8'))
columns_by_table = {}
for tbl in model['model']['tables']:
    cols = {c['name'] for c in tbl.get('columns', [])}
    columns_by_table[tbl['name']] = cols

# Visual specifications – note whether y is a measure (True) or column (False)
visuals = {
    # Executive Overview cards (measures)
    "card_total_users": {"type": "card", "measure": "Total Registered Users"},
    "card_active_subs": {"type": "card", "measure": "Active Paid Subscribers"},
    "card_mau": {"type": "card", "measure": "Monthly Active Viewers (MAU)"},
    "card_watch_hours": {"type": "card", "measure": "Total Watch Hours"},
    "card_mrr": {"type": "card", "measure": "Current MRR"},
    "card_churn": {"type": "card", "measure": "Monthly Churn Rate %"},
    # Executive Overview charts
    "chart_mau_hours": {"type": "line", "y": {"table": "MonthlyPerformance", "field": "active_viewers_mau"}},
    "chart_subs_mrr": {"type": "line", "y": {"table": "MonthlyPerformance", "field": "estimated_mrr"}},
    "chart_plan_dist": {"type": "donut", "category": {"table": "DimPlans", "field": "plan_name"}, "y": {"measure": "Converted Paying Subscribers"}},
    "chart_signups_cancels": {"type": "bar", "category": {"table": "MonthlyPerformance", "field": "calendar_month"}, "y": {"table": "MonthlyPerformance", "field": "new_registrations"}},
    "chart_channel_perf": {"type": "line", "y": {"table": "MonthlyPerformance", "field": "active_viewers_mau"}},
    # Content & Engagement
    "chart_top_content": {"type": "bar", "category": {"table": "ContentPerformance", "field": "title"}, "y": {"table": "ContentPerformance", "field": "total_watch_hours"}},
    "chart_genre_hours": {"type": "bar", "category": {"table": "ContentPerformance", "field": "genre"}, "y": {"table": "ContentPerformance", "field": "total_watch_hours"}},
    "chart_device_share": {"type": "donut", "category": {"table": "FactViewingSessions", "field": "device_type"}, "y": {"table": "FactViewingSessions", "field": "total_plays"}},
    "chart_completion_genre": {"type": "bar", "category": {"table": "ContentPerformance", "field": "genre"}, "y": {"table": "ContentPerformance", "field": "avg_completion_percentage"}},
    "chart_type_dynamics": {"type": "bar", "category": {"table": "ContentPerformance", "field": "content_type"}, "y": {"table": "ContentPerformance", "field": "total_watch_hours"}},
    "slicer_genre": {"type": "slicer", "category": {"table": "ContentPerformance", "field": "genre"}},
    # Retention & Churn
    "chart_channel_churn": {"type": "line", "y": {"measure": "True Churned Subscribers"}},
    "chart_churn_loss": {"type": "line", "y": {"measure": "lost_mrr"}},
    "chart_plan_churn": {"type": "bar", "category": {"table": "DimPlans", "field": "plan_name"}, "y": {"measure": "True Churned Subscribers"}},
    "chart_reasons": {"type": "pie", "category": {"table": "ChurnByDimension", "field": "cancellation_reason"}, "y": {"measure": "True Churned Subscribers"}},
    "chart_segments": {"type": "bar", "category": {"table": "UserSegments", "field": "engagement_segment"}, "y": {"measure": "Active Paid Subscribers"}},
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
            continue
        data = json.load(open(visual_file, 'r', encoding='utf-8'))
        query_state = {}
        # Build query based on type
        if spec['type'] == 'card':
            query_state = {"Values": {"projections": [measure_proj(spec['measure'])]}}
        elif spec['type'] in ('line', 'bar'):
            # Category if present
            if 'category' in spec:
                cat = spec['category']
                query_state['Category'] = {"projections": [column_proj(cat['table'], cat['field'])]}
            # Y – decide measure or column
            y = spec['y']
            if 'measure' in y:
                query_state['Y'] = {"projections": [measure_proj(y['measure'])]}
            else:
                query_state['Y'] = {"projections": [column_proj(y['table'], y['field'])]}
        elif spec['type'] in ('donut', 'pie'):
            cat = spec['category']
            query_state['Category'] = {"projections": [column_proj(cat['table'], cat['field'])]}
            y = spec['y']
            if 'measure' in y:
                query_state['Values'] = {"projections": [measure_proj(y['measure'])]}
            else:
                query_state['Values'] = {"projections": [column_proj(y['table'], y['field'])]}
        elif spec['type'] == 'slicer':
            cat = spec['category']
            query_state = {"Values": {"projections": [column_proj(cat['table'], cat['field'])]}}
        else:
            continue
        data.setdefault('visual', {})['query'] = {"queryState": query_state}
        json.dump(data, open(visual_file, 'w', encoding='utf-8'), indent=2)
        print(f'Updated {visual_id}')

print('All visuals populated')
