"""Lavnivåkoder (FR-10): hver vare planlegges én gang, etter alle foreldrene sine.

Lavnivåkoden er den lengste veien fra en vare uten forelder. Beregningen er en topologisk
gjennomgang (Kahn) uten rekursjon, så dype BOM-er ikke når rekursjonsgrensen.
"""

from collections import Counter, deque

from .types import Item, MrpInput


class MrpInputError(ValueError):
    """Inndataene kan ikke planlegges.

    Grunner: ukjente varer, duplikater, en sykel i BOM-en, første uke ≠ 1, en MPS-linje eller
    åpen ordre utenfor horisonten, negativ ledetid, ukjent partiregel eller FOQ uten kvantum ≥ 1.
    Mengde per < 1 og negative mengder avvises av API-et (FR-8), ikke av kjernen.
    """


def low_level_codes(data: MrpInput) -> dict[str, int]:
    """Gi lavnivåkoden per vare-id. Varer utenfor BOM-en får 0.

    Ugyldige inndata (like id-er eller linjer, ukjente varer) og en sykel gir
    ``MrpInputError``. Sykelfeilen nevner varene i én sykel.
    """
    _check_input(data)
    children: dict[str, set[str]] = {item.id: set() for item in data.items}
    parents: dict[str, set[str]] = {item.id: set() for item in data.items}
    for line in data.bom:
        children[line.parent].add(line.child)
        parents[line.child].add(line.parent)

    waiting = {item_id: len(found) for item_id, found in parents.items()}
    codes = dict.fromkeys(children, 0)
    queue = deque(sorted(item_id for item_id, count in waiting.items() if count == 0))
    while queue:
        parent = queue.popleft()
        for child in sorted(children[parent]):
            codes[child] = max(codes[child], codes[parent] + 1)
            waiting[child] -= 1
            if waiting[child] == 0:
                queue.append(child)

    remaining = {item_id for item_id, count in waiting.items() if count > 0}
    if remaining:
        cycle = _find_cycle(parents, remaining)
        shown = " → ".join([*cycle, cycle[0]])
        raise MrpInputError(f"BOM-en har en sykel: {shown}.")
    return codes


def _check_input(data: MrpInput) -> None:
    """Avvis ugyldige inndata med ``MrpInputError`` (se klassen for grunnene)."""
    if data.horizon.first_week != 1:
        raise MrpInputError(
            f"Første planuke er {data.horizon.first_week}, men kjernen krever uke 1."
        )
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

    weeks = data.horizon.weeks
    for mps in data.mps:
        if not 1 <= mps.week <= weeks:
            raise MrpInputError(
                f"MPS-linjen for varen {mps.item} har uke {mps.week}, "
                f"som er utenfor horisonten (uke 1–{weeks})."
            )
    for receipt in data.scheduled_receipts:
        if not 1 <= receipt.week <= weeks:
            raise MrpInputError(
                f"Den åpne ordren for varen {receipt.item} har uke {receipt.week}, "
                f"som er utenfor horisonten (uke 1–{weeks})."
            )
    for item in data.items:
        _check_item(item)


def _check_item(item: Item) -> None:
    """Avvis negativ ledetid, ukjent partiregel og FOQ uten kvantum ≥ 1."""
    if item.lead_time_weeks < 0:
        raise MrpInputError(f"Varen {item.id} har negativ ledetid ({item.lead_time_weeks}).")
    rule = item.lot_sizing.rule
    if rule not in ("L4L", "FOQ"):
        raise MrpInputError(f"Varen {item.id} har ukjent partiregel «{rule}».")
    quantity = item.lot_sizing.quantity
    if rule == "FOQ" and (quantity is None or quantity < 1):
        raise MrpInputError(f"Varen {item.id} har FOQ uten kvantum ≥ 1 (kvantum {quantity}).")


def _find_cycle(parents: dict[str, set[str]], remaining: set[str]) -> list[str]:
    """Finn én sykel blant varene som står igjen, i retning forelder → barn, fra minste id.

    Hver vare som står igjen, har minst én forelder som også står igjen. Går vi oppover fra
    en av dem, møter vi derfor før eller siden en vare vi har sett, og det er sykelen.
    """
    path: list[str] = []
    seen: dict[str, int] = {}
    node = min(remaining)
    while node not in seen:
        seen[node] = len(path)
        path.append(node)
        node = min(parent for parent in parents[node] if parent in remaining)
    cycle = path[seen[node] :][::-1]
    start = cycle.index(min(cycle))
    return cycle[start:] + cycle[:start]
