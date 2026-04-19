from core.ports.auth import AuthPort, AuthUser
from supabase import Client
from typing import Optional
from uuid import UUID

class SupabaseAuthAdapter(AuthPort):
    def __init__(self, client: Client):
        self.client = client

    def verify_token(self, token: str) -> Optional[AuthUser]:
        try:
            response = self.client.auth.get_user(token)
            if response and response.user:
                return AuthUser(
                    id=UUID(response.user.id),
                    email=response.user.email
                )
        except Exception:
            pass
        return None
