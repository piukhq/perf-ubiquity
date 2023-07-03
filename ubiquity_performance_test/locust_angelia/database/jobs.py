from datetime import UTC, datetime

from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.exc import DatabaseError

from ubiquity_performance_test.locust_angelia.database.models import SchemeAccount, SchemeAccountUserAssociation, User
from ubiquity_performance_test.locust_angelia.database.session import db_session
from ubiquity_performance_test.settings import fake


def query_status(card_id: int) -> list:
    """Queries a loyalty card's current status.

    :param card_id: id of the card to be queried

    :returns: status of the card

    """

    query = select(SchemeAccountUserAssociation.link_status).where(
        SchemeAccountUserAssociation.scheme_account_id == card_id
    )

    try:
        result = db_session.execute(query).all()
    except DatabaseError:
        logger.error(f"Could not fetch card status for card {card_id}!")
        return []
    else:
        return [x[0] for x in result]


def set_status_for_loyalty_card(card_id: int, status: int) -> None:
    """
    Set loyalty card status.

    :param card_id: id of the card to be queried
    :param status: status to be set
    """

    query = (
        update(SchemeAccountUserAssociation)
        .where(SchemeAccountUserAssociation.scheme_account_id == card_id)
        .values(link_status=status)
    )
    try:
        db_session.execute(query)
        db_session.commit()
    except DatabaseError:
        logger.error(f"Could not update card status for card {card_id}!")


def add_join(email: str, loyalty_plan: int) -> int:  # Not currently used - for future use if needed
    """
    **N.b. Not currently being used, but have left this in here in case we need it in the future. Re-implementation of
    this would require us to store the user email alongside the token to avoid having to decrypt Angelia tokens.**
    Adds a failed join to the database for this user and returns its id.

    :param email: email of the user adding the join
    :param loyalty_plan: id of the loyalty plan

    :returns: id of the created loyalty card in failed join state

    """

    query = select(User).where(User.email == email)

    result = db_session.execute(query).one()

    user_id = result.User.id

    loyalty_card = SchemeAccount(
        status=901,
        order=1,
        created=datetime.now(tz=UTC),
        updated=datetime.now(tz=UTC),
        card_number=fake.credit_card_number(),
        barcode=fake.pyint(),
        main_answer=fake.credit_card_number(),
        scheme_id=loyalty_plan,
        is_deleted=False,
        balances={},
        vouchers={},
        transactions=[],
        pll_links=[],
        formatted_images={},
        originating_journey=0,
    )

    db_session.add(loyalty_card)
    db_session.flush()

    user_association_object = SchemeAccountUserAssociation(
        scheme_account_id=loyalty_card.id, user_id=user_id, auth_provided=True
    )

    db_session.add(user_association_object)
    db_session.commit()

    logger.info(f"Created Failed join with ID: {loyalty_card.id}")

    return loyalty_card.id
