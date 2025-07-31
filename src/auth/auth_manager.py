"""
Authentication Manager for AI Avatar Application

Simple form-based authentication exactly as specified in the Technical Design Document.
Credentials: Login = UTASAvatar, Password = UTASRocks!
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Valid credentials as specified in TDD
VALID_CREDENTIALS = {
    "UTASAvatar": "UTASRocks!"
}

def authenticate_user(username: str, password: str) -> bool:
    """
    Authenticate user with provided credentials.
    
    Args:
        username: Username to authenticate
        password: Password to authenticate
        
    Returns:
        True if credentials are valid, False otherwise
    """
    if not username or not password:
        logger.warning("Authentication failed: Missing username or password")
        return False
    
    if username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password:
        logger.info(f"User '{username}' authenticated successfully")
        return True
    else:
        logger.warning(f"Authentication failed for user '{username}'")
        return False

def is_authenticated(session) -> bool:
    """
    Check if current session is authenticated.
    
    Args:
        session: Flask session object
        
    Returns:
        True if session is authenticated, False otherwise
    """
    return session.get('authenticated', False)

def get_authenticated_user(session) -> Optional[str]:
    """
    Get authenticated username from session.
    
    Args:
        session: Flask session object
        
    Returns:
        Username if authenticated, None otherwise
    """
    if is_authenticated(session):
        return session.get('username')
    return None

def clear_session(session) -> None:
    """
    Clear authentication from session.
    
    Args:
        session: Flask session object
    """
    session.pop('authenticated', None)
    session.pop('username', None)
    logger.info("Session cleared")