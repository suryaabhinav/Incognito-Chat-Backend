from fastapi import FastAPI
from app.routers import chatproxyrequest, generateproxyrequest

app = FastAPI()

# Include routers for organizing API endpoints
app.include_router(chatproxyrequest.router)
app.include_router(generateproxyrequest.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the LoLaMo"}

