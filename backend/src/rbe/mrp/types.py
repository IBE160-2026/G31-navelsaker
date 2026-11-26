"""Inndatatypene til MRP-kjernen (AD-2).

Frosne dataklasser med fasitens feltnavn. Samlinger er ``tuple`` i fasitens rekkefølge.
Resultattypene kommer i story 2.1.
"""

from dataclasses import dataclass
from typing import Literal

LotRule = Literal["L4L", "FOQ"]
Source = Literal["make", "purchase"]


@dataclass(frozen=True, slots=True)
class LotSizing:
    rule: LotRule
    quantity: int | None = None


@dataclass(frozen=True, slots=True)
class Item:
    id: str
    name: str
    source: Source
    unit: str
    lead_time_weeks: int
    on_hand: int
    safety_stock: int
    lot_sizing: LotSizing


@dataclass(frozen=True, slots=True)
class BomLine:
    parent: str
    child: str
    qty_per: int


@dataclass(frozen=True, slots=True)
class MpsLine:
    item: str
    week: int
    quantity: int
    hull_no: int


@dataclass(frozen=True, slots=True)
class ScheduledReceipt:
    item: str
    week: int
    quantity: int
    note: str = ""


@dataclass(frozen=True, slots=True)
class Horizon:
    first_week: int
    weeks: int


@dataclass(frozen=True, slots=True)
class MrpInput:
    horizon: Horizon
    items: tuple[Item, ...]
    bom: tuple[BomLine, ...]
    mps: tuple[MpsLine, ...]
    scheduled_receipts: tuple[ScheduledReceipt, ...]
