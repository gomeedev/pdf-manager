from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.ports.auth import AuthUser
from adapters.outbound.supabase_client import get_supabase_client
from adapters.outbound.supabase_auth import SupabaseAuthAdapter

security = HTTPBearer()

def get_auth_adapter() -> SupabaseAuthAdapter:
    client = get_supabase_client()
    return SupabaseAuthAdapter(client)

async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_adapter: SupabaseAuthAdapter = Depends(get_auth_adapter)
) -> AuthUser:
    token = credentials.credentials
    user = auth_adapter.verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
