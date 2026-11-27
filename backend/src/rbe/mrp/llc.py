"""Lavnivåkoder (FR-10): hver vare planlegges én gang, etter alle foreldrene sine.

Lavnivåkoden er den lengste veien fra en vare uten forelder. Beregningen er en topologisk
gjennomgang (Kahn) uten rekursjon, så dype BOM-er ikke når rekursjonsgrensen.
"""

from collections import deque

from .types import MrpInput


class MrpInputError(ValueError):
    """Inndataene kan ikke planlegges: ukjente varer, duplikater eller en sykel i BOM-en."""


def low_level_codes(data: MrpInput) -> dict[str, int]:
    """Gi lavnivåkoden per vare-id. Varer utenfor BOM-en får 0.

    Forutsetter at BOM-linjene bare viser til varer som finnes (``run_mrp`` sjekker det).
    En sykel gir ``MrpInputError`` som nevner varene i én sykel.
    """
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
