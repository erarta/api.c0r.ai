"""
Supabase client initialization
Centralized client configuration for all database operations
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from loguru import logger

# Load environment variables from .env file
load_dotenv()

# Must be set in .env file
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Initialize Supabase client
try:
    if SUPABASE_URL and SUPABASE_SERVICE_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        logger.info("Supabase client initialized successfully")
    else:
        logger.warning("Supabase URL or Service Key not provided")
        supabase: Client = None
except Exception as e:
    # For testing environments where env vars might not be set
    logger.warning(f"Failed to initialize Supabase client: {e}")
    supabase: Client = None

def get_client() -> Client:
    """
    Get Supabase client instance
    
    Returns:
        Supabase client instance
        
    Raises:
        RuntimeError: If client is not initialized
    """
    if supabase is None:
        raise RuntimeError("Supabase client is not initialized. Check environment variables.")
    return supabase

def is_client_available() -> bool:
    """
    Check if Supabase client is available
    
    Returns:
        True if client is initialized, False otherwise
    """
    return supabase is not None