from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import httpx

router = APIRouter()

@router.post("/chatproxyrequest")
async def chatproxyrequest(request: Request):

	url = "http://127.0.0.1:11434/api/chat"
	data = await request.json()
	headers = {"Content-Type": "application/json"}

	async def stream_response():
		async with httpx.AsyncClient() as client:
			async with client.stream("POST", url, json=data) as resp:
				async for chunk in resp.aiter_bytes():
					yield chunk


	return StreamingResponse(stream_response(), media_type="application/json")

