# SitWise — Veritabanı ER Diyagramı (SW-014)

```mermaid
erDiagram
    users ||--o{ sessions : "has"
    users ||--o{ calibration_profiles : "has"
    users ||--o{ fatigue_reports : "submits"
    users ||--o{ daily_summaries : "has"
    users ||--o{ user_thresholds : "configures"

    sessions ||--o{ metric_samples : "contains"
    sessions ||--o{ alerts : "triggers"

    alerts ||--o| alert_feedback : "receives"

    users {
        uuid id PK
        string email
        string password_hash
        string name
        timestamp created_at
    }

    calibration_profiles {
        uuid id PK
        uuid user_id FK
        float neck_mean
        float neck_std
        float shoulder_mean
        float shoulder_std
        float distance_cm
        timestamp created_at
    }

    sessions {
        uuid id PK
        uuid user_id FK
        timestamp started_at
        timestamp ended_at
        string device
    }

    metric_samples {
        bigint id PK
        uuid session_id FK
        timestamp ts
        float neck_ratio
        float shoulder_tilt
        float distance_cm
        int blinks_per_min
        string state
    }

    alerts {
        uuid id PK
        uuid session_id FK
        timestamp ts
        string type
        string severity
    }

    alert_feedback {
        uuid id PK
        uuid alert_id FK
        boolean is_false
        timestamp created_at
    }

    user_thresholds {
        uuid id PK
        uuid user_id FK
        string metric
        float value
        timestamp updated_at
    }

    fatigue_reports {
        uuid id PK
        uuid user_id FK
        date date
        int score
    }

    daily_summaries {
        uuid id PK
        uuid user_id FK
        date date
        int score
        int good_minutes
        int alert_count
        float avg_blink
    }