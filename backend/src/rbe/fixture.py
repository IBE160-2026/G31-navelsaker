"""Parser for fasitformatet i ``testdata/testfartoy-v1/input.json`` (AD-4, FR-2).

Dette er den eneste koden som leser fasitformatet. Scenario A er grunnlaget. B–E lages ved å
bruke ``override`` på scenarioet i ``base``: ``mps`` erstatter hele lista, ``on_hand``
overstyrer lagerbeholdningen for de oppgitte varene, og ``bom_qty`` overstyrer mengde per på
de oppgitte BOM-linjene. Stien kommer fra kalleren (seed sender ``get_settings().fixture_path``).
"""

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from rbe.mrp.types import (
    BomLine,
    Horizon,
    Item,
    LotSizing,
    MpsLine,
    MrpInput,
    ScheduledReceipt,
)

LOT_RULES = ("L4L", "FOQ")
SOURCES = ("make", "purchase")
OVERRIDE_KEYS = ("mps", "on_hand", "bom_qty")


class FixtureError(ValueError):
    """Fasitfila mangler, er ugyldig eller har et scenario som ikke kan løses."""


class _Reader:
    """Leser felt fra JSON-objekter og gir feil som nevner fila og stedet i den."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def fail(self, message: str) -> FixtureError:
        return FixtureError(f"Fasitfila {self.path}: {message}")

    def as_obj(self, value: Any, where: str) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise self.fail(f"{where} skal være et objekt.")
        return value

    def as_list(self, value: Any, where: str) -> list[Any]:
        if not isinstance(value, list):
            raise self.fail(f"{where} skal være en liste.")
        return value

    def field(self, data: dict[str, Any], key: str, where: str) -> Any:
        if key not in data:
            raise self.fail(f"feltet «{key}» mangler i {where}.")
        return data[key]

    def get_int(self, data: dict[str, Any], key: str, where: str) -> int:
        value = self.field(data, key, where)
        if isinstance(value, bool) or not isinstance(value, int):
            raise self.fail(f"feltet «{key}» i {where} skal være et heltall.")
        return value

    def get_str(self, data: dict[str, Any], key: str, where: str) -> str:
        value = self.field(data, key, where)
        if not isinstance(value, str):
            raise self.fail(f"feltet «{key}» i {where} skal være tekst.")
        return value

    def choice(self, data: dict[str, Any], key: str, where: str, allowed: tuple[str, ...]) -> Any:
        value = self.get_str(data, key, where)
        if value not in allowed:
            raise self.fail(f"feltet «{key}» i {where} er «{value}», men skal være {allowed}.")
        return value


def load_input(path: Path, scenario: str = "A") -> MrpInput:
    """Les fasitfila og gi inndataene for ``scenario`` (A–E) som kjernens typer."""
    reader = _Reader(path)
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FixtureError(f"Fant ikke fasitfila {path}.") from exc
    except (OSError, UnicodeDecodeError) as exc:
        raise FixtureError(f"Kunne ikke lese fasitfila {path}: {exc}") from exc
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise reader.fail(f"ugyldig JSON ({exc}).") from exc

    root = reader.as_obj(raw, "rota")
    scenarios = reader.as_obj(reader.field(root, "scenarios", "rota"), "«scenarios»")
    return _resolve(reader, root, scenarios, scenario, ())


def _resolve(
    reader: _Reader,
    root: dict[str, Any],
    scenarios: dict[str, Any],
    name: str,
    seen: tuple[str, ...],
) -> MrpInput:
    if name not in scenarios:
        known = ", ".join(sorted(scenarios))
        raise reader.fail(f"ukjent scenario «{name}». Kjente scenarioer: {known}.")
    if name in seen:
        chain = " → ".join([*seen, name])
        raise reader.fail(f"scenarioene peker på hverandre i ring: {chain}.")
    where = f"scenario {name}"
    spec = reader.as_obj(scenarios[name], where)
    if "base" not in spec:
        if "override" in spec:
            raise reader.fail(f"{where} har «override», men ingen «base».")
        return _parse_base(reader, root)
    base_name = reader.get_str(spec, "base", where)
    base = _resolve(reader, root, scenarios, base_name, (*seen, name))
    override = reader.as_obj(spec.get("override", {}), f"«override» i {where}")
    return _apply_override(reader, base, override, where)


def _parse_base(reader: _Reader, root: dict[str, Any]) -> MrpInput:
    horizon = reader.as_obj(reader.field(root, "horizon", "rota"), "«horizon»")
    items_raw = reader.as_list(reader.field(root, "items", "rota"), "«items»")
    bom_raw = reader.as_list(reader.field(root, "bom", "rota"), "«bom»")
    mps_raw = reader.as_list(reader.field(root, "mps", "rota"), "«mps»")
    receipts_raw = reader.as_list(
        reader.field(root, "scheduled_receipts", "rota"), "«scheduled_receipts»"
    )
    return MrpInput(
        horizon=Horizon(
            first_week=reader.get_int(horizon, "first_week", "«horizon»"),
            weeks=reader.get_int(horizon, "weeks", "«horizon»"),
        ),
        items=tuple(_parse_item(reader, raw, i) for i, raw in enumerate(items_raw)),
        bom=tuple(_parse_bom_line(reader, raw, f"«bom»[{i}]") for i, raw in enumerate(bom_raw)),
        mps=_parse_mps(reader, mps_raw, "«mps»"),
        scheduled_receipts=tuple(
            _parse_receipt(reader, raw, i) for i, raw in enumerate(receipts_raw)
        ),
    )


def _parse_item(reader: _Reader, raw: Any, index: int) -> Item:
    where = f"«items»[{index}]"
    data = reader.as_obj(raw, where)
    item_id = reader.get_str(data, "id", where)
    where = f"varen {item_id}"
    return Item(
        id=item_id,
        name=reader.get_str(data, "name", where),
        source=reader.choice(data, "source", where, SOURCES),
        unit=reader.get_str(data, "unit", where),
        lead_time_weeks=reader.get_int(data, "lead_time_weeks", where),
        on_hand=reader.get_int(data, "on_hand", where),
        safety_stock=reader.get_int(data, "safety_stock", where),
        lot_sizing=_parse_lot_sizing(reader, reader.field(data, "lot_sizing", where), where),
    )


def _parse_lot_sizing(reader: _Reader, raw: Any, owner: str) -> LotSizing:
    where = f"«lot_sizing» for {owner}"
    data = reader.as_obj(raw, where)
    rule = reader.choice(data, "rule", where, LOT_RULES)
    if rule == "FOQ":
        if "quantity" not in data:
            raise reader.fail(f"{where} har regelen FOQ, men mangler «quantity».")
        quantity = reader.get_int(data, "quantity", where)
        if quantity <= 0:
            raise reader.fail(f"«quantity» i {where} skal være større enn 0.")
        return LotSizing(rule=rule, quantity=quantity)
    quantity = reader.get_int(data, "quantity", where) if "quantity" in data else None
    return LotSizing(rule=rule, quantity=quantity)


def _parse_bom_line(reader: _Reader, raw: Any, where: str) -> BomLine:
    data = reader.as_obj(raw, where)
    return BomLine(
        parent=reader.get_str(data, "parent", where),
        child=reader.get_str(data, "child", where),
        qty_per=reader.get_int(data, "qty_per", where),
    )


def _parse_mps(reader: _Reader, raw: list[Any], where: str) -> tuple[MpsLine, ...]:
    lines = []
    for index, line_raw in enumerate(raw):
        line_where = f"{where}[{index}]"
        data = reader.as_obj(line_raw, line_where)
        lines.append(
            MpsLine(
                item=reader.get_str(data, "item", line_where),
                week=reader.get_int(data, "week", line_where),
                quantity=reader.get_int(data, "quantity", line_where),
                hull_no=reader.get_int(data, "hull_no", line_where),
            )
        )
    return tuple(lines)


def _parse_receipt(reader: _Reader, raw: Any, index: int) -> ScheduledReceipt:
    where = f"«scheduled_receipts»[{index}]"
    data = reader.as_obj(raw, where)
    note = reader.get_str(data, "note", where) if "note" in data else ""
    return ScheduledReceipt(
        item=reader.get_str(data, "item", where),
        week=reader.get_int(data, "week", where),
        quantity=reader.get_int(data, "quantity", where),
        note=note,
    )


def _apply_override(
    reader: _Reader, base: MrpInput, override: dict[str, Any], scenario: str
) -> MrpInput:
    unknown = sorted(set(override) - set(OVERRIDE_KEYS))
    if unknown:
        raise reader.fail(
            f"{scenario} har ukjente overstyringer: {', '.join(unknown)}. "
            f"Kjente: {', '.join(OVERRIDE_KEYS)}."
        )
    result = base
    if "mps" in override:
        mps_raw = reader.as_list(override["mps"], f"«mps» i {scenario}")
        mps = _parse_mps(reader, mps_raw, f"«mps» i {scenario}")
        known_ids = {item.id for item in base.items}
        for line in mps:
            if line.item not in known_ids:
                raise reader.fail(f"{scenario} har MPS for varen {line.item}, som ikke finnes.")
        result = replace(result, mps=mps)
    if "on_hand" in override:
        result = _override_on_hand(reader, result, override["on_hand"], scenario)
    if "bom_qty" in override:
        result = _override_bom_qty(reader, result, override["bom_qty"], scenario)
    return result


def _override_on_hand(reader: _Reader, base: MrpInput, raw: Any, scenario: str) -> MrpInput:
    where = f"«on_hand» i {scenario}"
    data = reader.as_obj(raw, where)
    known_ids = {item.id for item in base.items}
    for item_id in data:
        if item_id not in known_ids:
            raise reader.fail(
                f"{scenario} overstyrer lageret for varen {item_id}, som ikke finnes."
            )
    values = {item_id: reader.get_int(data, item_id, where) for item_id in data}
    items = tuple(
        replace(item, on_hand=values[item.id]) if item.id in values else item for item in base.items
    )
    return replace(base, items=items)


def _override_bom_qty(reader: _Reader, base: MrpInput, raw: Any, scenario: str) -> MrpInput:
    where = f"«bom_qty» i {scenario}"
    entries = reader.as_list(raw, where)
    changes: dict[tuple[str, str], int] = {}
    known = {(line.parent, line.child) for line in base.bom}
    for index, entry in enumerate(entries):
        line = _parse_bom_line(reader, entry, f"{where}[{index}]")
        key = (line.parent, line.child)
        if key not in known:
            raise reader.fail(
                f"{scenario} overstyrer BOM-linjen {line.parent} → {line.child}, som ikke finnes."
            )
        changes[key] = line.qty_per
    bom = tuple(
        replace(line, qty_per=changes[(line.parent, line.child)])
        if (line.parent, line.child) in changes
        else line
        for line in base.bom
    )
    return replace(base, bom=bom)
