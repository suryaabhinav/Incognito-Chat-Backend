import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.auth.jwt_utils import verify_access_token
from app.llmops.core import ContextAwareLLMChain
from langchain_ollama import OllamaLLM
import traceback

# Initialize LLM
llm = OllamaLLM(model="llama3", streaming=True, max_tokens=4096)
chain_handler = ContextAwareLLMChain(llm=llm)

router = APIRouter()

# Store message queues for WebSocket clients
clients = {}

@router.websocket("/ws/chatproxyrequest")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    
    # Verify token
    payload = verify_access_token(token)
    if not payload:
        await websocket.close(code=1008)
        return
    
    await websocket.accept()

    # Unique queue for this client
    message_queue = asyncio.Queue()
    clients[websocket] = message_queue

    try:
        # Start a loop for processing messages from the client
        while True:
            # Read a new message from the client
            user_message = await websocket.receive_text()

            # Enqueue the message for sequential processing
            await message_queue.put(user_message)

            # Process messages sequentially
            while not message_queue.empty():
                message = await message_queue.get()
                response = chain_handler.get_response(question=message)

                # Send the response back to the client
                async for chunk in response:
                    await websocket.send_text(chunk)
                    
    except WebSocketDisconnect as e:
        print(f"WebSocket disconnected: {e.code} - {e.reason}")                  
             
    except Exception as e:
        print(f"Connection closed: {e}")
        # traceback.print_exc()
    finally:
        # Clean up on disconnect
        del clients[websocket]
        # await websocket.close()

@router.websocket("/ws/hello")
async def hello_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        await websocket.send_text("Hello World")
    except WebSocketDisconnect:
        print("WebSocket connection closed")
