"""
SQLAlchemy DeclarativeBase — tüm modeller bu base'den türer.
SW-020: SQLAlchemy modelleri ve Alembic migration'ları
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Tüm ORM modellerinin ortak üst sınıfı."""

    pass
