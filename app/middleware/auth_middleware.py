from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.auth.jwt_utils import verify_access_token
from starlette.requests import Request

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip WebSocket connections (handled separately in routes)
        if request.scope["type"] == "websocket":
            return await call_next(request)

        # Exclude certain paths from authentication
        excluded_paths = ["/generatetoken"]
        if request.url.path in excluded_paths:
            return await call_next(request)

        # Check for Authorization header
        token = request.headers.get("Authorization")
        if token and verify_access_token(token.replace("Bearer ", "")):
            response = await call_next(request)
            return response

        # Return 401 if token is invalid or missing
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

