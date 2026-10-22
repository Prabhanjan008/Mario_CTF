# Script to reset and seed the database tables.

import os
from models.db import init_database, DEFAULT_SQLITE_PATH

DB_PATH = DEFAULT_SQLITE_PATH

def init_db(reset: bool = False):
    init_database(reset=reset, seed=True)
    print("Database initialized successfully with 5 Worlds and 12 CTF Challenges.")

if __name__ == "__main__":
    init_db(reset=True)
