# StreamScope Complete Data Dictionary

This document serves as the formal data dictionary for all tables and attributes in the StreamScope analytics database.

---

## 1. Table: `users`
**Description**: Stores master profile and demographic metadata for every registered user on the platform.

| Column Name | Data Type | Nullable | Key | Sample Values | Description / Business Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `user_id` | `INT` | No | PK | `101`, `542` | Unique surrogate key identifying each registered user. |
| `signup_date` | `DATE` | No | - | `2025-01-14` | The calendar date on which the user completed account registration. |
| `country` | `VARCHAR(50)` | No | - | `United States`, `United Kingdom` | Geographical nation where the user resides. |
| `age_group` | `VARCHAR(20)` | No | - | `18-24`, `25-34`, `35-44` | Age bracket self-reported or inferred during onboarding. |
| `acquisition_channel`| `VARCHAR(50)` | No | - | `Organic Search`, `Social Media` | Marketing acquisition source attributing the initial signup. |
| `preferred_device` | `VARCHAR(30)` | No | - | `Smart TV`, `Mobile`, `Laptop` | User's primary declared hardware for streaming video. |
| `created_at` | `TIMESTAMP` | No | - | `2025-01-14 10:22:00` | Database system insert timestamp. |

---

## 2. Table: `plans`
**Description**: Dimension table enumerating the commercially available subscription tiers and their entitlements.

| Column Name | Data Type | Nullable | Key | Sample Values | Description / Business Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `plan_id` | `INT` | No | PK | `1`, `2`, `3`, `4` | Unique surrogate key for each subscription tier. |
| `plan_name` | `VARCHAR(50)` | No | - | `Standard HD`, `Premium 4K` | Marketing name of the tier. |
| `monthly_price` | `DECIMAL(6,2)` | No | - | `6.99`, `11.99`, `16.99`, `21.99` | Standard monthly list price in USD. |
| `max_screens` | `INT` | No | - | `1`, `2`, `4` | Maximum allowable concurrent streaming devices. |
| `video_quality` | `VARCHAR(30)` | No | - | `Full HD 1080p`, `4K Ultra HD` | Maximum supported video and audio stream fidelity. |

---

## 3. Table: `subscriptions`
**Description**: Fact/lifecycle table recording all historical and active subscription agreements.

| Column Name | Data Type | Nullable | Key | Sample Values | Description / Business Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `subscription_id` | `INT` | No | PK | `1001`, `4205` | Unique surrogate identifier for each subscription lifecycle period. |
| `user_id` | `INT` | No | FK | `101`, `542` | References `users.user_id`. |
| `plan_id` | `INT` | No | FK | `2`, `3` | References `plans.plan_id`. |
| `start_date` | `DATE` | No | - | `2025-01-15` | Effective start date of the subscription agreement. |
| `end_date` | `DATE` | Yes | - | `2025-07-20`, `NULL` | Expiration or cancellation date. `NULL` denotes an ongoing active plan. |
| `status` | `ENUM` | No | - | `Active`, `Canceled` | Current administrative status of the subscription. |
| `billing_cycle` | `ENUM` | No | - | `Monthly`, `Annual` | Frequency of recurring payments. |
| `monthly_fee` | `DECIMAL(6,2)` | No | - | `11.99`, `9.83` | Actual recurring monthly fee charged (reflecting annual plan discounts). |
| `cancellation_reason`| `VARCHAR(100)`| Yes | - | `Price too high`, `NULL` | Customer-reported reason upon subscription cancellation. |

---

## 4. Table: `content`
**Description**: Dimension catalog of all movies and web series available in StreamScope's content library.

| Column Name | Data Type | Nullable | Key | Sample Values | Description / Business Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `content_id` | `INT` | No | PK | `1`, `42` | Unique surrogate key identifying each title. |
| `title` | `VARCHAR(100)`| No | - | `Cyber City 2099` | Public title of the movie or series. |
| `genre` | `VARCHAR(50)` | No | - | `Sci-Fi & Fantasy`, `Drama` | Primary content classification category. |
| `release_year` | `INT` | No | - | `2024`, `2025` | Initial public release year of the content. |
| `content_type` | `ENUM` | No | - | `Movie`, `Web Series` | Format classification. |
| `duration_minutes` | `INT` | No | - | `118`, `55` | Full runtime for a movie or typical episode duration for a series. |

---

## 5. Table: `viewing_sessions`
**Description**: High-granularity fact table recording individual playback sessions initiated by users.

| Column Name | Data Type | Nullable | Key | Sample Values | Description / Business Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `session_id` | `INT` | No | PK | `5001`, `98124` | Unique surrogate key for each viewing playback instance. |
| `user_id` | `INT` | No | FK | `101`, `542` | References `users.user_id`. |
| `content_id` | `INT` | No | FK | `1`, `42` | References `content.content_id`. |
| `started_at` | `DATETIME` | No | - | `2025-03-12 20:45:12`| Timestamp when the video player initiated playback. |
| `watch_minutes` | `INT` | No | - | `45`, `110` | Total continuous playback duration in minutes. |
| `completion_percentage`| `DECIMAL(5,2)`| No| - | `78.50`, `95.20` | Computed percentage of total title duration watched. |
| `device_type` | `VARCHAR(30)` | No | - | `Smart TV`, `Mobile` | Hardware client on which the session was streamed. |

---

## 6. Table: `app_events`
**Description**: Telemetry clickstream fact table tracking navigation and user interface interactions.

| Column Name | Data Type | Nullable | Key | Sample Values | Description / Business Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `event_id` | `INT` | No | PK | `1`, `245100` | Unique event identifier. |
| `user_id` | `INT` | No | FK | `101`, `542` | References `users.user_id`. |
| `event_timestamp` | `DATETIME` | No | - | `2025-02-10 18:32:01`| Exact system timestamp when the event was emitted. |
| `event_type` | `VARCHAR(50)` | No | - | `app_open`, `play`, `search`| Action performed by the client application. |
| `content_id` | `INT` | Yes | FK | `1`, `NULL` | Content context associated with the action (or `NULL` if general). |
| `device_type` | `VARCHAR(30)` | No | - | `Smart TV`, `Mobile` | Client platform triggering the event. |
