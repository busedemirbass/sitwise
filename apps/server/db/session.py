"""
Veritabanı engine ve oturum fabrikası.
SW-020: SQLAlchemy modelleri ve Alembic migration'ları

DATABASE_URL ortam değişkeninden bağlantı dizesini okur.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Ortam değişkeninden bağlantı URL'si alınır; yoksa yerel geliştirme varsayılanı
DATABASE_URL: str = os.environ.get(
    "DATABASE_URL",
    "postgresql://sitwise:sitwisepass@localhost:5432/sitwise_db",
)

engine = create_engine(
    DATABASE_URL,
    # Bağlantı havuzu boyutu ve taşma sınırı
    pool_size=5,
    max_overflow=10,
    # Ölü bağlantıları 30 dakikada bir sıfırla
    pool_recycle=1800,
    echo=False,  # SQL sorgularını loglara yansıtma (geliştirmede True yapılabilir)
)

# Her istek için ayrı bir session açılır; commit/rollback çağıran tarafın sorumluluğunda
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency injection için veritabanı oturumu üreteci."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
