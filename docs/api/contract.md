# SitWise API Sozlesmesi - Bolum 4.6

> **Kart:** SW-015
> **Durum:** Taslak (stub - is mantigi ilerleyen kartlarda eklenir)
> **Surum:** v1.0.0
> **Taban URL:** `http://localhost:8000/api/v1`
> **OpenAPI Arayuzu:** `http://localhost:8000/docs`
> **Gizlilik notu:** Kamera karesi asla iletilmez; yalnizca sayisal ergonomi ozetleri gonderilir.

---

## 4.6.1 Kimlik Dogrulama (Auth)

| # | Yontem | Yol | Istek Govdesi | Basari Yaniti | Aciklama |
|---|--------|-----|---------------|---------------|----------|
| 1 | `POST` | `/auth/register` | `{ name, email, password }` | `201 { access_token, token_type }` | Yeni kullanici kaydi; JWT doner |
| 2 | `POST` | `/auth/login` | `{ email, password }` | `200 { access_token, token_type }` | Kimlik dogrulama; JWT doner |
| 3 | `POST` | `/auth/logout` | - | `204 No Content` | Gecerli jetonu gecersiz kilar |
| 4 | `GET` | `/auth/me` | - | `200 { id, name, email }` | Oturum acmis kullanici profili |

**Kimlik dogrulama semasi:** Bearer Token (`Authorization: Bearer <jwt>`)

---

## 4.6.2 Oturumlar (Sessions)

| # | Yontem | Yol | Istek Govdesi | Basari Yaniti | Aciklama |
|---|--------|-----|---------------|---------------|----------|
| 5 | `POST` | `/sessions/` | `{ device? }` | `201 SessionResponse` | Yeni calisma oturumu baslatir |
| 6 | `PATCH` | `/sessions/{session_id}/end` | - | `200 SessionResponse` | Oturumu ended_at ile kapatir |
| 7 | `GET` | `/sessions/` | - | `200 { sessions[], total }` | Kullanicinin tum oturumlarini listeler |
| 8 | `GET` | `/sessions/{session_id}` | - | `200 SessionResponse` | Tek oturum detayi |

**SessionResponse alanlari:** `id`, `user_id`, `started_at`, `ended_at?`, `device`

---

## 4.6.3 Metrik Ornekleri (Metrics)

| # | Yontem | Yol | Istek Govdesi | Basari Yaniti | Aciklama |
|---|--------|-----|---------------|---------------|----------|
| 9 | `POST` | `/metrics/ingest` | `{ session_id, samples[] }` | `202 { accepted, session_id }` | Toplu sayisal metrik gonderir |
| 10 | `GET` | `/metrics/` | `?session_id&start&end&limit&offset` | `200 { samples[], total }` | Filtreli metrik listesi |

**MetricSample alanlari:** `ts`, `neck_ratio [0-2]`, `shoulder_tilt [-90 - +90 derece]`, `distance_cm [10-200]`, `blinks_per_min [0-60]`, `state: good / warning / bad`

**Toplu yuk siniri:** en az 1, en fazla 500 ornek per istek

---

## 4.6.4 Uyarilar (Alerts)

| # | Yontem | Yol | Istek Govdesi | Basari Yaniti | Aciklama |
|---|--------|-----|---------------|---------------|----------|
| 11 | `GET` | `/alerts/` | `?session_id&limit&offset` | `200 { alerts[], total }` | Kullanici uyarilarini listeler |
| 12 | `GET` | `/alerts/{alert_id}` | - | `200 AlertResponse` | Tek uyari detayi |
| 13 | `POST` | `/alerts/{alert_id}/feedback` | `{ is_false: bool }` | `201 AlertFeedbackResponse` | Yanlis pozitif bildirimi |

**AlertResponse alanlari:** `id`, `session_id`, `ts`, `type: posture / eye_fatigue / distance`, `severity: low / medium / high`

---

## 4.6.5 Gunluk Ozetler (Summaries)

| # | Yontem | Yol | Istek Govdesi | Basari Yaniti | Aciklama |
|---|--------|-----|---------------|---------------|----------|
| 14 | `GET` | `/summaries/daily` | `?date=YYYY-MM-DD` | `200 DailySummaryResponse` | Tek gunluk ergonomi ozeti |
| 15 | `GET` | `/summaries/range` | `?start=YYYY-MM-DD&end=YYYY-MM-DD` | `200 { summaries[], total }` | Tarih araligi ozetleri |

**DailySummaryResponse alanlari:** `id`, `user_id`, `date`, `score [0-100]`, `good_minutes`, `alert_count`, `avg_blink`

---

## 4.6.6 Kalibrasyon (Calibration)

| # | Yontem | Yol | Istek Govdesi | Basari Yaniti | Aciklama |
|---|--------|-----|---------------|---------------|----------|
| 16 | `POST` | `/calibration/` | `{ neck_mean, neck_std, shoulder_mean, shoulder_std, distance_cm }` | `201 CalibrationResponse` | Yeni kalibrasyon profili olusturur |
| 17 | `GET` | `/calibration/latest` | - | `200 CalibrationResponse` | En son kalibrasyon profilini doner |
| 18 | `GET` | `/calibration/{profile_id}` | - | `200 CalibrationResponse` | Belirli kalibrasyon profili |

---

## 4.6.7 Esik Degerleri (Thresholds)

| # | Yontem | Yol | Istek Govdesi | Basari Yaniti | Aciklama |
|---|--------|-----|---------------|---------------|----------|
| 19 | `GET` | `/thresholds/` | - | `200 { thresholds[] }` | Kullanicinin tum esiklerini listeler |
| 20 | `PUT` | `/thresholds/` | `{ metric, value }` | `200 ThresholdResponse` | Esik olusturur veya gunceller (upsert) |
| 21 | `DELETE` | `/thresholds/{metric}` | - | `204 No Content` | Esigi siler; sistem varsayilanina doner |

**Gecerli metrik adlari:** `neck_ratio`, `shoulder_tilt`, `distance_cm`, `blinks_per_min`

---

## 4.6.8 Saglik Kontrolu

| # | Yontem | Yol | Basari Yaniti | Aciklama |
|---|--------|-----|---------------|----------|
| 22 | `GET` | `/health` | `200 { status, service, version }` | Sunucu canlilik kontrolu |

---

## 4.6.9 Ortak HTTP Durum Kodlari

| Kod | Anlam | Ne Zaman |
|-----|-------|----------|
| `200` | OK | Basarili okuma |
| `201` | Created | Kaynak olusturuldu |
| `202` | Accepted | Toplu metrik kabul edildi |
| `204` | No Content | Silme / cikis basarili |
| `400` | Bad Request | Dogrulama hatasi |
| `401` | Unauthorized | Gecersiz / eksik JWT |
| `403` | Forbidden | Yetkisiz kaynak erisimi |
| `404` | Not Found | Kayit bulunamadi |
| `501` | Not Implemented | Stub - henuz uygulanmadi |

---

## 4.6.10 Notlar

- Tum zaman damgalari **UTC ISO 8601** formatindadir (ornek: `2026-10-07T08:00:00Z`).
- `session_id` ve kullanici ID'leri **UUID v4** formatindadir.
- Hata yanitlari `{ detail: string }` bicimindedir (FastAPI varsayilani).
- Canli OpenAPI semasi her zaman `GET /openapi.json` adresinden alinabilir.
