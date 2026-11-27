"""Inngangen til MRP-kjernen: ``run_mrp`` og ``result_to_dict`` (AD-2, AD-3).

``run_mrp`` beregner lavnivåkodene (som også sjekker inndataene), planlegger varene i
LLC-rekkefølge med ``plan_items`` (bruttobehov, netting, partiregel og ledetidsoffset) og gir
resultatet i fast rekkefølge. Meldingene er foreløpig tomme (story 2.4), og R11 kommer i 2.3.
"""

from dataclasses import fields, replace
from typing import Any

from .llc import low_level_codes
from .plan import plan_items
from .types import ItemResult, MrpException, MrpInput, MrpResult

WEEK_FIELDS = (
    "gross_requirements",
    "scheduled_receipts",
    "projected_on_hand",
    "net_requirements",
    "planned_order_receipts",
    "planned_order_releases",
)


def run_mrp(data: MrpInput) -> MrpResult:
    """Kjør MRP på ``data``. Ugyldige inndata gir ``MrpInputError``."""
    codes = low_level_codes(data)
    plans = plan_items(data, codes)
    items = []
    for item in data.items:
        plan = plans[item.id]
        items.append(
            ItemResult(
                id=item.id,
                name=item.name,
                unit=item.unit,
                on_hand=item.on_hand,
                low_level_code=codes[item.id],
                gross_requirements=plan.gross_requirements,
                scheduled_receipts=plan.scheduled_receipts,
                projected_on_hand=plan.projected_on_hand,
                net_requirements=plan.net_requirements,
                planned_order_receipts=plan.planned_order_receipts,
                planned_order_releases=plan.planned_order_releases,
                planned_orders=plan.planned_orders,
            )
        )
    return _ordered(items, [])


def _ordered(items: list[ItemResult], exceptions: list[MrpException]) -> MrpResult:
    """Den eneste sorteringen av resultatet (AD-3)."""
    sorted_items = tuple(
        _with_sorted_orders(item)
        for item in sorted(items, key=lambda item: (item.low_level_code, item.id))
    )
    sorted_exceptions = tuple(
        sorted(
            exceptions,
            key=lambda e: (e.type, e.item, getattr(e, "receipt_week", 0)),
        )
    )
    return MrpResult(items=sorted_items, exceptions=sorted_exceptions)


def _with_sorted_orders(item: ItemResult) -> ItemResult:
    orders = tuple(sorted(item.planned_orders, key=lambda order: order.receipt_week))
    if orders == item.planned_orders:
        return item
    return replace(item, planned_orders=orders)


def result_to_dict(result: MrpResult) -> dict[str, Any]:
    """Gi resultatet i formen til ett scenario i ``expected.json`` (AD-2).

    Bare ``dict``, ``list``, ``str`` og ``int``, så verdien kan lagres som JSON uendret.
    """
    return {
        "items": {item.id: _item_to_dict(item) for item in result.items},
        "exceptions": [_exception_to_dict(exception) for exception in result.exceptions],
    }


def _item_to_dict(item: ItemResult) -> dict[str, Any]:
    out: dict[str, Any] = {
        "name": item.name,
        "unit": item.unit,
        "on_hand": item.on_hand,
        "low_level_code": item.low_level_code,
    }
    for name in WEEK_FIELDS:
        out[name] = list(getattr(item, name))
    out["planned_orders"] = [
        {
            "receipt_week": order.receipt_week,
            "release_week": order.release_week,
            "quantity": order.quantity,
        }
        for order in item.planned_orders
    ]
    return out


def _exception_to_dict(exception: MrpException) -> dict[str, Any]:
    return {"type": exception.type} | {
        f.name: getattr(exception, f.name) for f in fields(exception)
    }
