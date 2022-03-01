import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import DatabaseError

from locust_angelia.database.db import DB
from locust_angelia.database.models import SchemeAccount, SchemeAccountUserAssociation, User
from settings import fake

logger = logging.getLogger("Database_Handler")


def query_status(card_id: int) -> int:
    """Queries a loyalty card's current status.

    :param card_id: id of the card to be queried

    :returns: status of the card

    """
    with DB().open() as session:

        query = select(SchemeAccount.status).where(SchemeAccount.id == card_id)

        try:
            result = session.execute(query).one()
        except DatabaseError:
            logger.error(f"Could not fetch card status for card {card_id}!")
        else:
            return result[0]


def add_join(email: str, loyalty_plan: int):  # Not currently used - for future use if needed
    """
    **N.b. Not currently being used, but have left this in here in case we need it in the future. Re-implementation of
    this would require us to store the user email alongside the token to avoid having to decrypt Angelia tokens.**
    Adds a failed join to the database for this user and returns its id.

    :param email: email of the user adding the join
    :param loyalty_plan: id of the loyalty plan

    :returns: id of the created loyalty card in failed join state

    """
    with DB().open() as session:

        query = select(User).where(User.email == email)

        result = session.execute(query).one()

        user_id = result.User.id

        loyalty_card = SchemeAccount(
            status=901,
            order=1,
            created=datetime.now(),
            updated=datetime.now(),
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

        session.add(loyalty_card)
        session.flush()

        user_association_object = SchemeAccountUserAssociation(
            scheme_account_id=loyalty_card.id, user_id=user_id, auth_provided=True
        )

        session.add(user_association_object)
        session.commit()

    logger.info(f"Created Failed join with ID: {loyalty_card.id}")

    return loyalty_card.id
