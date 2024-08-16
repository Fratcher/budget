from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QVBoxLayout, QPushButton, QWidget, QListWidget, QMessageBox
from PyQt5.QtGui import QIcon
import sys, os
import sqlite3
from datetime import datetime, timedelta

basedir = os.path.dirname(__file__)
db_path = os.path.join(basedir, 'data', 'budget.db')  # Update the path to point to the dist folder

class AddTransactionWindow(QtWidgets.QWidget):

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Add Transaction")
        self.resize(400, 300)
        layout = QVBoxLayout()

        self.description_input = QtWidgets.QLineEdit(self)
        self.description_input.setPlaceholderText("Description")
        layout.addWidget(self.description_input)

        self.amount_input = QtWidgets.QLineEdit(self)
        self.amount_input.setPlaceholderText("Amount")
        layout.addWidget(self.amount_input)

        self.date_input = QtWidgets.QLineEdit(self)
        self.date_input.setPlaceholderText("Date (YYYY-MM-DD)")
        layout.addWidget(self.date_input)

        add_button = QPushButton("Add Transaction")
        add_button.clicked.connect(self.add_transaction)
        layout.addWidget(add_button)

        self.setLayout(layout)

    def add_transaction(self):
        description = self.description_input.text()
        amount = float(self.amount_input.text())
        date = self.date_input.text()

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        # Insert the new transaction
        c.execute("INSERT INTO transactions (description, amount, date) VALUES (?, ?, ?)", (description, amount, date))

        # Fetch the current amount
        c.execute("SELECT amount FROM money WHERE id = 1")
        current_amount = c.fetchone()[0]

        # Update the current amount
        new_amount = current_amount + amount
        c.execute("UPDATE money SET amount = ? WHERE id = 1", (new_amount,))

        conn.commit()
        conn.close()

        self.main_window.update_data()
        self.close()

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Budget Buddy")
        self.resize(1000, 800)
        layout = QVBoxLayout()

        # Connect to the database
        self.conn = sqlite3.connect(db_path)
        self.c = self.conn.cursor()

        # Current amount of money
        self.current_amount_label = QLabel("Current Amount: $0.00")
        self.current_amount_label.setMargin(10)
        layout.addWidget(self.current_amount_label)

        # Money spent this week
        self.weekly_spent_label = QLabel("Money Spent This Week: $0.00")
        self.weekly_spent_label.setMargin(10)
        layout.addWidget(self.weekly_spent_label)

        # Money spent this month
        self.monthly_spent_label = QLabel("Money Spent This Month: $0.00")
        self.monthly_spent_label.setMargin(10)
        layout.addWidget(self.monthly_spent_label)

        # Money spent this year
        self.yearly_spent_label = QLabel("Money Invested: $702.00")
        self.yearly_spent_label.setMargin(10)
        layout.addWidget(self.yearly_spent_label)

        # Recent transactions
        self.recent_transactions_label = QLabel("Recent Transactions:")
        self.recent_transactions_label.setMargin(10)
        layout.addWidget(self.recent_transactions_label)

        self.recent_transactions_list = QListWidget()
        layout.addWidget(self.recent_transactions_list)

        add_transaction_button = QPushButton("Add Transaction")
        add_transaction_button.setIcon(QIcon(os.path.join(basedir, "icons", "money.svg")))
        add_transaction_button.clicked.connect(self.open_add_transaction_window)
        layout.addWidget(add_transaction_button)

        delete_transaction_button = QPushButton("Delete Transaction")
        delete_transaction_button.clicked.connect(self.delete_transaction)
        layout.addWidget(delete_transaction_button)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)
        self.show()

        self.update_data()

    def open_add_transaction_window(self):
        self.add_transaction_window = AddTransactionWindow(self)
        self.add_transaction_window.show()

    def delete_transaction(self):
        selected_items = self.recent_transactions_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a transaction to delete.")
            return

        selected_item = selected_items[0]
        transaction_text = selected_item.text()
        description, amount, date = transaction_text.split(": $")[0], float(transaction_text.split(": $")[1].split(" on ")[0]), transaction_text.split(" on ")[1]

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        # Delete the selected transaction
        c.execute("DELETE FROM transactions WHERE description = ? AND amount = ? AND date = ?", (description, amount, date))

        # Fetch the current amount
        c.execute("SELECT amount FROM money WHERE id = 1")
        current_amount = c.fetchone()[0]

        # Update the current amount
        new_amount = current_amount - amount
        c.execute("UPDATE money SET amount = ? WHERE id = 1", (new_amount,))

        conn.commit()
        conn.close()

        self.update_data()

    def update_data(self):
        # Fetch current amount of money
        self.c.execute("SELECT amount FROM money WHERE id = 1")
        current_amount = self.c.fetchone()[0]

        # Calculate weekly spending (only negative values)
        one_week_ago = datetime.now() - timedelta(days=7)
        self.c.execute("SELECT SUM(amount) FROM transactions WHERE date >= ? AND amount < 0", (one_week_ago.strftime('%Y-%m-%d'),))
        weekly_spent = self.c.fetchone()[0] or 0.0

        # Calculate monthly spending (only negative values)
        current_month = datetime.now().strftime('%Y-%m')
        self.c.execute("SELECT SUM(amount) FROM transactions WHERE date LIKE ? AND amount < 0", (current_month + '%',))
        monthly_spent = self.c.fetchone()[0] or 0.0

        # Fetch recent transactions
        self.c.execute("SELECT description, amount, date FROM transactions ORDER BY date DESC LIMIT 5")
        transactions = self.c.fetchall()

        # Update labels
        self.current_amount_label.setText(f"Current Amount: ${current_amount:.2f}")
        self.weekly_spent_label.setText(f"Money Spent This Week: ${weekly_spent:.2f}")
        self.monthly_spent_label.setText(f"Money Spent This Month: ${monthly_spent:.2f}")

        # Update recent transactions list
        self.recent_transactions_list.clear()
        for transaction in transactions:
            self.recent_transactions_list.addItem(f"{transaction[0]}: ${transaction[1]:.2f} on {transaction[2]}")

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(os.path.join(basedir, 'icons', 'icon.svg')))
    w = MainWindow()
    app.exec()
