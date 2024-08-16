import os
import sqlite3

# Define the base directory and the path to the database file
basedir = os.path.dirname(__file__)
db_path = os.path.join(basedir, 'data', 'budget.db')

# Connect to the database
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Create tables and insert initial data (if needed)
c.execute('''CREATE TABLE IF NOT EXISTS money (
             id INTEGER PRIMARY KEY,
             amount REAL)''')

c.execute('''CREATE TABLE IF NOT EXISTS transactions (
             id INTEGER PRIMARY KEY,
             description TEXT,
             amount REAL,
             date TEXT)''')

c.execute("INSERT INTO money (amount) VALUES (3499.61)")

initial_transactions = [
    ('Venmo_Receive', 27.51, '2024-08-13'),
    ('Unknown_Boardshop', -107.66, '2024-08-13'),
    ('Electricity', -30.09, '2024-08-13'),
    ('Costco_Pizza', -4.34, '2024-08-14')
]

c.executemany("INSERT INTO transactions (description, amount, date) VALUES (?, ?, ?)", initial_transactions)

conn.commit()
conn.close()
