"""
CLASS: Validators
INTENTION: Provides a centralized set of utility functions to enforce 
           business rules and data constraints across the banking system.
"""

class Validators:
    """
    Provides validation logic for banking constraints.
    INTENTION: To ensure all user-provided data (names, amounts, modes) adheres 
               to the system's structural and financial requirements.
    INTERFACE: Offers static methods that return boolean values based on 
               compliance with specific constraints.
    """
    
    @staticmethod
    def validate_amount(amount):
        """
        Checks if amount is positive and within a reasonable range.
        INTENTION: To prevent negative transactions and ensure amounts fit 
                   within the fixed-length 8-character format.
        INTERFACE: Takes a float 'amount' and returns True if valid.
        """
        return 0 < amount <= 999999.99

    @staticmethod
    def validate_name(name):
        """
        Ensures name is not empty and adheres to the 20 character limit.
        INTENTION: To verify that account holder names fit within the 20-character 
                   constraint of the Daily Transaction File. 
                   FIX: Now strips whitespace to prevent empty/blank names (Test 03, 06).
        INTERFACE: Takes a string 'name' and returns True if length is valid.
        """
        clean_name = name.strip()
        return 0 < len(clean_name) <= 20

    @staticmethod
    def validate_mode(mode):
        """
        Ensures the login mode is strictly 'standard' or 'admin'.
        INTENTION: To restrict session access to recognized authorization levels.
                   FIX: Specifically added to resolve Test 02 (Invalid Mode).
        INTERFACE: Takes a string 'mode' and returns True if it is a valid type.
        """
        return mode.lower() in ["standard", "admin"]