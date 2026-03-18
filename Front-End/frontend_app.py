"""
CLASS: FrontEndApp
INTENTION: Coordinates the interaction between the user session, account data, 
           and transaction logging.
"""

from session import Session
from accounts import AccountManager
from transactions import TransactionManager, Transaction
from validators import Validators

class FrontEndApp:
    """
    Coordinates interaction between session, accounts, and transactions.
    INTENTION: To serve as the controller that orchestrates the banking 
               system's operations and command dispatching.
    INTERFACE: Requires file paths and an input source to initialize and run the main loop.
    """
    def __init__(self, accounts_path, trans_path, input_source):
        """Initializes the app with required file paths and input source."""
        self.session = Session()
        self.account_manager = AccountManager()
        self.tx_manager = TransactionManager()
        self.accounts_path = accounts_path
        self.trans_path = trans_path
        self.input_source = input_source

    def run(self):
        """
        Primary loop for reading commands from the input stream.
        INTENTION: To continuously listen for and process user commands until 
                   the input stream is exhausted.
        """
        print("Welcome to the Banking System.")
        while True:
            line = self.input_source.readline()
            if not line: break
            
            cmd = line.strip().lower()
            if not cmd: continue
            self.dispatch(cmd)

    def dispatch(self, cmd):
        """
        Directs the command to the appropriate transaction handler.
        INTENTION: To act as a routing mechanism that calls specific 
                   transaction methods based on the input command.
        INTERFACE: Takes a string 'cmd' representing the transaction type.
        """
        actions = {
            "login": self.login_transaction,
            "logout": self.logout_transaction,
            "withdrawal": self.withdrawal_transaction,
            "transfer": self.transfer_transaction,
            "paybill": self.paybill_transaction,
            "deposit": self.deposit_transaction,
            "create": self.create_transaction,
            "delete": self.delete_transaction,
            "disable": self.disable_transaction,
            "changeplan": self.changeplan_transaction
        }
        
        if cmd in actions:
            actions[cmd]()
        else:
            print(f"Invalid transaction code: {cmd}")

    def _check_login(self, admin_required=False):
        """
        Validates session state and privilege requirements.
        INTENTION: To enforce security constraints that prevent unauthorized 
                   transactions before login or by non-admin users.
        INTERFACE: Returns a boolean indicating if the check passed.
        """
        if not self.session.is_logged_in:
            print("Error: No transaction other than login should be accepted before a login")
            return False
        if admin_required and self.session.mode != "admin":
            print("Error: Privileged transaction - only accepted when logged in admin mode")
            return False
        return True

    def login_transaction(self):
        """
        Starts a session and loads the current accounts file.
        INTENTION: To handle the login sequence and initialize the master account list.
        """
        if self.session.is_logged_in:
            print("Error: Already logged in.")
            return

        mode = self.input_source.readline().strip().lower() 
        if not Validators.validate_mode(mode):
            print(f"Error: Invalid login mode '{mode}'. Only 'standard' or 'admin' accepted.")
            return

        name = self.input_source.readline().strip()

        # Handle name validation based on mode
        if mode == "standard":
            if not Validators.validate_name(name):
                print("Error: Invalid username. Must be 1-20 characters and not empty.")
                return
            user = name
        else:
            user = name if name else "Admin"
        
        # Use the updated session login to store the user
        self.session.login(mode, user)
        self.account_manager.load_current_accounts(self.accounts_path)
        print(f"Accepted {mode} login.")

    def withdrawal_transaction(self):
        """
        Processes a withdrawal within standard or admin constraints.
        INTENTION: To collect withdrawal data and record it as a valid 
                   session transaction for later processing.
        """

        if not self.session.is_logged_in:
            print("Error: withdrawal only accepted when logged in.")
            return

        account_num = self.input_source.readline().strip()
        amount_str = self.input_source.readline().strip()


        if account_num not in self.account_manager.accounts_by_number:
            print(f"Error: Account number {account_num} not found.")
            return

        try:
            amount = float(amount_str)

            if not Validators.validate_amount(amount):
                print("Error: Invalid withdrawal amount.")
                return

            if self.session.mode == "standard" and amount > 500.00:
                print("Error: Standard users cannot withdraw more than $500.00.")
                return

            account = self.account_manager.accounts_by_number[account_num]
            if amount > account.balance:
                print("Error: Insufficient funds.")
                return

            self.tx_manager.add(Transaction("01", account.holder, account_num, amount))
            print("Withdrawal successful.")

        except ValueError:
            print("Error: Amount must be numeric.")

    def create_transaction(self):
        """
        Privileged: Creates a new bank account.
        INTENTION: To record an account creation request in the transaction file.
        """

        if not self._check_login(admin_required=True):
            self.input_source.readline() 
            self.input_source.readline() 
            return

        name = self.input_source.readline().strip()
        balance_str = self.input_source.readline().strip()
        

        if not Validators.validate_name(name):
            print("Error: Invalid name length (Must be 1-20 characters).")
            return


        existing_names = [acc.holder for acc in self.account_manager.accounts_by_number.values()]
        if name in existing_names:
            print(f"Error: Account name '{name}' already exists.")
            return

        try:
            balance = float(balance_str)

            if not Validators.validate_amount(balance):
                print("Error: Invalid initial balance.")
                return
        except ValueError:
            print("Error: Balance must be a numeric value.")
            return

        self.tx_manager.add(Transaction("05", name, "00000", balance))
        print("Account creation recorded.")

    def logout_transaction(self):
        """
        Ends a Front End session and writes out the transaction file.
        INTENTION: To finalize the transaction list and write it to disk 
                   before resetting the system state.
        """
        if not self.session.is_logged_in:
            print("Error: should only be accepted when logged in ")
            return
            
        self.tx_manager.add_end_of_session()
        self.tx_manager.write_daily_transactions(self.trans_path)
        self.session.logout()
        print("Session terminated.")

    def transfer_transaction(self):
        """
        Processes funds transfer between accounts.
        INTENTION: To record a transfer of funds from a source account to a 
                   destination account, capturing both account numbers and the amount.
        INTERFACE: Reads source account, destination account, and amount from input.
        """

        if not self.session.is_logged_in:
            print("Error: transfer only accepted when logged in.")
            return

        from_account_num = self.input_source.readline().strip()
        to_account_num = self.input_source.readline().strip()
        amount_str = self.input_source.readline().strip()

        accounts = self.account_manager.accounts_by_number
        if from_account_num not in accounts or to_account_num not in accounts:
            print("Error: One or both account numbers are invalid.")
            return

        from_acc = accounts[from_account_num]
        to_acc = accounts[to_account_num]

        if from_acc.status != 'A' or to_acc.status != 'A':
            print("Error: Cannot transfer to or from a disabled/deleted account.")
            return

        try:
            amount = float(amount_str)
            if not Validators.validate_amount(amount):
                print("Error: Invalid transfer amount.")
                return

            if self.session.mode == "standard" and amount > 1000.00:
                print("Error: Standard users cannot transfer more than $1000.00.")
                return

            if amount > from_acc.balance:
                print(f"Error: Insufficient funds in account {from_account_num}.")
                return

            self.tx_manager.add(Transaction("02", from_acc.holder, from_account_num, amount))
            # Note: Some specs require a second record for the 'to' account
            self.tx_manager.add(Transaction("02", to_acc.holder, to_account_num, amount))
            
            print("Transfer successfully recorded.")

        except ValueError:
            print("Error: Amount must be numeric.")

    def paybill_transaction(self):
        """
        Processes bill payment to a specific company.
        INTENTION: To record a payment from a user's account to a recognized 
                   utility or service provider.
        INTERFACE: Reads account number, company name, and amount from input.
        """
        if not self.session.is_logged_in:
            print("Error: paybill only accepted when logged in.")
            return

        account_num = self.input_source.readline().strip()
        company_code = self.input_source.readline().strip().upper()
        amount_str = self.input_source.readline().strip()

        valid_companies = ["EC", "CQ", "TV"]
        if company_code not in valid_companies:
            print(f"Error: Invalid company code '{company_code}'. Must be EC, CQ, or TV.")
            return
        
        account_num = account_num.zfill(5)

        if account_num not in self.account_manager.accounts_by_number:
            print(f"Error: Account number {account_num} not found.")
            return

        acc = self.account_manager.accounts_by_number[account_num]

        if self.session.mode == "standard" and acc.holder != self.session.user:
            print(f"Error: You are not authorized to pay bills from account {account_num}.")
            return

        try:
            amount = float(amount_str)
            if not Validators.validate_amount(amount):
                print("Error: Invalid payment amount.")
                return

            if self.session.mode == "standard" and amount > 1000.00:
                print("Error: Standard users cannot pay a bill over $1000.00.")
                return

            if amount > acc.balance:
                print(f"Error: Insufficient funds in account {account_num}.")
                return

            self.tx_manager.add(Transaction("03", acc.holder, account_num, amount))
            print(f"Bill payment to {company_code} successfully recorded.")

        except ValueError:
            print("Error: Amount must be numeric.")

    def deposit_transaction(self):
        """
        Processes account deposits.
        INTENTION: To record the addition of funds into a specified bank account.
        INTERFACE: Reads account number and deposit amount from input.
        """
        if not self.session.is_logged_in:
            print("Error: deposit only accepted when logged in.")
            return

        account_num = self.input_source.readline().strip()
        amount_str = self.input_source.readline().strip()

        account_num = account_num.zfill(5)

        if account_num not in self.account_manager.accounts_by_number:
            print(f"Error: Account number {account_num} not found.")
            return

        acc = self.account_manager.accounts_by_number[account_num]

        if acc.status != 'A':
            print("Error: Cannot deposit into a disabled account.")
            return

        if self.session.mode == "standard" and acc.holder != self.session.user:
            print(f"Error: Standard users can only deposit into their own account.")
            return

        try:
            amount = float(amount_str)
            if not Validators.validate_amount(amount):
                print("Error: Invalid deposit amount.")
                return

            if self.session.mode == "standard" and amount > 1000.00:
                print("Error: Standard users cannot deposit more than $1000.00.")
                return

            self.tx_manager.add(Transaction("04", acc.holder, account_num, amount))
            print("Deposit successfully recorded.")

        except ValueError:
            print("Error: Amount must be numeric.")

    def delete_transaction(self):
        """
        Privileged: Marks an account for deletion.
        INTENTION: To record a request for the permanent removal of a bank 
                   account from the system (Admin only).
        INTERFACE: Reads account holder name and account number from input.
        """

        if not self._check_login(admin_required=True):
            self.input_source.readline()
            self.input_source.readline()
            return

        name = self.input_source.readline().strip()
        acc_num = self.input_source.readline().strip()

        if acc_num not in self.account_manager.accounts_by_number:
            print(f"Error: Account number {acc_num} not found.")
            return

        acc = self.account_manager.accounts_by_number[acc_num]

        if acc.holder != name:
            print(f"Error: Name '{name}' does not match account {acc_num}.")
            return

        if acc.status != 'A':
            print("Error: Account is already disabled or deleted.")
            return

        self.tx_manager.add(Transaction("06", name, acc_num, 0.0))
        print("Account deletion recorded.")

    def disable_transaction(self):
        """
        Privileged: Disables an active account.
        INTENTION: To record a status change that prevents an account from 
                   performing further transactions (Admin only).
        INTERFACE: Reads account holder name and account number from input.
        """

        if not self._check_login(admin_required=True):
            self.input_source.readline()
            self.input_source.readline()
            return

        name = self.input_source.readline().strip()
        acc_num = self.input_source.readline().strip()


        if acc_num not in self.account_manager.accounts_by_number:
            print(f"Error: Account number {acc_num} not found.")
            return

        acc = self.account_manager.accounts_by_number[acc_num]

        if acc.holder != name:
            print(f"Error: Name '{name}' does not match holder of account {acc_num}.")
            return

        if acc.status != 'A':
            print("Error: Account is already disabled or deleted.")
            return

        self.tx_manager.add(Transaction("07", name, acc_num, 0.0))
        print("Account disabled.")

    def changeplan_transaction(self):
        """
        Privileged: Changes the account payment plan.
        INTENTION: To switch an account between 'Student' and 'Non-Student' 
                   fee structures (Admin only).
        INTERFACE: Reads account holder name and account number from input.
        """
        if not self._check_login(admin_required=True):
            self.input_source.readline()
            self.input_source.readline()
            return
        name = self.input_source.readline().strip()
        acc_num = self.input_source.readline().strip()
        self.tx_manager.add(Transaction("08", name, acc_num, 0.0))
        print("Account plan change recorded.")
    
    def changeplan_transaction(self):
        """
        Privileged: Changes the account payment plan.
        INTENTION: Validates admin status, account existence, and status.
        """

        if not self._check_login(admin_required=True):
            self.input_source.readline()
            self.input_source.readline()
            return

        name = self.input_source.readline().strip()
        acc_num = self.input_source.readline().strip()

        if acc_num not in self.account_manager.accounts_by_number:
            print(f"Error: Account {acc_num} not found.")
            return

        acc = self.account_manager.accounts_by_number[acc_num]

        if acc.holder != name:
            print(f"Error: Name '{name}' does not match holder of account {acc_num}.")
            return

        if acc.status != 'A':
            print("Error: Cannot change plan on a disabled or deleted account.")
            return

        self.tx_manager.add(Transaction("08", name, acc_num, 0.0))
        print("Account plan change recorded.")