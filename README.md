ATM Simulation Project

This is a command-line ATM simulation implemented in Python, designed to manage user accounts and transactions using CSV files for persistent storage. The project supports user login, balance checks, deposits, withdrawals, transfers, PIN changes, soft account deletion, and transaction history viewing, with features like PIN uniqueness and transaction logging.

Features

User Management: Stores user data (name, account number, hashed PIN, address, balance, deletion status) in users.csv.
Transaction Logging: Records deposits, withdrawals, and transfers with timestamps and target accounts in transactions.csv.
Soft Delete: Marks accounts as deleted (is_deleted=1) without removing data.
PIN Security: Enforces 4-digit PINs, ensures uniqueness, and uses SHA-256 hashing.
Input Validation: Validates amounts (e.g., 10 or 10.50, max 10000.00) and account numbers.
Error Handling: Handles invalid inputs, permissions, and CSV errors gracefully.

Project Structure

├── user.py 
├── atm.py  
├── main.py 
├── requirements.txt   
├── users.csv       
├── transactions.csv  
├── README.md         


Uses Python standard library modules (csv, os, hashlib, re, datetime, typing).
