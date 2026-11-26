"""Lesing av inndataene fra databasen som kjernens typer (AD-5)."""

from typing import cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from rbe.db.models import (
    BomLineRow,
    ItemRow,
    MpsLineRow,
    PlanningSettingsRow,
    ScheduledReceiptRow,
)
from rbe.mrp.types import (
    BomLine,
    Horizon,
    Item,
    LotRule,
    LotSizing,
    MpsLine,
    MrpInput,
    ScheduledReceipt,
    Source,
)


def read_input(session: Session) -> MrpInput:
    """Gi inndataene i databasen som ``MrpInput``, sortert deterministisk."""
    settings = session.get_one(PlanningSettingsRow, 1)
    items = session.scalars(select(ItemRow).order_by(ItemRow.id))
    bom = session.scalars(select(BomLineRow).order_by(BomLineRow.parent, BomLineRow.child))
    mps = session.scalars(select(MpsLineRow).order_by(MpsLineRow.id))
    receipts = session.scalars(select(ScheduledReceiptRow).order_by(ScheduledReceiptRow.id))
    return MrpInput(
        horizon=Horizon(first_week=settings.first_week, weeks=settings.horizon_weeks),
        items=tuple(
            Item(
                id=row.id,
                name=row.name,
                source=cast(Source, row.source),
                unit=row.unit,
                lead_time_weeks=row.lead_time_weeks,
                on_hand=row.on_hand,
                safety_stock=row.safety_stock,
                lot_sizing=LotSizing(rule=cast(LotRule, row.lot_rule), quantity=row.lot_quantity),
            )
            for row in items
        ),
        bom=tuple(BomLine(parent=r.parent, child=r.child, qty_per=r.qty_per) for r in bom),
        mps=tuple(
            MpsLine(item=r.item, week=r.week, quantity=r.quantity, hull_no=r.hull_no) for r in mps
        ),
        scheduled_receipts=tuple(
            ScheduledReceipt(item=r.item, week=r.week, quantity=r.quantity, note=r.note)
            for r in receipts
        ),
    )
