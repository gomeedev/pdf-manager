from typing import Protocol, Optional
from uuid import UUID
from pydantic import BaseModel

class AuthUser(BaseModel):
    id: UUID
    email: str

class AuthPort(Protocol):
    def verify_token(self, token: str) -> Optional[AuthUser]:
        ...
