import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime

class FinanceDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Finance Dashboard")
        self.geometry("800x600")  # Initial window size
        self.state('zoomed')  # Maximizes the window on startup

        # Create database if it doesn't exist
        self.create_database()

        # Create labels and buttons for the dashboard
        self.balance_label = ttk.Label(self, text="Current Balance: 0", font=("Arial", 16))
        self.balance_label.pack(pady=20)

        self.transaction_frame = ttk.Frame(self)
        self.transaction_frame.pack(pady=20)

        ttk.Label(self.transaction_frame, text="Type:").grid(row=0, column=0, padx=5)
        self.type_var = tk.StringVar()
        self.type_var.set("Income")
        ttk.OptionMenu(self.transaction_frame, self.type_var, "Income", "Income", "Expense").grid(row=0, column=1, padx=5)

        ttk.Label(self.transaction_frame, text="Amount ():").grid(row=1, column=0, padx=5)
        self.amount_entry = ttk.Entry(self.transaction_frame)
        self.amount_entry.grid(row=1, column=1, padx=5)

        ttk.Label(self.transaction_frame, text="Description:").grid(row=2, column=0, padx=5)
        self.description_entry = ttk.Entry(self.transaction_frame)
        self.description_entry.grid(row=2, column=1, padx=5)

        self.add_button = ttk.Button(self.transaction_frame, text="Add Transaction", command=self.add_transaction)
        self.add_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Create Treeview for displaying transactions
        self.tree = ttk.Treeview(self, columns=("Date", "Type", "Amount", "Description"), show='headings')
        self.tree.heading("Date", text="Date")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Amount", text="Amount ()")
        self.tree.heading("Description", text="Description")
        self.tree.pack(pady=20, fill='both', expand=True)

        # Update balance and populate the table initially
        self.update_balance()
        self.populate_table()

    def create_database(self):
        """Create the SQLite database and table if they do not exist."""
        conn = sqlite3.connect('finance_tracker.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                            id INTEGER PRIMARY KEY,
                            date TEXT,
                            type TEXT,
                            amount REAL,
                            description TEXT
                          )''')
        conn.commit()
        conn.close()

    def add_transaction(self):
        """Add a transaction to the database and update the balance display."""
        date = datetime.now().strftime("%Y-%m-%d")  # Automatically set the current date
        trans_type = self.type_var.get()
        description = self.description_entry.get()

        # Convert amount to float after removing thousands separator
        try:
            amount = float(self.amount_entry.get().replace(".", ""))
            self.save_transaction(date, trans_type, amount, description)
            self.update_balance()
            self.clear_entries()
            self.populate_table()  # Refresh the table
        except ValueError:
            print("Invalid amount format. Please enter a valid number.")

    def save_transaction(self, date, trans_type, amount, description):
        """Save the transaction to the database."""
        conn = sqlite3.connect('finance_tracker.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO transactions (date, type, amount, description) VALUES (?, ?, ?, ?)",
                       (date, trans_type, amount, description))
        conn.commit()
        conn.close()

    def get_transactions(self):
        """Retrieve all transactions from the database."""
        conn = sqlite3.connect('finance_tracker.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions")
        transactions = cursor.fetchall()
        conn.close()
        return transactions

    def calculate_balance(self):
        """Calculate the current balance based on transactions."""
        transactions = self.get_transactions()
        
        balance = 0.0
        for transaction in transactions:
            try:
                # Adjust indexing based on database structure
                amount = float(transaction[3])  # Assuming 4th element is amount
                if transaction[2] == "Income":
                    balance += amount
                else:
                    balance -= amount
            except ValueError:
                print(f"Invalid amount value in transaction: {transaction}")
                continue  # Skip invalid entries
        return balance

    def update_balance(self):
        """Update the balance label with the current balance."""
        balance = self.calculate_balance()
        formatted_balance = f"{balance:,.0f}"  # Format with thousands separator
        self.balance_label.config(text=f"Current Balance: {formatted_balance}")

    def clear_entries(self):
        """Clear all entry fields after a transaction is added."""
        self.amount_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.type_var.set("Income")

    def populate_table(self):
        """Populate the treeview with transactions from the database."""
        for row in self.tree.get_children():
            self.tree.delete(row)  # Clear existing rows in the table
        transactions = self.get_transactions()
        for transaction in transactions:
            date = transaction[1]  # Assuming 2nd element is date
            trans_type = transaction[2]  # Assuming 3rd element is type
            amount = f" {transaction[3]:,.0f}"  # Format with thousands separator
            description = transaction[4]  # Assuming 5th element is description
            self.tree.insert("", "end", values=(date, trans_type, amount, description))

# Run the application
if __name__ == "__main__":
    app = FinanceDashboard()
    app.mainloop()
