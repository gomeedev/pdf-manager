from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from core.ports.database import DatabasePort
from core.ports.storage import StoragePort
from adapters.outbound.supabase_client import get_supabase_client
from adapters.outbound.supabase_db import SupabaseDatabaseAdapter
from adapters.outbound.supabase_storage import SupabaseStorageAdapter
from core.security import security

def get_db_port(credentials: HTTPAuthorizationCredentials = Depends(security)) -> DatabasePort:
    """
    Returns the database port with the client initialized with the user's JWT token.
    This ensures all database operations respect Row Level Security (RLS).
    """
    token = credentials.credentials
    client = get_supabase_client(token)
    return SupabaseDatabaseAdapter(client)

def get_storage_port(credentials: HTTPAuthorizationCredentials = Depends(security)) -> StoragePort:
    """
    Returns the storage port with the client initialized with the user's JWT token.
    Enforces Storage RLS policies.
    """
    token = credentials.credentials
    client = get_supabase_client(token)
    return SupabaseStorageAdapter(client)
