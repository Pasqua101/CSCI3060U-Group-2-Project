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
        user = self.input_source.readline().strip() if mode == "standard" else "Admin"
        
        self.session.login(mode, user)
        self.account_manager.load_current_accounts(self.accounts_path)
        print(f"Accepted {mode} login.")

    def withdrawal_transaction(self):
        """
        Processes a withdrawal within standard or admin constraints.
        INTENTION: To collect withdrawal data and record it as a valid 
                   session transaction for later processing.
        """
        if not self._check_login():
            self.input_source.readline() 
            self.input_source.readline() 
            return

        acc_num = self.input_source.readline().strip()
        amount = float(self.input_source.readline().strip())
        
        self.tx_manager.add(Transaction("01", self.session.current_user, acc_num, amount))
        print("Withdrawal processed.")

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
        balance = float(self.input_source.readline().strip())
        
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
        if not self._check_login():
            for _ in range(3): self.input_source.readline()
            return
        from_acc = self.input_source.readline().strip()
        to_acc = self.input_source.readline().strip()
        amount = float(self.input_source.readline().strip())
        self.tx_manager.add(Transaction("02", self.session.current_user, from_acc, amount, to_acc[:2]))
        print("Transfer processed.")

    def paybill_transaction(self):
        """
        Processes bill payment to a specific company.
        INTENTION: To record a payment from a user's account to a recognized 
                   utility or service provider.
        INTERFACE: Reads account number, company name, and amount from input.
        """
        if not self._check_login():
            for _ in range(3): self.input_source.readline()
            return
        acc_num = self.input_source.readline().strip()
        company = self.input_source.readline().strip()
        amount = float(self.input_source.readline().strip())
        self.tx_manager.add(Transaction("03", self.session.current_user, acc_num, amount, company[:2]))
        print("Bill payment processed.")

    def deposit_transaction(self):
        """
        Processes account deposits.
        INTENTION: To record the addition of funds into a specified bank account.
        INTERFACE: Reads account number and deposit amount from input.
        """
        if not self._check_login():
            self.input_source.readline()
            self.input_source.readline()
            return
        acc_num = self.input_source.readline().strip()
        amount = float(self.input_source.readline().strip())
        self.tx_manager.add(Transaction("04", self.session.current_user, acc_num, amount))
        print("Deposit processed.")

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