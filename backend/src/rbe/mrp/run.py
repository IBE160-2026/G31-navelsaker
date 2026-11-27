"""Inngangen til MRP-kjernen: ``run_mrp`` og ``result_to_dict`` (AD-2, AD-3).

``run_mrp`` sjekker referansene i inndataene, beregner lavnivåkodene og gir resultatet i fast
rekkefølge. Ukesarrayene er foreløpig nuller, og forslag og meldinger er tomme. Story 2.2–2.4
fyller dem inn i den samme formen.
"""

from collections import Counter
from dataclasses import fields, replace
from typing import Any

from .llc import MrpInputError, low_level_codes
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
    _check_input(data)
    codes = low_level_codes(data)
    zeros = (0,) * data.horizon.weeks
    items = [
        ItemResult(
            id=item.id,
            name=item.name,
            unit=item.unit,
            on_hand=item.on_hand,
            low_level_code=codes[item.id],
            gross_requirements=zeros,
            scheduled_receipts=zeros,
            projected_on_hand=zeros,
            net_requirements=zeros,
            planned_order_receipts=zeros,
            planned_order_releases=zeros,
            planned_orders=(),
        )
        for item in data.items
    ]
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


def _check_input(data: MrpInput) -> None:
    """Avvis like vare-id-er, like BOM-linjer og linjer mot varer som ikke finnes."""
    id_counts = Counter(item.id for item in data.items)
    duplicates = sorted(item_id for item_id, count in id_counts.items() if count > 1)
    if duplicates:
        raise MrpInputError(f"Varen finnes flere ganger: {', '.join(duplicates)}.")

    line_counts = Counter((line.parent, line.child) for line in data.bom)
    duplicate_lines = sorted(key for key, count in line_counts.items() if count > 1)
    if duplicate_lines:
        shown = ", ".join(f"{parent} → {child}" for parent, child in duplicate_lines)
        raise MrpInputError(f"BOM-linjen finnes flere ganger: {shown}.")

    known = set(id_counts)
    for line in data.bom:
        for role, item_id in (("forelder", line.parent), ("barn", line.child)):
            if item_id not in known:
                raise MrpInputError(
                    f"BOM-linjen {line.parent} → {line.child} har {role} {item_id}, "
                    "som ikke finnes."
                )
    for mps in data.mps:
        if mps.item not in known:
            raise MrpInputError(
                f"MPS-linjen for uke {mps.week} gjelder varen {mps.item}, som ikke finnes."
            )
    for receipt in data.scheduled_receipts:
        if receipt.item not in known:
            raise MrpInputError(
                f"Den åpne ordren i uke {receipt.week} gjelder varen {receipt.item}, "
                "som ikke finnes."
            )


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
