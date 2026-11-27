"""Inn- og utdatatypene til MRP-kjernen (AD-2).

Frosne dataklasser med fasitens feltnavn. Samlinger er ``tuple``. Inndataene står i fasitens
rekkefølge, og resultatet i rekkefølgen fra AD-3 (se ``run_mrp``).
"""

from dataclasses import dataclass
from typing import ClassVar, Literal

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
    """Planhorisonten. ``first_week`` er alltid 1 (ellers ``MrpInputError``), og uke *t* har
    indeks *t* − 1 i ukesarrayene. En frigivelse før uke 1 er forfalt (R1, R9)."""

    first_week: int
    weeks: int


@dataclass(frozen=True, slots=True)
class MrpInput:
    horizon: Horizon
    items: tuple[Item, ...]
    bom: tuple[BomLine, ...]
    mps: tuple[MpsLine, ...]
    scheduled_receipts: tuple[ScheduledReceipt, ...]


@dataclass(frozen=True, slots=True)
class PlannedOrder:
    """Et planlagt ordreforslag. ``release_week`` kan være < 1 (forfalt, R9)."""

    receipt_week: int
    release_week: int
    quantity: int


@dataclass(frozen=True, slots=True)
class LeadTimeExceedsHorizon:
    """E1 (FR-13): varen har bruttobehov i horisonten og ledetid lengre enn horisonten."""

    type: ClassVar[Literal["LEAD_TIME_EXCEEDS_HORIZON"]] = "LEAD_TIME_EXCEEDS_HORIZON"
    item: str
    lead_time_weeks: int
    horizon_weeks: int


@dataclass(frozen=True, slots=True)
class PastDueRelease:
    """E2 (FR-14): et forslag med frigivelsesuke før første planuke."""

    type: ClassVar[Literal["PAST_DUE_RELEASE"]] = "PAST_DUE_RELEASE"
    item: str
    quantity: int
    receipt_week: int
    release_week: int
    weeks_past_due: int
    earliest_receipt_week: int


MrpException = LeadTimeExceedsHorizon | PastDueRelease


@dataclass(frozen=True, slots=True)
class ItemResult:
    """Resultatet for én vare. Ukesarrayene har lengde = horisont, og indeks 0 er uke 1."""

    id: str
    name: str
    unit: str
    on_hand: int
    low_level_code: int
    gross_requirements: tuple[int, ...]
    scheduled_receipts: tuple[int, ...]
    projected_on_hand: tuple[int, ...]
    net_requirements: tuple[int, ...]
    planned_order_receipts: tuple[int, ...]
    planned_order_releases: tuple[int, ...]
    planned_orders: tuple[PlannedOrder, ...]


@dataclass(frozen=True, slots=True)
class MrpResult:
    """Hele MRP-kjøringen: varene på (``low_level_code``, ``id``) og meldingene (AD-3)."""

    items: tuple[ItemResult, ...]
    exceptions: tuple[MrpException, ...]
