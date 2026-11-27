"""Exception-meldingene E1 og E2 (FR-13, FR-14) fra de ferdige planene.

- E1 (``LeadTimeExceedsHorizon``): én per vare med bruttobehov i horisonten og ledetid lengre
  enn horisonten. Ledetid lik horisonten gir ingen E1.
- E2 (``PastDueRelease``): én per forslag med frigivelsesuke før uke 1, for alle varer uansett
  ``source``. ``weeks_past_due`` = 1 − frigivelsesuke og ``earliest_receipt_week`` = 1 + ledetid.

Kjernen lager ingen tekst (AD-2). Rekkefølgen settes i ``run._ordered`` (AD-3).
"""

from .plan import ItemPlan
from .types import LeadTimeExceedsHorizon, MrpException, MrpInput, PastDueRelease


def find_exceptions(data: MrpInput, plans: dict[str, ItemPlan]) -> list[MrpException]:
    """E1 og E2 for alle varene i ``data``, usortert."""
    first_week = data.horizon.first_week
    out: list[MrpException] = []
    for item in data.items:
        plan = plans[item.id]
        if sum(plan.gross_requirements) > 0 and item.lead_time_weeks > data.horizon.weeks:
            out.append(LeadTimeExceedsHorizon(item.id, item.lead_time_weeks, data.horizon.weeks))
        for order in plan.planned_orders:
            if order.release_week < first_week:
                out.append(
                    PastDueRelease(
                        item=item.id,
                        quantity=order.quantity,
                        receipt_week=order.receipt_week,
                        release_week=order.release_week,
                        weeks_past_due=first_week - order.release_week,
                        earliest_receipt_week=first_week + item.lead_time_weeks,
                    )
                )
    return out
