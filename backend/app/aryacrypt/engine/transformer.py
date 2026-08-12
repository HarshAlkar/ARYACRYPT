def string_to_integer(password: str) -> int:
    """
    Transforms a raw string password into a large integer.
    This acts as the first step of preprocessing before Aryabhata encoding.
    
    Args:
        password (str): The raw string password to convert.
        
    Returns:
        int: A large integer representation of the string.
    """
    return int.from_bytes(password.encode('utf-8'), byteorder='big')
