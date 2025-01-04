from fastapi import APIRouter
from app.auth.jwt_utils import create_access_token

router = APIRouter()

@router.get("/generatetoken")
async def generate_token():
    # Generate a JWT token with a generic payload
    token = create_access_token(data={"sub": "guest_user"})
    return {"access_token": token, "token_type": "bearer"}
