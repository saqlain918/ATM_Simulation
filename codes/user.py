import csv
import hashlib
import os
from typing import List, Dict, Optional, Tuple, Callable

CONFIG = {
    "USERS_CSV": "/home/lenovo/PycharmProjects/PythonProject1/CSV_files/users.csv",
    "TRANSACTIONS_CSV": "/home/lenovo/PycharmProjects/PythonProject1/CSV_files/transactions.csv"
}

class CSVUtils:
    @staticmethod
    def validate_csv_headers(file_path: str, required_fields: List[str]) -> bool:
        try:
            with open(file_path, "r", newline="") as f:
                reader = csv.DictReader(f)
                return all(field in reader.fieldnames for field in required_fields)
        except (PermissionError, OSError, csv.Error):
            return False

    @staticmethod
    def initialize_csv(file_path: str, fieldnames: List[str], initial_data: Optional[List[Dict]] = None) -> bool:
        try:
            if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
                if CSVUtils.validate_csv_headers(file_path, fieldnames):
                    print(f"✅ {file_path} already exists and is valid.")
                    return True
            with open(file_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                if initial_data:
                    writer.writerows(initial_data)
            print(f"✅ Initialized {file_path}{' with ' + str(len(initial_data)) + ' rows' if initial_data else ''}")
            return True
        except PermissionError:
            print(f"❌ No permission to create/write {file_path}. Check directory permissions.")
            return False
        except OSError as e:
            print(f"❌ Error initializing {file_path}: {e}")
            return False
        except csv.Error as e:
            print(f"❌ CSV error in {file_path}: {e}")
            return False

    @staticmethod
    def safe_csv_operation(file_path: str, operation: Callable, *args, **kwargs) -> Tuple[bool, str | Dict]:
        try:
            result = operation(*args, **kwargs)
            if isinstance(result, tuple):
                return result
            return True, result
        except (PermissionError, OSError, csv.Error) as e:
            return False, f"❌ Error in {file_path}: {e}"
        except ValueError as e:
            return False, f"❌ Invalid data in {file_path}: {e}"
        except Exception as e:
            return False, f"❌ Unexpected error in {file_path}: {e}"

class User:
    USERS_CSV = CONFIG["USERS_CSV"]
    USER_FIELDS = ["name", "account_number", "pin", "address", "balance", "is_deleted"]
    CSVUtils = CSVUtils  # Explicitly bind CSVUtils to User class

    def __init__(self):
        self._init_users_csv()

    def _hash_pin(self, pin: str) -> Optional[str]:
        try:
            return hashlib.sha256(pin.encode()).hexdigest()
        except ValueError as e:
            print(f"❌ Error hashing PIN: {e}")
            return None

    def _is_valid_pin(self, pin: str) -> bool:
        return bool(pin.isdigit() and len(pin) == 4)

    def _is_pin_unique(self, account_number: str, new_pin: str) -> bool:
        hashed_new_pin = self._hash_pin(new_pin)
        if not hashed_new_pin:
            return False
        def operation():
            with open(self.USERS_CSV, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if (row["account_number"] != str(account_number) and
                        row["pin"] == hashed_new_pin and
                        row.get("is_deleted", "0") == "0"):
                        return False
            return True
        success, result = self.CSVUtils.safe_csv_operation(self.USERS_CSV, operation)
        if not success:
            print(result)
            return False
        return bool(result)

    def _init_users_csv(self) -> None:
        initial_data = [
            {
                "name": "Saqlain Rai",
                "account_number": "987654321",
                "pin": self._hash_pin("1234"),
                "address": "123 Main St, Karachi",
                "balance": "0.0",
                "is_deleted": "0"
            },
            {
                "name": "Ahmed",
                "account_number": "123456789",
                "pin": self._hash_pin("5678"),
                "address": "456 Gulshan Ave, Lahore",
                "balance": "0.0",
                "is_deleted": "0"
            }
        ]
        if not self.CSVUtils.initialize_csv(self.USERS_CSV, self.USER_FIELDS, initial_data):
            exit(1)

    def find_user(self, account_number: str, include_deleted: bool = False) -> Optional[Dict]:
        def operation():
            with open(self.USERS_CSV, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["account_number"] == account_number:
                        try:
                            row["balance"] = str(float(row.get("balance", "0.0")))
                        except ValueError:
                            row["balance"] = "0.0"
                        row["is_deleted"] = row.get("is_deleted", "0")
                        if include_deleted or row["is_deleted"] == "0":
                            return True, row
                return False, "User not found"
        success, result = self.CSVUtils.safe_csv_operation(self.USERS_CSV, operation)
        if not success:
            if isinstance(result, str) and "not found" in result.lower():
                print(f"❌ {self.USERS_CSV} not found. Reinitializing...")
                self._init_users_csv()
                return self.find_user(account_number, include_deleted)
            print(result)
            return None
        if isinstance(result, dict):
            return result
        return None

    def update_balance(self, account_number: str, new_balance: float) -> Tuple[bool, str]:
        def operation():
            user = self.find_user(account_number, include_deleted=True)
            if not user:
                return False, "❌ User not found."
            if user["is_deleted"] == "1":
                return False, "❌ Cannot update balance for deleted user."
            users = []
            with open(self.USERS_CSV, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["account_number"] == account_number:
                        row["balance"] = str(new_balance)
                    else:
                        try:
                            row["balance"] = str(float(row.get("balance", "0.0")))
                        except ValueError:
                            row["balance"] = "0.0"
                    row["is_deleted"] = row.get("is_deleted", "0")
                    users.append(row)
            with open(self.USERS_CSV, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.USER_FIELDS)
                writer.writeheader()
                writer.writerows(users)
            return True, "✅ Balance updated."
        return self.CSVUtils.safe_csv_operation(self.USERS_CSV, operation)

    def change_pin(self, user: Dict, new_pin: str, confirm_pin: str, verify_current_pin: bool = True,
                   current_pin: Optional[str] = None) -> Tuple[bool, str]:
        def operation():
            if user["is_deleted"] == "1":
                return False, "❌ Cannot change PIN for deleted user."
            if verify_current_pin:
                if not self._is_valid_pin(current_pin):
                    return False, "❌ PIN must be 4 digits."
                if self._hash_pin(current_pin) != user["pin"]:
                    return False, "❌ Incorrect PIN."
            if not self._is_valid_pin(new_pin):
                return False, "❌ PIN must be 4 digits."
            if new_pin != confirm_pin:
                return False, "❌ PINs do not match."
            if not self._is_pin_unique(user["account_number"], new_pin):
                return False, "❌ PIN already in use. Choose a different PIN."
            hashed_new_pin = self._hash_pin(new_pin)
            if not hashed_new_pin:
                return False, "❌ Failed to hash PIN."
            users = []
            with open(self.USERS_CSV, "r", newline="") as f:
                reader = csv.DictReader(f)
                users.extend(reader)
            for row in users:
                if row["account_number"] == user["account_number"]:
                    row["pin"] = hashed_new_pin
                    try:
                        row["balance"] = str(float(row.get("balance", "0.0")))
                    except ValueError:
                        row["balance"] = "0.0"
                row["is_deleted"] = row.get("is_deleted", "0")
            with open(self.USERS_CSV, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.USER_FIELDS)
                writer.writeheader()
                writer.writerows(users)
            return True, "✅ PIN changed successfully."
        return self.CSVUtils.safe_csv_operation(self.USERS_CSV, operation)

    def soft_delete_user(self, account_number: str) -> Tuple[bool, str]:
        def operation():
            user = self.find_user(account_number, include_deleted=True)
            if not user:
                return False, "❌ User not found."
            if user["is_deleted"] == "1":
                return False, "❌ User is already deleted."
            users = []
            with open(self.USERS_CSV, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["account_number"] == account_number:
                        row["is_deleted"] = "1"
                    else:
                        row["is_deleted"] = row.get("is_deleted", "0")
                    try:
                        row["balance"] = str(float(row.get("balance", "0.0")))
                    except ValueError:
                        row["balance"] = "0.0"
                    users.append(row)
            with open(self.USERS_CSV, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.USER_FIELDS)
                writer.writeheader()
                writer.writerows(users)
            return True, "✅ Account deleted successfully."
        return self.CSVUtils.safe_csv_operation(self.USERS_CSV, operation)