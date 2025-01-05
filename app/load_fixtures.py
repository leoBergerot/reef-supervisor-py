from sqlmodel import Session
from app.db.session import engine
from app.fixtures.fixtures import confirm_and_load_fixtures


def main():
    with Session(engine) as session:
        confirm_and_load_fixtures(session)


if __name__ == "__main__":
    main()
