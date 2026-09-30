from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AuthorizationState(str, Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


def _require_aware(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


@dataclass
class Authorization:
    authorization_id: str
    agent_id: str
    objective: str
    created_at: datetime
    expires_at: datetime
    state: AuthorizationState = AuthorizationState.ACTIVE
    revoked_at: datetime | None = None

    def __post_init__(self) -> None:
        _require_aware(self.created_at, "created_at")
        _require_aware(self.expires_at, "expires_at")

        if self.expires_at <= self.created_at:
            raise ValueError("expires_at must be later than created_at")

        if self.state is AuthorizationState.EXPIRED:
            raise ValueError(
                "EXPIRED is derived from time and cannot be set directly"
            )

        if self.revoked_at is not None:
            _require_aware(self.revoked_at, "revoked_at")

            if not self.created_at <= self.revoked_at < self.expires_at:
                raise ValueError(
                    "revoked_at must be within the authorization window"
                )

            self.state = AuthorizationState.REVOKED

        if (
            self.state is AuthorizationState.REVOKED
            and self.revoked_at is None
        ):
            raise ValueError(
                "REVOKED authorization requires revoked_at"
            )

    def is_expired(self, at_time: datetime) -> bool:
        _require_aware(at_time, "at_time")
        return at_time >= self.expires_at

    def effective_state(
        self,
        at_time: datetime,
    ) -> AuthorizationState:
        _require_aware(at_time, "at_time")

        if (
            self.state is AuthorizationState.REVOKED
            and self.revoked_at is not None
            and self.revoked_at <= at_time
        ):
            return AuthorizationState.REVOKED

        if self.is_expired(at_time):
            return AuthorizationState.EXPIRED

        return AuthorizationState.ACTIVE

    def revoke(self, revoked_at: datetime) -> None:
        _require_aware(revoked_at, "revoked_at")

        if self.state is AuthorizationState.REVOKED:
            raise ValueError("authorization is already revoked")

        if revoked_at < self.created_at:
            raise ValueError(
                "authorization cannot be revoked before it exists"
            )

        if revoked_at >= self.expires_at:
            raise ValueError(
                "expired authorization cannot be revoked"
            )

        self.state = AuthorizationState.REVOKED
        self.revoked_at = revoked_at
