"""
Rapid prototype of the Banking System Back End.

Input files:
- old master accounts file in the starter-code format
- merged daily transaction file (40-character transaction records)

Output files:
- new current accounts file
- new master accounts file

Run:
python read.py <old_master_file> <merged_transaction_file> [new_current_file] [new_master_file]
"""

import sys
from print_error import log_constraint_error, log_success
from write import write_new_current_accounts, write_new_master_accounts


STUDENT_FEE = 0.05
NON_STUDENT_FEE = 0.10
VALID_PLANS = {'SP', 'NP'}
VALID_STATUSES = {'A', 'D'}


def read_old_bank_accounts(file_path):
    """Read the starter-code master accounts file into a list of account dictionaries."""
    accounts = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_num, line in enumerate(file, 1):
            clean_line = line.rstrip('\n')

            if len(clean_line) != 45:
                log_constraint_error(
                    f"Invalid length ({len(clean_line)} chars, expected 45)",
                    file_path,
                    fatal=True,
                )

            account_number = clean_line[0:5]
            name = clean_line[6:26].rstrip()
            status = clean_line[27]
            balance_str = clean_line[29:37]
            transactions_str = clean_line[38:42]
            plan_type = clean_line[43:45]

            if name == 'END_OF_FILE':
                break

            if not account_number.isdigit():
                log_constraint_error(f"Invalid account number on line {line_num}", file_path, fatal=True)
            if status not in VALID_STATUSES:
                log_constraint_error(f"Invalid account status on line {line_num}", file_path, fatal=True)
            if plan_type not in VALID_PLANS:
                log_constraint_error(f"Invalid account plan on line {line_num}", file_path, fatal=True)
            if len(balance_str) != 8 or balance_str[5] != '.':
                log_constraint_error(f"Invalid balance format on line {line_num}", file_path, fatal=True)
            if not transactions_str.isdigit():
                log_constraint_error(f"Invalid total transaction count on line {line_num}", file_path, fatal=True)

            try:
                balance = float(balance_str)
                total_transactions = int(transactions_str)
            except ValueError:
                log_constraint_error(f"Invalid numeric field on line {line_num}", file_path, fatal=True)

            accounts.append({
                'account_number': account_number,
                'name': name,
                'status': status,
                'balance': balance,
                'total_transactions': total_transactions,
                'plan': plan_type,
            })

    return accounts


def read_merged_transaction_file(file_path):
    """Read merged transaction records into memory."""
    transactions = []

    with open(file_path, "r", encoding="utf-8") as file:
        for raw_line in file:
            clean_line = raw_line.rstrip("\n")

            if not clean_line.strip():
                continue

            if len(clean_line) != 40:
                log_constraint_error(
                    f"Invalid length ({len(clean_line)} chars, expected 40)",
                    "Transaction File",
                    fatal=False
                )
                continue

            code = clean_line[0:2]
            name = clean_line[3:23].strip()
            account_number = clean_line[24:29]
            amount_str = clean_line[30:38]
            misc = clean_line[39]

            if len(amount_str) != 8 or amount_str[5] != ".":
                log_constraint_error(
                    f"Invalid amount format in transaction record",
                    clean_line,
                    fatal=False
                )
                continue

            try:
                amount = float(amount_str)
            except ValueError:
                log_constraint_error(
                    f"Invalid numeric amount in transaction record",
                    clean_line,
                    fatal=False
                )
                continue

            transactions.append({
                "code": code,
                "name": name,
                "account_number": account_number,
                "amount": amount,
                "misc": misc,
                "raw": clean_line
            })

    return transactions


def get_account_by_number(accounts_by_number, account_number):
    """Return the account dictionary for a given account number, or None."""
    return accounts_by_number.get(account_number)


def get_next_account_number(accounts_by_number):
    """Return the next unused 5-digit account number."""
    if not accounts_by_number:
        return '00001'
    next_number = max(int(number) for number in accounts_by_number) + 1
    return str(next_number).zfill(5)


def count_successful_transaction(account):
    """Increment the successful transaction count for one account."""
    account['total_transactions'] += 1


def apply_daily_fees(accounts):
    """Apply end-of-day transaction fees based on account plan and total transactions."""
    for account in accounts:
        fee_per_transaction = STUDENT_FEE if account['plan'] == 'SP' else NON_STUDENT_FEE
        total_fee = round(account['total_transactions'] * fee_per_transaction, 2)
        account['balance'] = round(account['balance'] - total_fee, 2)
        if account['balance'] < 0:
            account['balance'] = 0.0


def process_transactions(accounts, transactions):
    """Apply the merged transaction log to the old master accounts list."""
    accounts_by_number = {account['account_number']: account for account in accounts}
    pending_transfer = None

    for transaction in transactions:
        code = transaction['code']
        number = transaction['account_number']
        name = transaction['name']
        amount = round(transaction['amount'], 2)
        raw = transaction['raw']

        if code == '00':
            pending_transfer = None
            continue

        if code == '01':
            account = get_account_by_number(accounts_by_number, number)
            if account is None or account['name'] != name or account['status'] != 'A':
                log_constraint_error('Withdrawal from invalid or disabled account', raw)
                continue
            if account['balance'] < amount:
                log_constraint_error('Withdrawal would create a negative balance', raw)
                continue
            account['balance'] = round(account['balance'] - amount, 2)
            count_successful_transaction(account)
            log_success(f"Withdrawal processed. New balance = {account['balance']:.2f}", raw)

        elif code == '02':
            if pending_transfer is None:
                pending_transfer = transaction
                continue

            source = get_account_by_number(accounts_by_number, pending_transfer['account_number'])
            target = get_account_by_number(accounts_by_number, number)
            transfer_amount = round(pending_transfer['amount'], 2)

            if source is None or source['name'] != pending_transfer['name'] or source['status'] != 'A':
                log_constraint_error('Transfer source account is invalid or disabled', pending_transfer['raw'])
            elif target is None or target['status'] != 'A':
                log_constraint_error('Transfer target account is invalid or disabled', raw)
            elif source['balance'] < transfer_amount:
                log_constraint_error('Transfer would create a negative balance', pending_transfer['raw'])
            else:
                source['balance'] = round(source['balance'] - transfer_amount, 2)
                target['balance'] = round(target['balance'] + transfer_amount, 2)
                count_successful_transaction(source)
                count_successful_transaction(target)
                log_success(
                    f"Transfer processed from {source['account_number']} to {target['account_number']} amount {transfer_amount:.2f}",
                    f"{pending_transfer['raw']} | {raw}"
                )

            pending_transfer = None

        elif code == '03':
            account = get_account_by_number(accounts_by_number, number)
            if account is None or account['name'] != name or account['status'] != 'A':
                log_constraint_error('Paybill from invalid or disabled account', raw)
                continue
            if account['balance'] < amount:
                log_constraint_error('Paybill would create a negative balance', raw)
                continue
            account['balance'] = round(account['balance'] - amount, 2)
            count_successful_transaction(account)
            log_success(f"Paybill processed. New balance = {account['balance']:.2f}", raw)

        elif code == '04':
            account = get_account_by_number(accounts_by_number, number)
            if account is None or account['name'] != name or account['status'] != 'A':
                log_constraint_error('Deposit to invalid or disabled account', raw)
                continue
            account['balance'] = round(account['balance'] + amount, 2)
            count_successful_transaction(account)
            log_success(f"Deposit processed. New balance = {account['balance']:.2f}", raw)

        elif code == '05':
            if len(name) == 0 or len(name) > 20:
                log_constraint_error('Create account has invalid account holder name', raw)
                continue
            new_number = get_next_account_number(accounts_by_number)
            if new_number in accounts_by_number:
                log_constraint_error('New account number is not unique', raw)
                continue
            new_account = {
                'account_number': new_number,
                'name': name,
                'status': 'A',
                'balance': amount,
                'total_transactions': 1,
                'plan': 'NP',
            }
            accounts.append(new_account)
            accounts_by_number[new_number] = new_account
            log_success(f"Account created with new number {new_number}", raw)

        elif code == '06':
            account = get_account_by_number(accounts_by_number, number)
            if account is None or account['name'] != name:
                log_constraint_error('Delete account request for unknown account', raw)
                continue
            if account['balance'] != 0:
                log_constraint_error('Delete account requires zero balance', raw)
                continue
            del accounts_by_number[number]
            accounts.remove(account)
            log_success(f"Account {number} deleted", raw)

        elif code == '07':
            account = get_account_by_number(accounts_by_number, number)
            if account is None or account['name'] != name:
                log_constraint_error('Disable account request for unknown account', raw)
                continue
            account['status'] = 'D'
            count_successful_transaction(account)
            log_success(f"Account {number} disabled", raw)

        elif code == '08':
            account = get_account_by_number(accounts_by_number, number)
            if account is None or account['name'] != name:
                log_constraint_error('Change plan request for unknown account', raw)
                continue
            if transaction['misc'] in VALID_PLANS:
                account['plan'] = transaction['misc']
            else:
                account['plan'] = 'SP' if account['plan'] == 'NP' else 'NP'
            count_successful_transaction(account)
            log_success(f"Plan changed to {account['plan']}", raw)

        else:
            log_constraint_error(f'Unknown transaction code {code}', raw)

    return sorted(accounts, key=lambda acc: int(acc['account_number']))


def run_backend(old_master_file, merged_transaction_file,
                new_current_file='new_current_accounts.txt',
                new_master_file='new_master_accounts.txt'):
    """Run the complete Back End flow from input files to output files."""
    accounts = read_old_bank_accounts(old_master_file)
    transactions = read_merged_transaction_file(merged_transaction_file)
    updated_accounts = process_transactions(accounts, transactions)
    apply_daily_fees(updated_accounts)
    write_new_current_accounts(updated_accounts, new_current_file)
    write_new_master_accounts(updated_accounts, new_master_file)
    print(f"SUCCESS: Output written to {new_current_file} and {new_master_file}")
    return updated_accounts


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python read.py <old_master_file> <merged_transaction_file> [new_current_file] [new_master_file]')
        sys.exit(1)

    old_master = sys.argv[1]
    merged_transactions = sys.argv[2]
    current_output = sys.argv[3] if len(sys.argv) >= 4 else 'new_current_accounts.txt'
    master_output = sys.argv[4] if len(sys.argv) >= 5 else 'new_master_accounts.txt'

    run_backend(old_master, merged_transactions, current_output, master_output)