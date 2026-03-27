import copy
import pytest
from read import process_transactions


def base_accounts():
    return [
        {
            "account_number": "00001",
            "name": "John Doe",
            "status": "A",
            "balance": 1000.00,
            "total_transactions": 0,
            "plan": "NP",
        },
        {
            "account_number": "00002",
            "name": "Jane Smith",
            "status": "A",
            "balance": 200.00,
            "total_transactions": 0,
            "plan": "SP",
        },
        {
            "account_number": "00003",
            "name": "Alex Lee",
            "status": "D",
            "balance": 300.00,
            "total_transactions": 0,
            "plan": "NP",
        },
    ]


def test_empty_transaction_list_returns_accounts_unchanged():
    accounts = base_accounts()
    original = copy.deepcopy(accounts)

    updated = process_transactions(accounts, [])

    assert updated == original


def test_end_of_session_transaction_does_nothing(capsys):
    accounts = base_accounts()
    transactions = [
        {
            "code": "00",
            "account_number": "00000",
            "name": "",
            "amount": 0.0,
            "misc": "0",
            "raw": "00                      00000 00000.00 0",
        }
    ]

    updated = process_transactions(accounts, transactions)
    captured = capsys.readouterr()

    assert updated[0]["balance"] == 1000.00
    assert updated[1]["balance"] == 200.00
    assert updated[2]["balance"] == 300.00
    assert captured.out == ""


def test_valid_withdrawal(capsys):
    accounts = base_accounts()
    transactions = [
        {
            "code": "01",
            "account_number": "00001",
            "name": "John Doe",
            "amount": 100.0,
            "misc": "0",
            "raw": "01 John Doe             00001 00100.00 0",
        }
    ]

    updated = process_transactions(accounts, transactions)
    captured = capsys.readouterr()

    assert updated[0]["balance"] == 900.00
    assert updated[0]["total_transactions"] == 1
    assert "SUCCESS:" in captured.out
    assert "Withdrawal processed" in captured.out


def test_withdrawal_invalid_account_logs_error(capsys):
    accounts = base_accounts()
    transactions = [
        {
            "code": "01",
            "account_number": "99999",
            "name": "Ghost",
            "amount": 50.0,
            "misc": "0",
            "raw": "01 Ghost                99999 00050.00 0",
        }
    ]

    updated = process_transactions(accounts, transactions)
    captured = capsys.readouterr()

    assert updated[0]["balance"] == 1000.00
    assert "ERROR:" in captured.out
    assert "Withdrawal from invalid or disabled account" in captured.out


def test_withdrawal_disabled_account_logs_error(capsys):
    accounts = base_accounts()
    transactions = [
        {
            "code": "01",
            "account_number": "00003",
            "name": "Alex Lee",
            "amount": 50.0,
            "misc": "0",
            "raw": "01 Alex Lee             00003 00050.00 0",
        }
    ]

    updated = process_transactions(accounts, transactions)
    captured = capsys.readouterr()

    assert updated[2]["balance"] == 300.00
    assert "ERROR:" in captured.out
    assert "Withdrawal from invalid or disabled account" in captured.out


def test_withdrawal_insufficient_funds_logs_error(capsys):
    accounts = base_accounts()
    transactions = [
        {
            "code": "01",
            "account_number": "00002",
            "name": "Jane Smith",
            "amount": 500.0,
            "misc": "0",
            "raw": "01 Jane Smith           00002 00500.00 0",
        }
    ]

    updated = process_transactions(accounts, transactions)
    captured = capsys.readouterr()

    assert updated[1]["balance"] == 200.00
    assert "ERROR:" in captured.out
    assert "Withdrawal would create a negative balance" in captured.out


def test_first_transfer_record_only_sets_pending_transfer(capsys):
    accounts = base_accounts()
    transactions = [
        {
            "code": "02",
            "account_number": "00001",
            "name": "John Doe",
            "amount": 50.0,
            "misc": "0",
            "raw": "02 John Doe             00001 00050.00 0",
        }
    ]

    updated = process_transactions(accounts, transactions)
    captured = capsys.readouterr()

    assert updated[0]["balance"] == 1000.00
    assert updated[1]["balance"] == 200.00
    assert captured.out == ""


def test_valid_transfer_pair(capsys):
    accounts = base_accounts()
    transactions = [
        {
            "code": "02",
            "account_number": "00001",
            "name": "John Doe",
            "amount": 50.0,
            "misc": "0",
            "raw": "02 John Doe             00001 00050.00 0",
        },
        {
            "code": "02",
            "account_number": "00002",
            "name": "Jane Smith",
            "amount": 0.0,
            "misc": "0",
            "raw": "02 Jane Smith           00002 00000.00 0",
        },
    ]

    updated = process_transactions(accounts, transactions)
    captured = capsys.readouterr()

    john = next(acc for acc in updated if acc["account_number"] == "00001")
    jane = next(acc for acc in updated if acc["account_number"] == "00002")

    assert john["balance"] == 950.00
    assert jane["balance"] == 250.00
    assert john["total_transactions"] == 1
    assert jane["total_transactions"] == 1
    assert "SUCCESS:" in captured.out
    assert "Transfer processed" in captured.out


def test_transfer_invalid_target_logs_error(capsys):
    accounts = base_accounts()
    transactions = [
        {
            "code": "02",
            "account_number": "00001",
            "name": "John Doe",
            "amount": 50.0,
            "misc": "0",
            "raw": "02 John Doe             00001 00050.00 0",
        },
        {
            "code": "02",
            "account_number": "99999",
            "name": "Ghost",
            "amount": 0.0,
            "misc": "0",
            "raw": "02 Ghost                99999 00000.00 0",
        },
    ]

    updated = process_transactions(accounts, transactions)
    captured = capsys.readouterr()

    assert updated[0]["balance"] == 1000.00
    assert "ERROR:" in captured.out
    assert "Transfer target account is invalid or disabled" in captured.out


def test_valid_paybill(capsys):
    accounts = base_accounts()
    transactions = [
        {
            "code": "03",
            "account_number": "00001",
            "name": "John Doe",
            "amount": 100.0,
            "misc": "0",
            "raw": "03 John Doe             00001 00100.00 0",
        }
    ]

    updated = process_transactions(accounts, transactions)
    captured = capsys.readouterr()

    assert updated[0]["balance"] == 900.00
    assert updated[0]["total_transactions"] == 1
    assert "SUCCESS:" in captured.out
    assert "Paybill processed" in captured.out


def test_valid_deposit(capsys):
    accounts = base_accounts()
    transactions = [
        {
            "code": "04",
            "account_number": "00001",
            "name": "John Doe",
            "amount": 50.0,
            "misc": "0",
            "raw": "04 John Doe             00001 00050.00 0",
        }
    ]

    updated = process_transactions(accounts, transactions)
    captured = capsys.readouterr()

    assert updated[0]["balance"] == 1050.00
    assert updated[0]["total_transactions"] == 1
    assert "SUCCESS:" in captured.out
    assert "Deposit processed" in captured.out


def test_valid_create_account(capsys):
    accounts = base_accounts()
    transactions = [
        {
            "code": "05",
            "account_number": "00000",
            "name": "New User",
            "amount": 200.0,
            "misc": "0",
            "raw": "05 New User             00000 00200.00 0",
        }
    ]

    updated = process_transactions(accounts, transactions)
    captured = capsys.readouterr()

    assert len(updated) == 4
    new_account = next(acc for acc in updated if acc["account_number"] == "00004")
    assert new_account["name"] == "New User"
    assert new_account["balance"] == 200.00
    assert new_account["status"] == "A"
    assert new_account["plan"] == "NP"
    assert "SUCCESS:" in captured.out
    assert "Account created with new number 00004" in captured.out


def test_create_with_invalid_name_logs_error(capsys):
    accounts = base_accounts()
    transactions = [
        {
            "code": "05",
            "account_number": "00000",
            "name": "",
            "amount": 200.0,
            "misc": "0",
            "raw": "05                      00000 00200.00 0",
        }
    ]

    updated = process_transactions(accounts, transactions)
    captured = capsys.readouterr()

    assert len(updated) == 3
    assert "ERROR:" in captured.out
    assert "Create account has invalid account holder name" in captured.out


def test_valid_delete_zero_balance_account(capsys):
    accounts = [
        {
            "account_number": "00009",
            "name": "Zero User",
            "status": "A",
            "balance": 0.0,
            "total_transactions": 0,
            "plan": "NP",
        }
    ]
    transactions = [
        {
            "code": "06",
            "account_number": "00009",
            "name": "Zero User",
            "amount": 0.0,
            "misc": "0",
            "raw": "06 Zero User            00009 00000.00 0",
        }
    ]

    updated = process_transactions(accounts, transactions)
    captured = capsys.readouterr()

    assert updated == []
    assert "SUCCESS:" in captured.out
    assert "Account 00009 deleted" in captured.out


def test_valid_disable(capsys):
    accounts = base_accounts()
    transactions = [
        {
            "code": "07",
            "account_number": "00001",
            "name": "John Doe",
            "amount": 0.0,
            "misc": "0",
            "raw": "07 John Doe             00001 00000.00 0",
        }
    ]

    updated = process_transactions(accounts, transactions)
    captured = capsys.readouterr()

    assert updated[0]["status"] == "D"
    assert updated[0]["total_transactions"] == 1
    assert "SUCCESS:" in captured.out
    assert "Account 00001 disabled" in captured.out


def test_valid_change_plan_toggle(capsys):
    accounts = base_accounts()
    transactions = [
        {
            "code": "08",
            "account_number": "00002",
            "name": "Jane Smith",
            "amount": 0.0,
            "misc": "0",
            "raw": "08 Jane Smith           00002 00000.00 0",
        }
    ]

    updated = process_transactions(accounts, transactions)
    captured = capsys.readouterr()

    assert updated[1]["plan"] == "NP"
    assert updated[1]["total_transactions"] == 1
    assert "SUCCESS:" in captured.out
    assert "Plan changed to NP" in captured.out


def test_unknown_transaction_code_logs_error(capsys):
    accounts = base_accounts()
    transactions = [
        {
            "code": "99",
            "account_number": "00001",
            "name": "John Doe",
            "amount": 0.0,
            "misc": "0",
            "raw": "99 John Doe             00001 00000.00 0",
        }
    ]

    updated = process_transactions(accounts, transactions)
    captured = capsys.readouterr()

    assert updated[0]["balance"] == 1000.00
    assert "ERROR:" in captured.out
    assert "Unknown transaction code 99" in captured.out


def test_mixed_transactions_cover_loop_multiple_iterations(capsys):
    accounts = base_accounts()
    transactions = [
        {
            "code": "04",
            "account_number": "00001",
            "name": "John Doe",
            "amount": 50.0,
            "misc": "0",
            "raw": "04 John Doe             00001 00050.00 0",
        },
        {
            "code": "01",
            "account_number": "00003",
            "name": "Alex Lee",
            "amount": 20.0,
            "misc": "0",
            "raw": "01 Alex Lee             00003 00020.00 0",
        },
        {
            "code": "03",
            "account_number": "00002",
            "name": "Jane Smith",
            "amount": 10.0,
            "misc": "0",
            "raw": "03 Jane Smith           00002 00010.00 0",
        },
    ]

    updated = process_transactions(accounts, transactions)
    captured = capsys.readouterr()

    john = next(acc for acc in updated if acc["account_number"] == "00001")
    jane = next(acc for acc in updated if acc["account_number"] == "00002")
    alex = next(acc for acc in updated if acc["account_number"] == "00003")

    assert john["balance"] == 1050.00
    assert jane["balance"] == 190.00
    assert alex["balance"] == 300.00

    assert "SUCCESS:" in captured.out
    assert "ERROR:" in captured.out