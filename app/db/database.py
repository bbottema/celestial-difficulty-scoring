import sqlite3

from utils.event_bus_config import database_ready_bus

database_ready_bus.on_next('DATABASE_READY')

def get_db_connection():
    return sqlite3.connect('celestial.db')


def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # cursor.execute('''DROP TABLE IF EXISTS observation_sites''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS observation_sites(
                      id INTEGER PRIMARY KEY, 
                        name TEXT,
                        latitude REAL,
                        longitude REAL,
                        light_pollution TEXT)''')

    conn.commit()
    conn.close()
