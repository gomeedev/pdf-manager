from supabase import create_client, Client
from core.config import settings

def get_supabase_client(token: str = None) -> Client:
    """
    Returns a Supabase client.
    If a token is provided, the client is initialized with the user's JWT
    to enforce Row Level Security (RLS) on the database side.
    """
    client = create_client(settings.supabase_url, settings.supabase_anon_key)
    if token:
        # We can dynamically pass the jwt securely to impersonate the user for RLS
        client.postgrest.auth(token)
    return client

def get_service_client() -> Client:
    """
    Returns a Supabase client using the Service Role Key.
    This bypasses all RLS policies. Use only for internal/admin operations.
    """
    return create_client(settings.supabase_url, settings.supabase_service_key)
