"""
CLASS: Validators
INTENTION: Provides a centralized set of utility functions to enforce 
           business rules and data constraints across the banking system.
"""

class Validators:
    """
    Provides validation logic for banking constraints.
    INTENTION: To ensure all user-provided data (names, amounts) adheres to 
               the system's structural and financial requirements.
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
        Ensures name adheres to the 20 character limit.
        INTENTION: To verify that account holder names fit within the 
                   20-character constraint of the Daily Transaction File.
        INTERFACE: Takes a string 'name' and returns True if length is valid.
        """
        return 0 < len(name) <= 20