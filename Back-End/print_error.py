import sys


def log_constraint_error(description, context, fatal=False):
    """
    Print an error in the required project format.

    Args:
        description: Human-readable description of the problem.
        context: Transaction info for constraint errors, or file name for fatal errors.
        fatal: When True, stop the program immediately.
    """
    if fatal:
        print(f"ERROR: Fatal error - File {context} - {description}")
        sys.exit(1)
    else:
        print(f"ERROR: {context}: {description}")


def log_success(message, context):
    """
    Print a success message for a valid processed transaction.
    """
    print(f"SUCCESS: {context}: {message}")