"""Tabellene i databasen (AD-5).

Skjemaet lages med ``create_all`` og har ingen migrering. Endres skjemaet, slettes fila.
Alle mengder og uker er heltall.
"""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ItemRow(Base):
    __tablename__ = "items"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str]
    source: Mapped[str]
    unit: Mapped[str]
    lead_time_weeks: Mapped[int]
    on_hand: Mapped[int]
    safety_stock: Mapped[int]
    lot_rule: Mapped[str]
    lot_quantity: Mapped[int | None]


class BomLineRow(Base):
    __tablename__ = "bom_lines"

    parent: Mapped[str] = mapped_column(ForeignKey("items.id"), primary_key=True)
    child: Mapped[str] = mapped_column(ForeignKey("items.id"), primary_key=True)
    qty_per: Mapped[int]


class MpsLineRow(Base):
    __tablename__ = "mps_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item: Mapped[str] = mapped_column(ForeignKey("items.id"))
    week: Mapped[int]
    quantity: Mapped[int]
    hull_no: Mapped[int] = mapped_column(unique=True)  # FR-8: byggenummeret er unikt.


class ScheduledReceiptRow(Base):
    __tablename__ = "scheduled_receipts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item: Mapped[str] = mapped_column(ForeignKey("items.id"))
    week: Mapped[int]
    quantity: Mapped[int]
    note: Mapped[str] = mapped_column(default="")


class PlanningSettingsRow(Base):
    """Én rad med planhorisonten."""

    __tablename__ = "planning_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_week: Mapped[int]
    horizon_weeks: Mapped[int]


class UserRow(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
