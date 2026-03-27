import pytest
from read import read_merged_transaction_file


def write_file(tmp_path, filename, content):
    file_path = tmp_path / filename
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)


def test_valid_transaction_line(tmp_path):
    content = "04 John Doe             00001 00050.00 0\n"
    file_path = write_file(tmp_path, "valid.txt", content)

    transactions = read_merged_transaction_file(file_path)

    assert len(transactions) == 1
    assert transactions[0]["code"] == "04"
    assert transactions[0]["name"] == "John Doe"
    assert transactions[0]["account_number"] == "00001"
    assert transactions[0]["amount"] == 50.00
    assert transactions[0]["misc"] == "0"
    assert transactions[0]["raw"] == "04 John Doe             00001 00050.00 0"


def test_blank_line_is_skipped(tmp_path, capsys):
    content = "\n"
    file_path = write_file(tmp_path, "blank.txt", content)

    transactions = read_merged_transaction_file(file_path)
    captured = capsys.readouterr()

    assert transactions == []
    assert captured.out == ""


def test_invalid_length_logs_error_and_skips_line(tmp_path, capsys):
    content = "04 John Doe 00001 00050.00 0\n"
    file_path = write_file(tmp_path, "bad_length.txt", content)

    transactions = read_merged_transaction_file(file_path)
    captured = capsys.readouterr()

    assert transactions == []
    assert "ERROR:" in captured.out
    assert "Invalid length" in captured.out


def test_invalid_amount_format_logs_error_and_skips_line(tmp_path, capsys):
    content = "04 John Doe             00001 00050000 0\n"
    file_path = write_file(tmp_path, "bad_format.txt", content)

    transactions = read_merged_transaction_file(file_path)
    captured = capsys.readouterr()

    assert transactions == []
    assert "ERROR:" in captured.out
    assert "Invalid amount format in transaction record" in captured.out


def test_non_numeric_amount_logs_error_and_skips_line(tmp_path, capsys):
    content = "04 John Doe             00001 ABCDE.FG 0\n"
    file_path = write_file(tmp_path, "non_numeric.txt", content)

    transactions = read_merged_transaction_file(file_path)
    captured = capsys.readouterr()

    assert transactions == []
    assert "ERROR:" in captured.out
    assert "Invalid numeric amount in transaction record" in captured.out


def test_mixed_file_returns_only_valid_transactions(tmp_path, capsys):
    content = (
        "04 John Doe             00001 00050.00 0\n"
        "\n"
        "04 John Doe 00001 00050.00 0\n"
        "04 John Doe             00001 ABCDE.FG 0\n"
        "03 Jane Smith           00002 00020.00 0\n"
    )
    file_path = write_file(tmp_path, "mixed.txt", content)

    transactions = read_merged_transaction_file(file_path)
    captured = capsys.readouterr()

    assert len(transactions) == 2
    assert transactions[0]["code"] == "04"
    assert transactions[0]["name"] == "John Doe"
    assert transactions[0]["amount"] == 50.00

    assert transactions[1]["code"] == "03"
    assert transactions[1]["name"] == "Jane Smith"
    assert transactions[1]["amount"] == 20.00

    assert "ERROR:" in captured.out