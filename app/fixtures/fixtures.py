from sqlalchemy.orm import Session

from app.schemas.parameter import Parameter
from sqlalchemy import MetaData


def clean_database(session: Session):
    """
    Remove all data
    """
    engine = session.get_bind()
    metadata = MetaData()
    metadata.reflect(bind=engine)
    for table in reversed(metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()


def confirm_and_load_fixtures(session: Session):
    """
    Confirm remove data
    """
    confirmation = input(
        "Do you want to clean the database before loading the fixtures (Don't accept in production)? (yes/no): ")
    if confirmation.lower() in ["yes", "y"]:
        print("Cleaning the database...")
        clean_database(session)
        print("Database cleaned.")

    print("Loading fixtures...")
    load_fixtures(session)
    print("Fixtures loaded successfully.")


def load_fixtures(session: Session):
    ###
    # Parameter fixtures
    ###

    kh = Parameter(name="Alkalinity", sub_name="KH")
    ca = Parameter(name="Calcium", sub_name="CA")
    temp = Parameter(name="Temperature", sub_name="°c")
    no2 = Parameter(name="Nitrite", sub_name="No2")
    no3 = Parameter(name="Nitrate", sub_name="No3")

    session.add(kh)
    session.add(ca)
    session.add(temp)
    session.add(no2)
    session.add(no3)

    session.commit()

    ###
    # End parameter fixtures
    ###
