"""
StreamScope TMSL Model Generator
================================
Generates official Microsoft Power BI TMSL model.bim for StreamScope_Analytics.Dataset.
Includes:
- 10 Tables (Dimensions, Facts, Pre-Aggregated Views, and Dedicated DAX Measures)
- Star Schema Relationships
- 15+ Production DAX Measures
- Robust Power Query M partition expressions loading from local project data
"""

import os
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PBI_DATA_DIR = os.path.join(BASE_DIR, "powerbi", "data").replace("\\", "/")
MODEL_BIM_PATH = os.path.join(BASE_DIR, "powerbi", "StreamScope_Analytics.Dataset", "model.bim")

def create_table_definition(name, csv_filename, columns_spec, is_hidden=False):
    csv_path = f"{PBI_DATA_DIR}/{csv_filename}".replace("\\", "/")
    
    col_defs = []
    col_types_m = []
    for col_name, data_type, format_str in columns_spec:
        c_def = {
            "name": col_name,
            "dataType": data_type,
            "sourceColumn": col_name,
            "summarizeBy": "none" if data_type in ["string", "dateTime"] else "sum"
        }
        if format_str:
            c_def["formatString"] = format_str
        col_defs.append(c_def)
        
        m_type = "type text"
        if data_type == "int64":
            m_type = "Int64.Type"
        elif data_type == "double":
            m_type = "type number"
        elif data_type == "dateTime":
            m_type = "type datetime"
        elif data_type == "boolean":
            m_type = "type logical"
        col_types_m.append(f'{{"{col_name}", {m_type}}}')

    col_types_str = "{" + ", ".join(col_types_m) + "}"

    m_expression = [
        "let",
        f'    Source = Csv.Document(File.Contents("{csv_path}"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),',
        '    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
        f'    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {col_types_str})',
        "in",
        "    ChangedType"
    ]

    return {
        "name": name,
        "isHidden": is_hidden,
        "columns": col_defs,
        "partitions": [
            {
                "name": name,
                "mode": "import",
                "source": {
                    "type": "m",
                    "expression": m_expression
                }
            }
        ]
    }

def generate_model():
    print("Generating comprehensive Power BI TMSL semantic model (model.bim)...")

    # Table 1: _Measures
    measures_table = {
        "name": "_Measures",
        "columns": [
            {
                "name": "RowId",
                "dataType": "int64",
                "sourceColumn": "RowId",
                "isHidden": True
            }
        ],
        "partitions": [
            {
                "name": "_Measures",
                "mode": "import",
                "source": {
                    "type": "m",
                    "expression": [
                        "let",
                        '    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("i45WMlSKjQUA", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [RowId = _t]),',
                        '    ChangedType = Table.TransformColumnTypes(Source,{{"RowId", Int64.Type}})',
                        "in",
                        "    ChangedType"
                    ]
                }
            }
        ],
        "measures": [
            {
                "name": "Total Registered Users",
                "expression": "DISTINCTCOUNT(DimUsers[user_id])",
                "formatString": "#,##0",
                "description": "Total cumulative customer accounts registered."
            },
            {
                "name": "Converted Paying Subscribers",
                "expression": 'CALCULATE(DISTINCTCOUNT(FactSubscriptions[user_id]), FactSubscriptions[status] IN {"Active", "Canceled"})',
                "formatString": "#,##0",
                "description": "Unique users who purchased at least one paid subscription."
            },
            {
                "name": "Conversion Rate %",
                "expression": "DIVIDE([Converted Paying Subscribers], [Total Registered Users], 0) * 100",
                "formatString": "0.0%",
                "description": "Percentage of registered accounts converting to paying subscribers."
            },
            {
                "name": "Active Paid Subscribers",
                "expression": 'CALCULATE(DISTINCTCOUNT(FactSubscriptions[user_id]), FactSubscriptions[status] = "Active")',
                "formatString": "#,##0",
                "description": "Currently active, paying subscribers."
            },
            {
                "name": "Current MRR",
                "expression": 'CALCULATE(SUM(FactSubscriptions[monthly_fee]), FactSubscriptions[status] = "Active")',
                "formatString": "$#,##0",
                "description": "Monthly Recurring Revenue run-rate from active subscriptions."
            },
            {
                "name": "ARPU",
                "expression": "DIVIDE([Current MRR], [Active Paid Subscribers], 0)",
                "formatString": "$#,##0.00",
                "description": "Average Revenue Per Paying Subscriber."
            },
            {
                "name": "Total Watch Hours",
                "expression": "DIVIDE(SUM(FactViewingSessions[watch_minutes]), 60, 0)",
                "formatString": "#,##0.0",
                "description": "Cumulative video watch hours across all sessions."
            },
            {
                "name": "Total Viewing Sessions",
                "expression": "COUNTROWS(FactViewingSessions)",
                "formatString": "#,##0",
                "description": "Total stream playback sessions."
            },
            {
                "name": "Monthly Active Viewers (MAU)",
                "expression": "DISTINCTCOUNT(FactViewingSessions[user_id])",
                "formatString": "#,##0",
                "description": "Unique viewers who streamed in the period."
            },
            {
                "name": "Platform Completion Rate %",
                "expression": "AVERAGE(FactViewingSessions[completion_percentage])",
                "formatString": "0.0%",
                "description": "Average video duration percentage completed."
            },
            {
                "name": "Average Watch Time Per Viewer",
                "expression": "DIVIDE(SUM(FactViewingSessions[watch_minutes]), [Monthly Active Viewers (MAU)], 0)",
                "formatString": "#,##0.0",
                "description": "Mean watch minutes per active viewer."
            },
            {
                "name": "True Churned Subscribers",
                "expression": "CALCULATE(DISTINCTCOUNT(ChurnByDimension[user_id]), ChurnByDimension[is_true_churn] = 1)",
                "formatString": "#,##0",
                "description": "Canceled subscribers who did not restart within 30 days."
            },
            {
                "name": "Monthly Churn Rate %",
                "expression": "DIVIDE([True Churned Subscribers], [Active Paid Subscribers], 0) * 100",
                "formatString": "0.0%",
                "description": "Proportion of active subscriber base churned."
            },
            {
                "name": "Subscriber Retention Rate %",
                "expression": "IF(NOT(ISBLANK([Monthly Churn Rate %])), 100 - [Monthly Churn Rate %], BLANK())",
                "formatString": "0.0%",
                "description": "Complement of monthly churn rate."
            },
            {
                "name": "Reactivated Subscribers",
                "expression": "CALCULATE(DISTINCTCOUNT(ChurnByDimension[user_id]), ChurnByDimension[is_reactivated] = 1)",
                "formatString": "#,##0",
                "description": "Subscribers who returned after >30 days."
            }
        ]
    }

    # Table 2: MonthlyPerformance
    monthly_cols = [
        ("calendar_month", "string", None),
        ("new_registrations", "int64", "#,##0"),
        ("active_subscribers", "int64", "#,##0"),
        ("estimated_mrr", "double", "$#,##0.00"),
        ("active_viewers_mau", "int64", "#,##0"),
        ("total_sessions", "int64", "#,##0"),
        ("total_watch_hours", "double", "#,##0.0"),
        ("churned_subscribers", "int64", "#,##0"),
        ("lost_mrr", "double", "$#,##0.00")
    ]
    t_monthly = create_table_definition("MonthlyPerformance", "monthly_performance.csv", monthly_cols)

    # Table 3: ContentPerformance
    content_cols = [
        ("content_id", "int64", None),
        ("title", "string", None),
        ("genre", "string", None),
        ("release_year", "int64", "0"),
        ("content_type", "string", None),
        ("duration_minutes", "int64", "#,##0"),
        ("unique_viewers", "int64", "#,##0"),
        ("total_plays", "int64", "#,##0"),
        ("total_watch_hours", "double", "#,##0.0"),
        ("avg_completion_percentage", "double", "0.0%")
    ]
    t_content_perf = create_table_definition("ContentPerformance", "content_performance.csv", content_cols)

    # Table 4: ChurnByDimension
    churn_cols = [
        ("subscription_id", "int64", None),
        ("user_id", "int64", None),
        ("country", "string", None),
        ("acquisition_channel", "string", None),
        ("preferred_device", "string", None),
        ("plan_name", "string", None),
        ("monthly_price", "double", "$#,##0.00"),
        ("start_date", "string", None),
        ("end_date", "string", None),
        ("status", "string", None),
        ("billing_cycle", "string", None),
        ("monthly_fee", "double", "$#,##0.00"),
        ("cancellation_reason", "string", None),
        ("is_true_churn", "int64", "0"),
        ("is_reactivated", "int64", "0")
    ]
    t_churn = create_table_definition("ChurnByDimension", "churn_by_dimension.csv", churn_cols)

    # Table 5: UserSegments
    seg_cols = [
        ("user_id", "int64", None),
        ("signup_date", "string", None),
        ("country", "string", None),
        ("acquisition_channel", "string", None),
        ("preferred_device", "string", None),
        ("total_sessions", "int64", "#,##0"),
        ("total_watch_hours", "double", "#,##0.0"),
        ("avg_completion_pct", "double", "0.0%"),
        ("last_streamed_at", "string", None),
        ("engagement_segment", "string", None)
    ]
    t_segments = create_table_definition("UserSegments", "user_segments.csv", seg_cols)

    # Table 6: DimUsers
    user_cols = [
        ("user_id", "int64", None),
        ("signup_date", "string", None),
        ("country", "string", None),
        ("age_group", "string", None),
        ("acquisition_channel", "string", None),
        ("preferred_device", "string", None)
    ]
    t_users = create_table_definition("DimUsers", "dim_users.csv", user_cols)

    # Table 7: DimPlans
    plan_cols = [
        ("plan_id", "int64", None),
        ("plan_name", "string", None),
        ("monthly_price", "double", "$#,##0.00"),
        ("max_screens", "int64", "0"),
        ("video_quality", "string", None)
    ]
    t_plans = create_table_definition("DimPlans", "dim_plans.csv", plan_cols)

    # Table 8: DimContent
    content_dim_cols = [
        ("content_id", "int64", None),
        ("title", "string", None),
        ("genre", "string", None),
        ("release_year", "int64", "0"),
        ("content_type", "string", None),
        ("duration_minutes", "int64", "#,##0")
    ]
    t_content = create_table_definition("DimContent", "dim_content.csv", content_dim_cols)

    # Table 9: FactSubscriptions
    sub_cols = [
        ("subscription_id", "int64", None),
        ("user_id", "int64", None),
        ("plan_id", "int64", None),
        ("start_date", "string", None),
        ("end_date", "string", None),
        ("status", "string", None),
        ("billing_cycle", "string", None),
        ("monthly_fee", "double", "$#,##0.00"),
        ("cancellation_reason", "string", None)
    ]
    t_subs = create_table_definition("FactSubscriptions", "fact_subscriptions.csv", sub_cols)

    # Table 10: FactViewingSessions
    sess_cols = [
        ("session_id", "int64", None),
        ("user_id", "int64", None),
        ("content_id", "int64", None),
        ("started_at", "string", None),
        ("watch_minutes", "int64", "#,##0"),
        ("completion_percentage", "double", "0.0%"),
        ("device_type", "string", None)
    ]
    t_sess = create_table_definition("FactViewingSessions", "fact_viewing_sessions.csv", sess_cols)

    # Define Relationships
    relationships = [
        {
            "name": "rel_subs_users",
            "fromTable": "FactSubscriptions",
            "fromColumn": "user_id",
            "toTable": "DimUsers",
            "toColumn": "user_id"
        },
        {
            "name": "rel_subs_plans",
            "fromTable": "FactSubscriptions",
            "fromColumn": "plan_id",
            "toTable": "DimPlans",
            "toColumn": "plan_id"
        },
        {
            "name": "rel_sess_users",
            "fromTable": "FactViewingSessions",
            "fromColumn": "user_id",
            "toTable": "DimUsers",
            "toColumn": "user_id"
        },
        {
            "name": "rel_sess_content",
            "fromTable": "FactViewingSessions",
            "fromColumn": "content_id",
            "toTable": "DimContent",
            "toColumn": "content_id"
        },
        {
            "name": "rel_churn_users",
            "fromTable": "ChurnByDimension",
            "fromColumn": "user_id",
            "toTable": "DimUsers",
            "toColumn": "user_id"
        },
        {
            "name": "rel_segments_users",
            "fromTable": "UserSegments",
            "fromColumn": "user_id",
            "toTable": "DimUsers",
            "toColumn": "user_id"
        }
    ]

    model_bim = {
        "name": "StreamScope_Analytics",
        "compatibilityLevel": 1567,
        "model": {
            "culture": "en-US",
            "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "tables": [
                measures_table,
                t_monthly,
                t_content_perf,
                t_churn,
                t_segments,
                t_users,
                t_plans,
                t_content,
                t_subs,
                t_sess
            ],
            "relationships": relationships
        }
    }

    with open(MODEL_BIM_PATH, "w", encoding="utf-8") as f:
        json.dump(model_bim, f, indent=2)

    size_kb = os.path.getsize(MODEL_BIM_PATH) / 1024
    print(f"✓ Created {MODEL_BIM_PATH} successfully! Size: {size_kb:.1f} KB")

if __name__ == "__main__":
    generate_model()
