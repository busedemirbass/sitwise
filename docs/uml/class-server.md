# SitWise — Sunucu Sınıf Diyagramı (SW-014)

```mermaid
classDiagram
    class BaseRepository~T~ {
        +get(id) T
        +add(entity) T
        +list() List~T~
    }

    class UserRepository {
        +get_by_email(email) User
    }

    class MetricRepository {
        +add_batch(metrics)
        +by_date_range(user_id, start, end)
    }

    class AlertRepository {
        +get_user_alerts(user_id)
    }

    BaseRepository <|-- UserRepository
    BaseRepository <|-- MetricRepository
    BaseRepository <|-- AlertRepository

    class AuthService {
        -UserRepository user_repo
        +register(data) Token
        +login(creds) Token
        +verify_token(token) User
    }

    class MetricsService {
        -MetricRepository metric_repo
        +ingest(batch)
    }

    class SummaryService {
        -MetricRepository metric_repo
        -AlertRepository alert_repo
        +daily(user_id, date) DailySummary
        +range(user_id, start, end)
    }

    AuthService --> UserRepository
    MetricsService --> MetricRepository
    SummaryService --> MetricRepository
    SummaryService --> AlertRepository