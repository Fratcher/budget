import os
import sqlite3

# Define the base directory and the path to the database file
basedir = os.path.dirname(__file__)
db_path = os.path.join(basedir, 'data', 'budget.db')

# Connect to the database
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Drop existing tables if they exist
c.execute('''DROP TABLE IF EXISTS money''')
c.execute('''DROP TABLE IF EXISTS transactions''')

# Create tables and insert initial data
c.execute('''CREATE TABLE money (
             id INTEGER PRIMARY KEY,
             amount REAL)''')

c.execute('''CREATE TABLE transactions (
             id INTEGER PRIMARY KEY,
             description TEXT,
             amount REAL,
             date TEXT,
             category TEXT)''')

c.execute("INSERT INTO money (amount) VALUES (0.00)")


conn.commit()
conn.close()

