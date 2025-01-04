from sqlmodel import Session
from app.db.session import engine
from app.fixtures.fixtures import load_fixtures


def main():
    with Session(engine) as session:
        load_fixtures(session)
        print("Fixtures loaded successfully!")


if __name__ == "__main__":
    main()
