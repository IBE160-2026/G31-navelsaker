"""Bruttobehov, netting, partiregel og ledetidsoffset per vare (FR-10, FR-11).

Varene planlegges i rekkefølgen (``low_level_code``, ``id``), så alle foreldre er ferdige før
barnet. Uke *t* har indeks *t* − 1 (``horizon.first_week`` er alltid 1, se ``Horizon``).

- Bruttobehov (R3): varens MPS-linjer per uke, pluss forelderens forslag × mengde per i
  frigivelsesuka. Barna leser forelderens ``planned_orders``, ikke arrayen.
- Netting (R2, R5, R7): startlageret gjelder før uke 1, og åpne ordre dekker behov samme uke.
  NB = max(0, BB + SS − (BL forrige + ÅO)) og BL = BL forrige + ÅO + PM − BB.
- Partiregel (R6): L4L gir PM = NB, og FOQ med Q gir minste multiplum av Q som er ≥ NB.
- Forslag (R8, R9): frigivelsesuke = mottaksuke − ledetid. Frigivelser før uke 1 står bare i
  ``planned_orders``. Åpne ordre flyttes aldri (R10).
"""

from collections import defaultdict
from dataclasses import dataclass

from .types import BomLine, Item, MrpInput, PlannedOrder


@dataclass(frozen=True, slots=True)
class ItemPlan:
    """Ukesarrayene og forslagene for én vare. Indeks 0 er uke 1."""

    gross_requirements: tuple[int, ...]
    scheduled_receipts: tuple[int, ...]
    projected_on_hand: tuple[int, ...]
    net_requirements: tuple[int, ...]
    planned_order_receipts: tuple[int, ...]
    planned_order_releases: tuple[int, ...]
    planned_orders: tuple[PlannedOrder, ...]


def plan_items(data: MrpInput, codes: dict[str, int]) -> dict[str, ItemPlan]:
    """Planlegg alle varene. ``codes`` er lavnivåkodene, og inndataene er sjekket."""
    weeks = data.horizon.weeks
    lines_by_child: dict[str, list[BomLine]] = defaultdict(list)
    for line in data.bom:
        lines_by_child[line.child].append(line)
    mps_by_item: dict[str, list[int]] = defaultdict(lambda: [0] * weeks)
    for mps in data.mps:
        mps_by_item[mps.item][mps.week - 1] += mps.quantity
    receipts_by_item: dict[str, list[int]] = defaultdict(lambda: [0] * weeks)
    for receipt in data.scheduled_receipts:
        receipts_by_item[receipt.item][receipt.week - 1] += receipt.quantity

    plans: dict[str, ItemPlan] = {}
    for item in sorted(data.items, key=lambda item: (codes[item.id], item.id)):
        gross = list(mps_by_item.get(item.id, [0] * weeks))
        for line in lines_by_child.get(item.id, ()):
            for order in plans[line.parent].planned_orders:
                if order.release_week >= 1:
                    gross[order.release_week - 1] += order.quantity * line.qty_per
        receipts = receipts_by_item.get(item.id, [0] * weeks)
        plans[item.id] = _plan_item(item, gross, receipts)
    return plans


def _plan_item(item: Item, gross: list[int], receipts: list[int]) -> ItemPlan:
    weeks = len(gross)
    on_hand: list[int] = []
    net: list[int] = []
    planned: list[int] = []
    previous = item.on_hand
    for week in range(weeks):
        available = previous + receipts[week]
        need = max(0, gross[week] + item.safety_stock - available)
        receipt = _lot_size(item, need)
        previous = available + receipt - gross[week]
        on_hand.append(previous)
        net.append(need)
        planned.append(receipt)

    orders = tuple(
        PlannedOrder(
            receipt_week=week + 1,
            release_week=week + 1 - item.lead_time_weeks,
            quantity=quantity,
        )
        for week, quantity in enumerate(planned)
        if quantity > 0
    )
    releases = [0] * weeks
    for order in orders:
        if order.release_week >= 1:
            releases[order.release_week - 1] += order.quantity
    return ItemPlan(
        gross_requirements=tuple(gross),
        scheduled_receipts=tuple(receipts),
        projected_on_hand=tuple(on_hand),
        net_requirements=tuple(net),
        planned_order_receipts=tuple(planned),
        planned_order_releases=tuple(releases),
        planned_orders=orders,
    )


def _lot_size(item: Item, need: int) -> int:
    """R6: L4L gir NB, og FOQ med Q gir minste multiplum av Q som er ≥ NB."""
    if need <= 0:
        return 0
    if item.lot_sizing.rule == "FOQ":
        quantity = item.lot_sizing.quantity
        assert quantity is not None and quantity >= 1  # sjekket i _check_input
        return -(-need // quantity) * quantity
    return need
