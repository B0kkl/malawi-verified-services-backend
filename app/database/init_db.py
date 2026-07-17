from app.database.base import Base
from app.database.session import engine


def init_database():
    print("Starting database initialization...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")


if __name__ == "__main__":
    init_database()
