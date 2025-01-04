from sqlalchemy.orm import Session

from app.schemas.parameter import Parameter


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
