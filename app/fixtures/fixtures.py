from sqlalchemy.orm import Session

from app.schemas.parameter import Parameter
from sqlalchemy import MetaData
import typer


def clean_database(session: Session):
    """
    Remove all data
    """
    engine = session.get_bind()
    metadata = MetaData()
    metadata.reflect(bind=engine)
    for table in reversed(metadata.sorted_tables):
        if table.name == "alembic_version":
            continue
        session.execute(table.delete())
    session.commit()


def confirm_and_load_fixtures(session: Session):
    """
    Confirm remove data
    """
    confirmation = typer.confirm(
        "Do you want to clean the database before loading the fixtures (Don't accept in production)?"
    )
    if confirmation:
        print("Cleaning the database...")
        clean_database(session)
        print("Database cleaned.")
    else:
        exit()

    print("Loading fixtures...")
    load_fixtures(session)
    print("Fixtures loaded successfully.")


def load_fixtures(session: Session):
    ###
    # Parameter fixtures (catalog defaults by water type)
    ###

    parameters = [
        Parameter(name="Temperature", sub_name="°c", need_value=True, for_seawater=True, for_freshwater=True),
        Parameter(name="Alkalinity", sub_name="KH", need_value=True, for_seawater=True, for_freshwater=True),
        Parameter(name="Calcium", sub_name="CA", need_value=True, for_seawater=True, for_freshwater=False),
        Parameter(name="Magnesium", sub_name="Mg", need_value=True, for_seawater=True, for_freshwater=False),
        Parameter(name="Nitrate", sub_name="No3", need_value=True, for_seawater=True, for_freshwater=True),
        Parameter(name="Phosphate", sub_name="PO4", need_value=True, for_seawater=True, for_freshwater=False),
        Parameter(name="Salinity", sub_name="Density", need_value=True, for_seawater=True, for_freshwater=False),
        Parameter(name="Power of hydrogen", sub_name="pH", need_value=True, for_seawater=False, for_freshwater=True),
        Parameter(name="Nitrite", sub_name="No2", need_value=True, for_seawater=False, for_freshwater=True),
        Parameter(name="Water change", sub_name="%", need_value=False, for_seawater=False, for_freshwater=True),
    ]

    for parameter in parameters:
        session.add(parameter)

    session.commit()

    ###
    # End parameter fixtures
    ###
