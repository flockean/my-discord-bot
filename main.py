from src.controller.client_controller import start_bot
from src.database.db_setup import init_db


def main():
    init_db()
    start_bot()


if __name__ == "__main__":
    main()
