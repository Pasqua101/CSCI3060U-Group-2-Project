from print_error import log_constraint_error


MAX_BALANCE = 99999.99


def _validate_account(account):
    """Validate one in-memory account dictionary before it is written to a file."""
    required_keys = {
        'account_number', 'name', 'status', 'balance', 'total_transactions', 'plan'
    }
    missing = required_keys - set(account.keys())
    if missing:
        raise ValueError(f"Missing account fields: {sorted(missing)}")

    if not str(account['account_number']).isdigit():
        raise ValueError(f"Invalid account number: {account['account_number']}")
    if len(str(account['account_number'])) > 5:
        raise ValueError(f"Account number exceeds 5 digits: {account['account_number']}")
    if len(str(account['name'])) > 20:
        raise ValueError(f"Account name exceeds 20 characters: {account['name']}")
    if account['status'] not in ('A', 'D'):
        raise ValueError(f"Invalid status: {account['status']}")
    if account['plan'] not in ('SP', 'NP'):
        raise ValueError(f"Invalid plan: {account['plan']}")
    if not isinstance(account['balance'], (int, float)):
        raise ValueError(f"Balance must be numeric: {account['balance']}")
    if account['balance'] < 0 or account['balance'] > MAX_BALANCE:
        raise ValueError(f"Balance out of range: {account['balance']}")
    if not isinstance(account['total_transactions'], int) or account['total_transactions'] < 0:
        raise ValueError(f"Invalid transaction count: {account['total_transactions']}")


def write_new_current_accounts(accounts, file_path):
    """
    Write the new current accounts file.

    Format used by the starter code:
    NNNNN AAAAAAAAAAAAAAAAAAAA S PPPPPPPP PP
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        for account in sorted(accounts, key=lambda acc: int(acc['account_number'])):
            _validate_account(account)
            acc_num = str(account['account_number']).zfill(5)
            name = str(account['name']).ljust(20)[:20]
            status = account['status']
            balance = f"{float(account['balance']):08.2f}"
            plan = account['plan']
            file.write(f"{acc_num} {name} {status} {balance} {plan}\n")

        file.write("00000 END_OF_FILE          A 00000.00 NP\n")


def write_new_master_accounts(accounts, file_path):
    """
    Write the new master accounts file.

    Format used by the starter code:
    NNNNN AAAAAAAAAAAAAAAAAAAA S PPPPPPPP TTTT PP
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        for account in sorted(accounts, key=lambda acc: int(acc['account_number'])):
            _validate_account(account)
            acc_num = str(account['account_number']).zfill(5)
            name = str(account['name']).ljust(20)[:20]
            status = account['status']
            balance = f"{float(account['balance']):08.2f}"
            transactions = str(account['total_transactions']).zfill(4)
            plan = account['plan']
            file.write(f"{acc_num} {name} {status} {balance} {transactions} {plan}\n")

        file.write("00000 END_OF_FILE          A 00000.00 0000 NP\n")