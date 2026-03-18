"""
CLASS: Transaction and TransactionManager
INTENTION: Handles the creation, storage, and file-writing of 40-character 
           banking transaction records.
"""

class Transaction:
    """
    Represents a single banking transaction record.
    INTENTION: To encapsulate the data required for a single transaction entry.
    INTERFACE: Takes transaction code, user name, account number, amount, and optional misc info.
    """
    def __init__(self, code, name, account_no, amount, misc="00"):
        self.code = code
        self.name = name
        self.account_no = account_no
        self.amount = amount
        self.misc = misc

class TransactionManager:
    """
    Maintains a list of transactions and writes them to file at logout.
    INTENTION: To collect all session transactions and batch-write them to the 
               Daily Transaction File upon session termination.
    INTERFACE: Provides methods to add transactions and export them to a text file.
    """
    def __init__(self):
        self.transactions = []

    def add(self, tx):
        """
        Adds a transaction object to the current list.
        INTENTION: To store a new transaction record in the session history.
        """
        self.transactions.append(tx)

    def write_daily_transactions(self, path):
        """
        Writes all formatted lines to the daily transaction file.
        INTENTION: To iterate through stored transactions and write them as 
                   fixed-length 40-character strings to the specified output path.
        """
        with open(path, 'a') as f:
            for tx in self.transactions:
                # CC AAAAAAAAAAAAAAAAAAAA NNNNN PPPPPPPP MM
                line = f"{tx.code} {tx.name:<20} {tx.account_no:>05} {tx.amount:>08.2f} {tx.misc}"
                # Explicitly slice to 40 chars to ensure strict adherence to requirements
                f.write(line[:40] + "\n")
    
    def add_end_of_session(self):
        """
        Adds the final 00 transaction record.
        INTENTION: To create and append the mandatory 'End of Session' (00) 
                   transaction required at logout.
        """
        self.add(Transaction("00", " ", "00000", 0.0))