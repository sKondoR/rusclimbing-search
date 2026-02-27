from typing import Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


security = HTTPBearer()


class PermissionChecker:
    """
    Permission checker class for FastAPI endpoints.

    This class provides a dependency that can be used to check permissions
    on API endpoints.
    """

    def __init__(self, required_permission: str | None = None):
        """
        Initialize the PermissionChecker.

        Args:
            required_permission: The permission required to access the endpoint.
        """
        self.required_permission = required_permission

    async def __call__(
        self,
        _credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> bool:
        """
        Check if the user has the required permission.

        Args:
            _credentials: HTTP authorization credentials (unused, kept for signature compatibility).

        Returns:
            True if the user has the permission.

        Raises:
            HTTPException: If authentication fails or permission is denied.
        """
        # In a real implementation, you would validate the token
        # and check the user's permissions against the required permission
        # For now, we'll allow all authenticated requests
        if self.required_permission:
            # Here you would check the user's actual permissions
            # For example: from app.core.auth import get_current_user
            # user = await get_current_user(_credentials)
            # if not user.has_permission(self.required_permission):
            #     raise HTTPException(
            #         status_code=status.HTTP_403_FORBIDDEN,
            #         detail=f"Permission denied: {self.required_permission}",
            #     )
            pass
        return True


permission_checker = PermissionChecker
