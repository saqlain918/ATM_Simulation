ATM Simulation Project

This is a command-line ATM simulation implemented in Python, designed to manage user accounts and transactions using CSV files for persistent storage. The project supports user login, balance checks, deposits, withdrawals, transfers, PIN changes, soft account deletion, and transaction history viewing, with features like PIN uniqueness and transaction logging.

Features

User Management: Stores user data (name, account number, hashed PIN, address, balance, deletion status) in users.csv.
Transaction Logging: Records deposits, withdrawals, and transfers with timestamps and target accounts in transactions.csv.
Soft Delete: Marks accounts as deleted (is_deleted=1) without removing data.
PIN Security: Enforces 4-digit PINs, ensures uniqueness, and uses SHA-256 hashing.
Input Validation: Validates amounts (e.g., 10 or 10.50, max 10000.00) and account numbers.
Error Handling: Handles invalid inputs, permissions, and CSV errors gracefully.
PEP 8/257 Compliance: Follows Python style and docstring guidelines.

Project Structure

Codes
    ├─ user.py 
    ├─ atm.py 
    ├─ main.py 
CSV_files
    ├─ users.csv  
    ├── transactions.csv  
├── requirements.txt  
├── README.md         

Prerequisites

Python: Version 3.6 or higher (3.8+ recommended, as used in PyCharm’s virtual environment).

No external dependencies: Uses Python standard library modules (csv, os, hashlib, re, datetime, typing).

Operating System: Tested on Linux (e.g., Ubuntu); should work on Windows/Mac with path adjustments.

IDE : PyCharm for development and running.

Setup Instructions

Clone the Repository:
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

Install Dependencies:

The requirements.txt as no external packages are needed.but other python libraries are mention.

pip install -r requirements.txt

Confirms standard library usage.

Right-click project folder → Mark Directory as → Sources Root.

Run the Program:
Via PyCharm:

Expected output:

✅ Initialized /path/to/your-repo-name/users.csv with 2 rows
✅ Initialized /path/to/your-repo-name/transactions.csv
--- Login ---
Enter account number:
Login:
Use predefined users:
Account: 123456789, PIN: 5678 (Ahmed)
Account: 987654321, PIN: 1234 (Saqlain Rai)
Example:

Enter account number: 123456789
Enter 4-digit PIN: 5678
✅ Login successful!
--- ATM Menu ---
1. Check Balance
2. Deposit Funds
3. Withdraw Funds
4. Transfer Funds
5. Change PIN
6. View Transactions
7. Delete Account
8. Exit
Choose (1-8):
Example Operations:
Deposit: Choose 2, enter 100.00 → Balance becomes 100.00.
Withdraw: Choose 3, enter 50.00 → Balance becomes 50.00.
Transfer: Choose 4, enter 987654321, 25.00 → Transfers to Saqlain Rai.
View Transactions: Choose 6:
--- Transaction History ---
2025-06-24 16:16:00 | Deposit | 100.00 | 123456789 | Credit
2025-06-24 16:17:00 | Withdrawal | 50.00 | 123456789 | Debit
2025-06-24 16:18:00 | Transfer | 25.00 | 987654321 | Debit
Soft Delete: Choose 7, confirm yes → Account marked is_deleted=1.
