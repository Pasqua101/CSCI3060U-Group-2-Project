"""
CLASS: Account and AccountManager
INTENTION: Manages the internal representation of bank account data and 
           handles the parsing of the Current Bank Accounts File.
"""

class Account:
    """
    Represents a bank account with status and balance.
    INTENTION: To encapsulate all data associated with a single bank account 
               entity, including its number, holder name, status, and balance.
    INTERFACE: Stores state variables provided during instantiation.
    """
    def __init__(self, number, holder, status, balance):
        self.number = number   # NNNNN 
        self.holder = holder   # AAAAAAAAAAAAAAAAAAAA 
        self.status = status   # A or D 
        self.balance = balance # PPPPPPPP 

class AccountManager:
    """
    Loads and retrieves accounts from the current bank accounts file.
    INTENTION: To provide a centralized data access layer that reads the 
               master account list into memory for validation and processing.
    INTERFACE: Offers methods to parse the accounts file and store it in a dictionary.
    """
    def __init__(self):
        """Initializes an empty dictionary to hold Account objects."""
        self.accounts_by_number = {}

    def load_current_accounts(self, path):
        """
        Parses the fixed-length 37-character file.
        INTENTION: To read the input accounts file line-by-line and populate 
                   the internal account dictionary using fixed-width slicing.
        INTERFACE: Takes a string 'path' to the accounts file.
        """
        with open(path, 'r') as f:
            for line in f:
                if "END_OF_FILE" in line: break 
                num = line[0:5]
                name = line[6:26].strip()
                status = line[27]
                bal = float(line[29:37])
                self.accounts_by_number[num] = Account(num, name, status, bal)