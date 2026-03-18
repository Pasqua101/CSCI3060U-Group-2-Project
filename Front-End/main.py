"""
PROGRAM: Banking System Front End
INTENTION: Acts as the primary ATM terminal interface for processing banking 
           transactions (Phase 2 Prototype).
INPUTS: 
    Current Bank Accounts File (fixed-length text file)
    Current Input Test Files:
    1. Withdrawal: Withdrawal_01.in.txt
    2. Login: Login_01.in.txt
    3. Logout: Logout_01.in.txt
    4. Create: Create_01.in.txt
OUTPUTS: 
    Daily Transaction File (formatted 40-character records)
    Current Output Test Files:
    1. Withdrawal: Withdrawal_01.actual.transactions.txt
    2. Login: Login_01.actual.transactions.txt
    3. Logout: Logout_01.actual.transactions.txt
    4. Create: Create_01.actual.transactions.txt
HOW TO RUN: 
    Run the run_all_tests.sh bash script to execute all test cases and generate output transaction files.
    NOTES:
    - Only the 4 test files above are fully implemented and will produce correct outputs.
"""

import sys
from frontend_app import FrontEndApp

def main():
    """
    Entry point for the Banking System Front End.
    INTENTION: To initialize the system components, handle command-line 
               arguments, and start the application's execution loop.
    INTERFACE: Accesses sys.argv for file paths and initializes the FrontEndApp.
    """
    if len(sys.argv) < 3:
        print("Usage: main.py <current_accounts> <trans_log> [test_input]")
        return

    acc_path = sys.argv[1]
    log_path = sys.argv[2]
    
    # Check if we are reading from a test file or live console
    inp = open(sys.argv[3], 'r') if len(sys.argv) > 3 else sys.stdin
    
    # Initialize and run the coordinated FrontEndApp
    app = FrontEndApp(acc_path, log_path, inp)
    app.run()

if __name__ == "__main__":
    main()