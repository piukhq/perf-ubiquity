import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import DatabaseError

from locust_angelia.database.db import DB
from locust_angelia.database.models import SchemeAccount, SchemeAccountUserAssociation, User
from settings import fake

logger = logging.getLogger("Database_Handler")


def query_status(card_id):
    DB().open()
    session = DB().session

    query = select(User).where(SchemeAccount).id == card_id

    try:
        result = session.execute(query).one()
    except DatabaseError:
        logger.error(f"Could not fetch card status for card {card_id}!")
    else:
        return result.SchemeAccount.status

    DB().close()


def add_join(email, loyalty_plan):  # Not using this for now, but will leave in in case we need this in the future.
    DB().open()
    session = DB().session

    query = select(User).where(User.email == email)

    result = session.execute(query).one()

    user_id = result.User.id
    print(user_id)

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

    DB().close()

    logger.info(f"Created Failed join with ID: {loyalty_card.id}")

    return loyalty_card.id
