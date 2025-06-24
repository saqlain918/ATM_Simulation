import csv
import os
import re
from datetime import datetime
from typing import Dict, Optional
from codes.user import User, CONFIG

class ATM:


    TRANSACTIONS_CSV = CONFIG["TRANSACTIONS_CSV"]
    TRANSACTION_FIELDS = ["account_number", "type", "amount", "target_account", "status", "timestamp"]

    def __init__(self):
        self.user_manager = User()
        self._init_transactions_csv()

    def _get_transaction_file_path(self) -> str:
        return self.TRANSACTIONS_CSV

    def _init_transactions_csv(self) -> None:
        if not User.CSVUtils.initialize_csv(self.TRANSACTIONS_CSV, self.TRANSACTION_FIELDS):
            exit(1)

    def _log_transaction(self, account_number: str, trans_type: str, amount: float,
                        target_account: str = "", status: str = "") -> None:
        def operation():
            transaction_file = self._get_transaction_file_path()
            if not os.path.isfile(transaction_file) or os.path.getsize(transaction_file) == 0:
                User.CSVUtils.initialize_csv(transaction_file, self.TRANSACTION_FIELDS)
            with open(transaction_file, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.TRANSACTION_FIELDS)
                writer.writerow({
                    "account_number": account_number,
                    "type": trans_type,
                    "amount": amount,
                    "target_account": target_account,
                    "status": status,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            return True, "✅ Transaction logged"
        success, message = User.CSVUtils.safe_csv_operation(self.TRANSACTIONS_CSV, operation)
        if not success:
            print(message)

    def _prompt_account_number(self) -> str:
        return input("Enter account number: ").strip()

    def _prompt_pin(self) -> str:
        return input("Enter 4-digit PIN: ").strip()

    def _handle_failed_attempts(self, user: Dict) -> Optional[Dict]:
        print("❌ Too many attempts.")
        reset_choice = input("Would you like to reset your PIN? (yes/no): ").strip().lower()
        if reset_choice == "yes":
            success = False
            while not success:
                new_pin = input("Enter new 4-digit PIN (or press Enter to cancel): ").strip()
                if not new_pin:
                    print("❌ PIN change cancelled.")
                    print("👋 Thank you for using ATM!")
                    exit(0)
                confirm_pin = input("Confirm new PIN: ").strip()
                success, message = self.user_manager.change_pin(user, new_pin, confirm_pin, verify_current_pin=False)
                print(message)
            print("🔄 Please try logging in again.")
            return self.login()
        print("👋 Thank you for using ATM!")
        exit(0)

    def login(self) -> Optional[Dict]:
        try:
            print("\n--- Login ---")
            account_number = self._prompt_account_number()
            user = self.user_manager.find_user(account_number)
            if not user:
                print("❌ Account not found.")
                return None
            if user["is_deleted"] == "1":
                print("❌ Account is deleted.")
                return None
            for attempt in range(3):
                pin = self._prompt_pin()
                if not self.user_manager._is_valid_pin(pin):
                    print("❌ PIN must be 4 digits.")
                    continue
                if self.user_manager._hash_pin(pin) == user["pin"]:
                    print("✅ Login successful!")
                    return user
                print(f"❌ Incorrect PIN. {2 - attempt} attempts left.")
            return self._handle_failed_attempts(user)
        except KeyboardInterrupt:
            print("\n❌ Login cancelled.")
            print("👋 Thank you for using ATM!")
            exit(0)
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return None

    def check_balance(self, user: Dict) -> None:
        try:
            if user["is_deleted"] == "1":
                print("❌ Cannot check balance for deleted user.")
                return
            balance = float(user.get("balance", "0.0"))
            print(f"💰 Current balance: {balance:.2f}")
        except ValueError:
            print("❌ Invalid balance data. Setting to 0.00.")
            balance = 0.0
            self.user_manager.update_balance(user["account_number"], balance)
            print(f"💰 Current balance: {balance:.2f}")

    def deposit_funds(self, user: Dict) -> None:
        while True:
            try:
                if user["is_deleted"] == "1":
                    print("❌ Cannot deposit to deleted user.")
                    return
                amount = input("Enter amount to deposit (or press Enter to cancel): ").strip()
                if not amount:
                    print("❌ Deposit cancelled.")
                    return
                if not re.match(r"^\d+(\.\d{1,2})?$", amount):
                    print("❌ Invalid amount format. Use numbers (e.g., 10 or 10.50).")
                    continue
                amount = float(amount)
                if amount <= 0:
                    print("❌ Amount must be positive.")
                    continue
                if amount > 10000:
                    print("❌ Deposit amount exceeds limit (10000.00).")
                    continue
                current_balance = float(user.get("balance", "0.0"))
                new_balance = current_balance + amount
                success, message = self.user_manager.update_balance(user["account_number"], new_balance)
                if not success:
                    print(message)
                    return
                self._log_transaction(user["account_number"], "Deposit", amount,
                                     target_account=user["account_number"], status="Credit")
                print(f"✅ Deposited {amount:.2f}")
                break
            except ValueError:
                print("❌ Invalid amount. Use numbers only.")
                continue
            except Exception as e:
                print(f"❌ Deposit failed: {e}")
                continue

    def withdraw_funds(self, user: Dict) -> None:
        while True:
            try:
                if user["is_deleted"] == "1":
                    print("❌ Cannot withdraw from deleted user.")
                    return
                amount = input("Enter amount to withdraw (or press Enter to cancel): ").strip()
                if not amount:
                    print("❌ Withdrawal cancelled.")
                    return
                if not re.match(r"^\d+(\.\d{1,2})?$", amount):
                    print("❌ Invalid amount format. Use numbers (e.g., 10 or 10.50).")
                    continue
                amount = float(amount)
                if amount <= 0:
                    print("❌ Amount must be positive.")
                    continue
                if amount > 10000:
                    print("❌ Withdrawal amount exceeds limit (10000.00).")
                    continue
                current_balance = float(user.get("balance", "0.0"))
                if amount > current_balance:
                    print("❌ Insufficient balance.")
                    continue
                new_balance = current_balance - amount
                success, message = self.user_manager.update_balance(user["account_number"], new_balance)
                if not success:
                    print(message)
                    return
                self._log_transaction(user["account_number"], "Withdrawal", amount,
                                     target_account=user["account_number"], status="Debit")
                print(f"✅ Withdrawn {amount:.2f}")
                break
            except ValueError:
                print("❌ Invalid amount. Use numbers only.")
                continue
            except Exception as e:
                print(f"❌ Withdrawal failed: {e}")
                continue

    def transfer_funds(self, user: Dict) -> None:
        while True:
            try:
                if user["is_deleted"] == "1":
                    print("❌ Cannot transfer from deleted user.")
                    return
                target_account = input("Enter target account number (or press Enter to cancel): ").strip()
                if not target_account:
                    print("❌ Transfer cancelled.")
                    return
                if target_account == user["account_number"]:
                    print("❌ Cannot transfer to your own account.")
                    continue
                target_user = self.user_manager.find_user(target_account)
                if not target_user:
                    print("❌ Target account not found.")
                    continue
                if target_user["is_deleted"] == "1":
                    print("❌ Cannot transfer to deleted user.")
                    continue
                amount = input("Enter amount to transfer (or press Enter to cancel): ").strip()
                if not amount:
                    print("❌ Transfer cancelled.")
                    return
                if not re.match(r"^\d+(\.\d{1,2})?$", amount):
                    print("❌ Invalid amount format. Use numbers (e.g., 10 or 10.50).")
                    continue
                amount = float(amount)
                if amount <= 0:
                    print("❌ Amount must be positive.")
                    continue
                if amount > 10000:
                    print("❌ Transfer amount exceeds limit (10000.00).")
                    continue
                current_balance = float(user.get("balance", "0.0"))
                if amount > current_balance:
                    print("❌ Insufficient balance.")
                    continue
                success, message = self.user_manager.update_balance(user["account_number"], current_balance - amount)
                if not success:
                    print(message)
                    return
                target_balance = float(target_user.get("balance", "0.0"))
                success, message = self.user_manager.update_balance(target_account, target_balance + amount)
                if not success:
                    print(message)
                    return
                self._log_transaction(user["account_number"], "Transfer", amount, target_account, "Debit")
                self._log_transaction(target_account, "Transfer", amount, user["account_number"], "Credit")
                print(f"✅ Transferred {amount:.2f} to account {target_account}")
                break
            except ValueError:
                print("❌ Invalid amount. Use numbers only.")
                continue
            except Exception as e:
                print(f"❌ Transfer failed: {e}")
                continue

    def change_pin(self, user: Dict) -> None:
        for attempt in range(3):
            current_pin = input("Enter current 4-digit PIN (or press Enter to cancel): ").strip()
            if not current_pin:
                print("❌ PIN change cancelled.")
                return
            new_pin = input("Enter new 4-digit PIN: ").strip()
            confirm_pin = input("Confirm new PIN: ").strip()
            success, message = self.user_manager.change_pin(user, new_pin, confirm_pin,
                                                          verify_current_pin=True, current_pin=current_pin)
            print(message)
            if success:
                return
            if "Incorrect PIN" in message:
                print(f"{2 - attempt} attempts left.")
            else:
                return
        print("❌ Too many attempts.")

    def soft_delete_account(self, user: Dict) -> None:
        try:
            confirm = input("Are you sure you want to delete your account? (yes/no): ").strip().lower()
            if confirm != "yes":
                print("❌ Account deletion cancelled.")
                return
            success, message = self.user_manager.soft_delete_user(user["account_number"])
            print(message)
            if success:
                print("👋 Thank you for using ATM!")
                exit(0)
        except Exception as e:
            print(f"❌ Account deletion failed: {e}")

    def view_transactions(self, user: Dict) -> None:
        transaction_file = self._get_transaction_file_path()
        def operation():
            print("\n--- Transaction History ---")
            found = False
            with open(transaction_file, "r", newline="") as f:
                reader = csv.DictReader(f)
                if not all(field in reader.fieldnames for field in self.TRANSACTION_FIELDS):
                    return False, f"❌ Invalid transaction file structure. Please reinitialize {transaction_file}"
                for row in reader:
                    if not all(field in row for field in self.TRANSACTION_FIELDS):
                        print(f"⚠️ Skipping malformed transaction row: missing fields {set(self.TRANSACTION_FIELDS) - set(row.keys())}")
                        continue
                    if row["account_number"] == user["account_number"]:
                        target = row.get("target_account", "") or "-"
                        try:
                            amount = float(row["amount"])
                            print(f"{row['timestamp']} | {row['type']} | {amount:.2f} | {target} | {row['status']}")
                            found = True
                        except ValueError as e:
                            print(f"⚠️ Skipping invalid transaction: invalid amount '{row['amount']}' ({e})")
                            continue
                        except Exception as e:
                            print(f"⚠️ Skipping invalid transaction: {e}")
                            continue
            if not found:
                print("📜 No transactions found.")
            return True, "✅ Transaction history displayed"
        success, message = User.CSVUtils.safe_csv_operation(transaction_file, operation)
        if not success and "not found" not in message.lower():
            print(message)
        elif not success:
            print("📜 No transactions found.")

    def _display_menu(self) -> None:
        print("\n--- ATM Menu ---")
        print("1. Check Balance")
        print("2. Deposit Funds")
        print("3. Withdraw Funds")
        print("4. Transfer Funds")
        print("5. Change PIN")
        print("6. View Transactions")
        print("7. Delete Account")
        print("8. Exit")

    def _handle_menu_choice(self, user: Dict, choice: str) -> Optional[Dict]:
        if choice == "1":
            self.check_balance(user)
        elif choice == "2":
            self.deposit_funds(user)
            return self.user_manager.find_user(user["account_number"])
        elif choice == "3":
            self.withdraw_funds(user)
            return self.user_manager.find_user(user["account_number"])
        elif choice == "4":
            self.transfer_funds(user)
            return self.user_manager.find_user(user["account_number"])
        elif choice == "5":
            self.change_pin(user)
            return self.user_manager.find_user(user["account_number"])
        elif choice == "6":
            self.view_transactions(user)
        elif choice == "7":
            self.soft_delete_account(user)
            return None
        elif choice == "8":
            print("👋 Thank you for using ATM!")
            return None
        else:
            print("❌ Invalid option.")
        return user

    def main_menu(self, user: Dict) -> None:
        while True:
            try:
                self._display_menu()
                choice = input("Choose (1-8): ").strip()
                user = self._handle_menu_choice(user, choice)
                if user is None:
                    break
            except KeyboardInterrupt:
                print("\n❌ Operation cancelled.")
                break
            except Exception as e:
                print(f"❌ Menu error: {e}")

    def start(self) -> None:
        while True:
            user = self.login()
            if user:
                self.main_menu(user)
                break

if __name__ == "__main__":
    atm = ATM()
    atm.start()