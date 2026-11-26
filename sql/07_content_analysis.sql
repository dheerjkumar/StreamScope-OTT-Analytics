-- =====================================================================
-- StreamScope OTT Analytics
-- Module C: Content Performance Analysis
-- File: sql/07_content_analysis.sql
-- Author: StreamScope Data & Product Analytics Team
-- RDBMS: MySQL 8.0+
-- =====================================================================

USE streamscope;

-- ---------------------------------------------------------------------
-- QUERY C1: Top 10 Titles Ranked Holistically (Viewers, Watch Hours, Completion)
-- ---------------------------------------------------------------------
-- Business Question: What are the genuine blockbuster titles on StreamScope?
-- Why Needed: Do not rank purely by total hours (which favors long titles). Balance with audience reach and completion.
-- Tables: content, viewing_sessions
-- Joins: INNER JOIN on content_id
-- Functions: COUNT(DISTINCT), SUM, AVG, DENSE_RANK()
-- ---------------------------------------------------------------------
WITH content_stats AS (
    SELECT
        c.content_id,
        c.title,
        c.genre,
        c.content_type,
        c.duration_minutes,
        COUNT(DISTINCT vs.user_id) AS unique_viewers,
        COUNT(vs.session_id) AS total_plays,
        ROUND(SUM(vs.watch_minutes) / 60.0, 1) AS total_watch_hours,
        ROUND(AVG(vs.completion_percentage), 2) AS avg_completion_pct
    FROM content c
    JOIN viewing_sessions vs ON c.content_id = vs.content_id
    GROUP BY c.content_id, c.title, c.genre, c.content_type, c.duration_minutes
)
SELECT
    title,
    genre,
    content_type,
    unique_viewers,
    total_plays,
    total_watch_hours,
    avg_completion_pct,
    DENSE_RANK() OVER (ORDER BY total_watch_hours DESC) AS rank_by_hours,
    DENSE_RANK() OVER (ORDER BY unique_viewers DESC) AS rank_by_viewers
FROM content_stats
ORDER BY total_watch_hours DESC
LIMIT 10;

-- ---------------------------------------------------------------------
-- QUERY C2: Genre Consumption vs Catalog Share (ROI Analysis)
-- ---------------------------------------------------------------------
-- Business Question: Which genres generate disproportionate viewership relative to their library catalog size?
-- Why Needed: Identifies over-indexed and under-indexed content categories for licensing decisions.
-- Tables: content, viewing_sessions
-- ---------------------------------------------------------------------
WITH catalog_genre AS (
    SELECT
        genre,
        COUNT(content_id) AS title_count,
        ROUND(COUNT(content_id) * 100.0 / (SELECT COUNT(*) FROM content), 2) AS catalog_share_pct
    FROM content
    GROUP BY genre
),
viewing_genre AS (
    SELECT
        c.genre,
        COUNT(DISTINCT vs.user_id) AS unique_viewers,
        ROUND(SUM(vs.watch_minutes) / 60.0, 1) AS genre_watch_hours,
        ROUND(AVG(vs.completion_percentage), 2) AS avg_completion_pct
    FROM content c
    JOIN viewing_sessions vs ON c.content_id = vs.content_id
    GROUP BY c.genre
)
SELECT
    cg.genre,
    cg.title_count,
    cg.catalog_share_pct,
    vg.unique_viewers,
    vg.genre_watch_hours,
    ROUND(vg.genre_watch_hours * 100.0 / (SELECT SUM(watch_minutes)/60.0 FROM viewing_sessions), 2) AS viewership_share_pct,
    vg.avg_completion_pct,
    ROUND(
        (ROUND(vg.genre_watch_hours * 100.0 / (SELECT SUM(watch_minutes)/60.0 FROM viewing_sessions), 2) - cg.catalog_share_pct), 
        2
    ) AS demand_supply_gap
FROM catalog_genre cg
JOIN viewing_genre vg ON cg.genre = vg.genre
ORDER BY vg.genre_watch_hours DESC;

-- ---------------------------------------------------------------------
-- QUERY C3: Content Type Performance (Movies vs Web Series)
-- ---------------------------------------------------------------------
-- Business Question: How does viewer engagement differ between serialized episodes and feature films?
-- Tables: content, viewing_sessions
-- ---------------------------------------------------------------------
SELECT
    c.content_type,
    COUNT(DISTINCT c.content_id) AS total_titles,
    COUNT(vs.session_id) AS total_sessions,
    COUNT(DISTINCT vs.user_id) AS unique_viewers,
    ROUND(SUM(vs.watch_minutes) / 60.0, 1) AS total_watch_hours,
    ROUND(AVG(vs.watch_minutes), 1) AS avg_session_watch_minutes,
    ROUND(AVG(vs.completion_percentage), 2) AS avg_completion_pct
FROM content c
JOIN viewing_sessions vs ON c.content_id = vs.content_id
GROUP BY c.content_type;

-- ---------------------------------------------------------------------
-- QUERY C4: Highest Completion Rate Content (High Satisfaction / Low Abandonment)
-- ---------------------------------------------------------------------
-- Business Question: Which content has minimum abandonment (< 15% drop-off) among titles with substantial reach?
-- Threshold: At least 500 unique viewers to avoid small-sample bias.
-- Tables: content, viewing_sessions
-- ---------------------------------------------------------------------
SELECT
    c.title,
    c.genre,
    c.content_type,
    COUNT(DISTINCT vs.user_id) AS unique_viewers,
    ROUND(AVG(vs.completion_percentage), 2) AS avg_completion_pct,
    ROUND(SUM(vs.watch_minutes) / 60.0, 1) AS total_watch_hours
FROM content c
JOIN viewing_sessions vs ON c.content_id = vs.content_id
GROUP BY c.content_id, c.title, c.genre, c.content_type
HAVING COUNT(DISTINCT vs.user_id) >= 500
ORDER BY avg_completion_pct DESC
LIMIT 10;

-- ---------------------------------------------------------------------
-- QUERY C5: Repeat Viewing Behavior & Rewatch Rate
-- ---------------------------------------------------------------------
-- Business Question: What percentage of viewers rewatch content, and which titles drive the highest rewatch frequency?
-- Tables: viewing_sessions, content
-- ---------------------------------------------------------------------
WITH user_content_views AS (
    SELECT
        content_id,
        user_id,
        COUNT(session_id) AS stream_count
    FROM viewing_sessions
    GROUP BY content_id, user_id
)
SELECT
    c.title,
    c.genre,
    COUNT(ucv.user_id) AS total_distinct_viewers,
    SUM(CASE WHEN ucv.stream_count > 1 THEN 1 ELSE 0 END) AS repeat_viewers,
    ROUND(SUM(CASE WHEN ucv.stream_count > 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(ucv.user_id), 2) AS rewatch_rate_pct,
    ROUND(AVG(ucv.stream_count), 2) AS avg_streams_per_viewer
FROM user_content_views ucv
JOIN content c ON ucv.content_id = c.content_id
GROUP BY c.content_id, c.title, c.genre
HAVING COUNT(ucv.user_id) >= 500
ORDER BY rewatch_rate_pct DESC
LIMIT 10;
