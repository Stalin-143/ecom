"""
Input validation and sanitization utilities
"""
import re
from bleach import clean
import email_validator
from urllib.parse import urlparse


def sanitize_string(text: str, max_length: int = 512) -> str:
    """Sanitize string input"""
    if not isinstance(text, str):
        return ""
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Limit length
    text = text[:max_length]
    
    # Remove dangerous characters and HTML tags
    text = clean(text, tags=[], strip=True)
    
    return text


def validate_email(email: str) -> tuple[bool, str]:
    """Validate email address"""
    try:
        email_validator.validate_email(email)
        return True, email.lower()
    except email_validator.EmailNotValidError as e:
        return False, str(e)


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Requirements:
    - At least 8 characters
    - Contains uppercase letter
    - Contains lowercase letter
    - Contains digit
    - Contains special character
    """
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain an uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain a lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain a digit"
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        return False, "Password must contain a special character"
    
    return True, "Password is valid"


def validate_phone(phone: str) -> bool:
    """Validate phone number"""
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\.+]', '', phone)
    
    # Check if it's a valid format (8-15 digits)
    return bool(re.match(r'^\d{8,15}$', cleaned))


def validate_url(url: str) -> bool:
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except:
        return False


def validate_filename(filename: str) -> bool:
    """Validate filename - prevent directory traversal"""
    # Check for directory traversal attempts
    if '..' in filename or '/' in filename or '\\' in filename:
        return False
    
    # Check for null bytes
    if '\x00' in filename:
        return False
    
    return True


def is_sql_injection_attempt(text: str) -> bool:
    """Detect common SQL injection patterns"""
    sql_keywords = [
        r"'\s*;",  # '; 
        r"'\s*OR\s*'",  # ' OR '
        r"'\s*AND\s*'",  # ' AND '
        r"--\s",  # SQL comment
        r";.*DROP",
        r";.*DELETE",
        r";.*INSERT",
        r";.*UPDATE",
        r"UNION.*SELECT",
        r"EXEC\s*\(",
    ]
    
    for pattern in sql_keywords:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False


def is_xss_attempt(text: str) -> bool:
    """Detect common XSS patterns"""
    xss_patterns = [
        r"<script",
        r"javascript:",
        r"on\w+\s*=",  # onload=, onclick=, etc.
        r"<iframe",
        r"<object",
        r"<embed",
    ]
    
    for pattern in xss_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False


def validate_integer(value, min_val=None, max_val=None) -> tuple[bool, int]:
    """Validate integer input"""
    try:
        num = int(value)
        if min_val is not None and num < min_val:
            return False, None
        if max_val is not None and num > max_val:
            return False, None
        return True, num
    except (ValueError, TypeError):
        return False, None


def validate_float(value, min_val=None, max_val=None) -> tuple[bool, float]:
    """Validate float input"""
    try:
        num = float(value)
        if min_val is not None and num < min_val:
            return False, None
        if max_val is not None and num > max_val:
            return False, None
        return True, num
    except (ValueError, TypeError):
        return False, None
