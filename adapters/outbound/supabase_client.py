from supabase import create_client, Client, ClientOptions
from core.config import settings

def get_supabase_client(token: str = None) -> Client:
    """
    Returns a Supabase client.
    If a token is provided, the client is initialized with the user's JWT
    to enforce Row Level Security (RLS) on both the database and storage side.
    """
    if token:
        options = ClientOptions(headers={"Authorization": f"Bearer {token}"})
        client = create_client(settings.supabase_url, settings.supabase_anon_key, options=options)
        # Required to correctly pass the JWT context to PostgreSQL via Postgrest
        client.postgrest.auth(token)
    else:
        client = create_client(settings.supabase_url, settings.supabase_anon_key)
        
    return client

def get_service_client() -> Client:
    """
    Returns a Supabase client using the Service Role Key.
    This bypasses all RLS policies. Use only for internal/admin operations.
    """
    return create_client(settings.supabase_url, settings.supabase_service_key)
