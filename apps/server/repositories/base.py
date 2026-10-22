"""
Temel repository sınıfı — CRUD işlemlerinin genel arayüzü.
SW-014 ve SW-021: docs/uml/class-server.md referans alınmıştır.
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Genel veri tabanı repository sınıfı."""

    def __init__(self, db: Session, model: type[T]) -> None:
        self.db = db
        self.model = model

    def get(self, entity_id: Any) -> T | None:
        """Birincil anahtara göre tek bir kayıt döner."""
        return self.db.query(self.model).filter(self.model.id == entity_id).first()

    def add(self, entity: T) -> T:
        """Yeni kaydı veritabanına ekler ve güncel halini döner."""
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def list(self) -> list[T]:
        """Modelin tüm kayıtlarını listeler."""
        return self.db.query(self.model).all()
