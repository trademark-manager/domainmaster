from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        api_key: str,
    ):
        super().__init__(app)
        self.api_key = api_key

    async def dispatch(self, request: Request, call_next):
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(status_code=403, content={"detail": "Unauthorized"})
        token = authorization.split(" ")[1]
        if token != self.api_key:
            return JSONResponse(status_code=403, content={"detail": "Unauthorized"})
        return await call_next(request)
