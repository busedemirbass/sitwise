"""
SW-073: Hazır Veri Hattı Çalıştırıcı (Master Pipeline Runner).
Kabul Kriteri: Eyeblink8 ve seçilen duruş seti CSV'ye çevrildi.

Kullanım:
    python scripts/pipeline/run_pipeline.py
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

# Proje kök dizinini sys.path'e ekle
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from scripts.pipeline.eyeblink8_pipeline import (  # noqa: E402
    generate_eyeblink8_benchmark_csv,
)
from scripts.pipeline.posture_pipeline import (  # noqa: E402
    generate_posture_benchmark_csv,
)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Eyeblink8 ve MultiPosture duruş setlerini MediaPipe özniteliklerine "
            "dönüştürür ve standart CSV olarak kaydeder."
        )
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/processed",
        help="Dönüştürülen CSV dosyalarının kaydedileceği dizin",
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    eyeblink_csv = out_dir / "eyeblink8_features.csv"
    posture_csv = out_dir / "posture_features.csv"

    print("==================================================")
    print("SitWise Track C: Hazır Veri Hattı (SW-073)")
    print("==================================================")

    # 1. Eyeblink8 Veri Seti Dönüşümü
    print("\n[1/2] Eyeblink8 veri seti MediaPipe EAR hattından geçiriliyor...")
    eb_rows = generate_eyeblink8_benchmark_csv(eyeblink_csv)
    print(f"  -> Tamamlandı: {eb_rows} satır oluşturuldu.")
    print(f"  -> Çıktı: {eyeblink_csv}")

    # 2. MultiPosture Duruş Veri Seti Dönüşümü
    print("\n[2/2] MultiPosture duruş seti MediaPipe Pose hattından geçiriliyor...")
    mp_rows = generate_posture_benchmark_csv(posture_csv)
    print(f"  -> Tamamlandı: {mp_rows} satır oluşturuldu.")
    print(f"  -> Çıktı: {posture_csv}")

    print("\n[OK] Kabul kriteri başarıyla sağlandı:")
    print("  ✓ Eyeblink8 CSV formatına çevrildi.")
    print("  ✓ Seçilen duruş seti (MultiPosture) CSV formatına çevrildi.")
    print("==================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
