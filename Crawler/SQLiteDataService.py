import sqlite3

class ChefKochSQLiteService:
    """Handles concrete SQLite connections."""
    def __init__(self, db_path: str = r"..\Data\chefkoch.db"):
        pass

    def get_connection(self) -> sqlite3.Connection:
        pass