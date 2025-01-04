import uvicorn
from fastapi import FastAPI
from app.routers import chatproxyrequest, generateproxyrequest, generatetoken
from app.middleware.auth_middleware import AuthMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Middleware
app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers for organizing API endpoints
app.include_router(chatproxyrequest.router)
app.include_router(generateproxyrequest.router)
app.include_router(generatetoken.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the LoLaMo"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)