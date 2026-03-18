"""
CLASS: Session
INTENTION: Manages the lifecycle of a user session, including authentication state, 
           user permissions, and transaction limits.
"""

class Session:
    """
    Tracks login state and enforces mode-based constraints.
    INTENTION: To provide a centralized state manager that dictates what actions 
               a user is permitted to perform based on their login status and mode.
    INTERFACE: Maintains boolean login status and strings for mode/user identification.
    """
    def __init__(self):
        """
        Initializes a default, logged-out session state.
        INTENTION: To ensure every new session starts with no privileges or user data.
        """
        self.is_logged_in = False
        self.mode = None # standard or admin 
        self.user = None # Renamed from current_user to match FrontEndApp expectations
        self.withdraw_total = 0.0 # Track for $500 limit 

    def login(self, mode, user=None):
        """
        Initializes a new session.
        INTENTION: To transition the system into an active state and record 
                   the authorization level (standard/admin) of the user.
        INTERFACE: Takes a string 'mode' and an optional 'user' name.
        """
        self.is_logged_in = True
        self.mode = mode
        self.user = user # Set to match the FrontEndApp variable name

    def logout(self):
        """
        Resets session variables.
        INTENTION: To clear all sensitive session data and return the system 
                   to a secure, logged-out state.
        """
        self.__init__()

    def can_do_privileged(self):
        """
        Returns true if mode is admin.
        INTENTION: To serve as a guard for administrative-only transactions 
                   like 'create' or 'delete'.
        INTERFACE: Returns a boolean based on current session mode.
        """
        return self.mode == 'admin'