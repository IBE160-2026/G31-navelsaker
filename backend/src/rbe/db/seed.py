"""Oppstart av databasen: tabeller, seed av scenario A og demobrukeren (FR-1, FR-2, AD-5).

Seed og demobruker sjekkes hver for seg og skrives i hver sin transaksjon. Eksisterende
inndata seedes aldri på nytt. Demobrukerens hash oppdateres hvis passordet i konfigurasjonen
ikke lenger stemmer, så konfigurasjonen alltid gjelder.
"""

import logging
from pathlib import Path

from pwdlib import PasswordHash
from sqlalchemy import Engine, exists, select
from sqlalchemy.orm import Session

from rbe.config import Settings
from rbe.db.models import (
    Base,
    BomLineRow,
    ItemRow,
    MpsLineRow,
    PlanningSettingsRow,
    ScheduledReceiptRow,
    UserRow,
)
from rbe.db.session import make_sessionmaker
from rbe.fixture import FixtureError, load_input
from rbe.mrp.types import MrpInput

logger = logging.getLogger(__name__)

password_hash = PasswordHash.recommended()


def check_fixture(path: Path) -> None:
    """Stopp oppstarten hvis fasitfila mangler, også når databasen allerede er seedet."""
    if not path.is_file():
        raise FixtureError(f"Fant ikke fasitfila {path}. Sjekk RBE_FIXTURE_PATH.")


def seed_if_empty(session: Session, data: MrpInput) -> bool:
    """Legg inn ``data`` hvis varetabellen er tom. Gir ``True`` hvis det ble seedet."""
    if session.scalar(select(exists().select_from(ItemRow))):
        return False
    session.add_all(
        ItemRow(
            id=item.id,
            name=item.name,
            source=item.source,
            unit=item.unit,
            lead_time_weeks=item.lead_time_weeks,
            on_hand=item.on_hand,
            safety_stock=item.safety_stock,
            lot_rule=item.lot_sizing.rule,
            lot_quantity=item.lot_sizing.quantity,
        )
        for item in data.items
    )
    session.flush()  # Varene må finnes før radene som peker på dem.
    session.add_all(
        BomLineRow(parent=line.parent, child=line.child, qty_per=line.qty_per) for line in data.bom
    )
    session.add_all(
        MpsLineRow(item=line.item, week=line.week, quantity=line.quantity, hull_no=line.hull_no)
        for line in data.mps
    )
    session.add_all(
        ScheduledReceiptRow(
            item=receipt.item, week=receipt.week, quantity=receipt.quantity, note=receipt.note
        )
        for receipt in data.scheduled_receipts
    )
    session.merge(
        PlanningSettingsRow(
            id=1, first_week=data.horizon.first_week, horizon_weeks=data.horizon.weeks
        )
    )
    return True


def ensure_demo_user(session: Session, settings: Settings) -> str:
    """Sørg for at demobrukeren finnes med passordet fra konfigurasjonen.

    Gir ``"created"``, ``"updated"`` eller ``"unchanged"``. Andre brukere røres ikke.
    """
    user = session.scalar(select(UserRow).where(UserRow.username == settings.demo_username))
    if user is None:
        session.add(
            UserRow(
                username=settings.demo_username,
                password_hash=password_hash.hash(settings.demo_password),
            )
        )
        return "created"
    if password_hash.verify(settings.demo_password, user.password_hash):
        return "unchanged"
    user.password_hash = password_hash.hash(settings.demo_password)
    return "updated"


def startup(engine: Engine, settings: Settings) -> None:
    """Kjør oppstarten i fast rekkefølge: fasitsjekk, tabeller, seed og demobruker.

    Mappa til SQLite-fila er allerede opprettet av ``make_engine``.
    """
    check_fixture(settings.fixture_path)
    Base.metadata.create_all(engine)
    sessions = make_sessionmaker(engine)

    with sessions.begin() as session:
        if seed_if_empty(session, load_input(settings.fixture_path, "A")):
            logger.info("Tom database: la inn scenario A fra %s.", settings.fixture_path)
        else:
            logger.info("Databasen har allerede data. Seeder ikke på nytt.")

    with sessions.begin() as session:
        outcome = ensure_demo_user(session, settings)
    messages = {
        "created": "Opprettet demobrukeren «%s».",
        "updated": "Oppdaterte passordet til demobrukeren «%s» fra konfigurasjonen.",
        "unchanged": "Demobrukeren «%s» finnes allerede.",
    }
    logger.info(messages[outcome], settings.demo_username)
