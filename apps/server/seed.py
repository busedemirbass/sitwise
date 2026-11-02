"""
SW-031: Sahte Veri Üreteci CLI Komutu.
Kabul Kriteri: Tek komutla DB doluyor.

Kullanım:
    python seed.py
    python seed.py --days 14 --reset
"""

from __future__ import annotations

import argparse
import sys

from db.base import Base
from db.seed import seed_database
from db.session import SessionLocal, engine
import models  # noqa: F401

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main() -> int:
    parser = argparse.ArgumentParser(
        description=("SitWise veritabanini sahte (mock) ergonomi verileriyle doldurur.")
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Kac gunluk gecmis veri uretilecegi (varsayilan: 7)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Onceki demo verilerini temizleyip bastan doldurur",
    )
    args = parser.parse_args()

    # Tablolar mevcut degilse otomatik olarak olustur
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("[SitWise] Veritabani sahte verilerle dolduruluyor...")
        stats = seed_database(db, days=args.days, reset=args.reset)
        print("[OK] Islem basariyla tamamlandi!")
        print("--------------------------------------------------")
        print(f"  - Kullanicilar         : {stats['users']}")
        print(f"  - Kalibrasyon Profili  : {stats['calibration_profiles']}")
        print(f"  - Esik Degerleri       : {stats['thresholds']}")
        print(f"  - Calisma Oturumlari   : {stats['sessions']}")
        print(f"  - Metrik Ornekleri     : {stats['metric_samples']}")
        print(f"  - Uyarilar (Alerts)    : {stats['alerts']}")
        print(f"  - Uyari Geri Bildirim  : {stats['alert_feedbacks']}")
        print(f"  - Gunluk Ozetler       : {stats['daily_summaries']}")
        print(f"  - Yorgunluk Raporlari  : {stats['fatigue_reports']}")
        print("--------------------------------------------------")
        print("Giris Bilgileri (Demo):")
        print("  E-posta : demo@sitwise.app")
        print("  Sifre   : Password123!")
        return 0
    except Exception as exc:
        print(f"Hata olustu: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
