import asyncio
from datetime import datetime
from fastapi import Depends, FastAPI, Request, WebSocket
from sse_starlette import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio.client import Redis
from fastapi.responses import HTMLResponse

from exceptions import (
    AuthenticationError,
    HeadersValidationError,
    create_response_for_exception
)
from redis_service import listen_to_channel, redis_client
from utils import get_headers_token, is_user_authenticated, is_user_recipient

app = FastAPI()

origins = [
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8001/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


async def event():
    while True:
        yield f'{datetime.now()}'
        await asyncio.sleep(1)


@app.get("/notify")
async def notify(request: Request, redis: Redis = Depends(redis_client)):

    try:
        authorization_header = get_headers_token(request.headers)
    except HeadersValidationError as e:
        return create_response_for_exception(msg=e.msg, status=e.status)
    try:
        response = await is_user_authenticated(authorization_header)
        user_id = response.get('user_id')
        return EventSourceResponse(
            listen_to_channel(is_user_recipient, user_id, redis)
        )
    except AuthenticationError as e:
        return create_response_for_exception(msg=e.msg, status=e.status)
