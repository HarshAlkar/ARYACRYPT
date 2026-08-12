import string
import unicodedata
from typing import List, Tuple
from .constants import MIN_PASSWORD_LENGTH


class PasswordValidationError(Exception):
    """
    Custom exception raised when password validation fails.
    Contains a detailed list of specific validation failures.
    """
    def __init__(self, errors: List[str]):
        super().__init__("Password validation failed: " + ", ".join(errors))
        self.errors = errors


class PasswordValidator:
    """
    Validates input passwords before they are transformed by the Aryabhata framework.
    
    Responsibilities:
    - Verifies password length against system constraints.
    - Ensures adequate character complexity (letters, numbers).
    - Checks for special symbols.
    - Validates Unicode safety (rejects control/non-printable characters).
    """

    @staticmethod
    def validate(password: str) -> Tuple[bool, List[str]]:
        """
        Performs a comprehensive validation of the password.
        
        Args:
            password (str): The raw user password.
            
        Returns:
            Tuple[bool, List[str]]: A tuple containing a boolean success flag,
                                    and a list of detailed error messages if any.
        """
        errors: List[str] = []
        
        if not isinstance(password, str):
            return False, ["Password must be a valid text string."]

        # 1. Unicode Safety (Check for non-printable control characters)
        if any(unicodedata.category(c).startswith('C') for c in password):
            errors.append("Password contains invalid, non-printable, or control Unicode characters.")
            
        # 2. Length Check
        if len(password) < MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")
            
        # 3. Alphabetical Character Check
        if not any(c.isalpha() for c in password):
            errors.append("Password must contain at least one alphabetical character.")
            
        # 4. Numeric Character Check
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one numeric character (0-9).")
            
        # 5. Special Symbols Check
        special_symbols = set(string.punctuation)
        if not any(c in special_symbols for c in password):
            errors.append("Password must contain at least one special symbol (e.g., @, #, $, !).")
            
        return len(errors) == 0, errors

    @staticmethod
    def validate_or_raise(password: str) -> None:
        """
        Validates the password and raises a detailed PasswordValidationError 
        if the criteria are not met. Useful for fail-fast application logic.
        
        Args:
            password (str): The raw user password.
            
        Raises:
            PasswordValidationError: If validation fails.
        """
        is_valid, errors = PasswordValidator.validate(password)
        if not is_valid:
            raise PasswordValidationError(errors)
