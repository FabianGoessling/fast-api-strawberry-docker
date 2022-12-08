import asyncio
import uuid
from concurrent.futures.process import _MAX_WINDOWS_WORKERS
from typing import Dict, List

import strawberry
from fastapi import FastAPI
from fastapi.responses import FileResponse
from strawberry.fastapi import GraphQLRouter

from .store import queues


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello World"


@strawberry.type
class Message:
    user_id: uuid.UUID
    user_name: str
    text: str


@strawberry.type
class Messages:
    messages: List[Message]


@strawberry.type
class MessageReturn(Message):
    success: bool


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def send_message(self, message: str, user_name: str, user_id: uuid.UUID) -> MessageReturn:
        for queue in queues:
            await queue.put(Message(**{"text": message, "user_id": user_id, "user_name": user_name}))
        return MessageReturn(**{"success": True, "text": message, "user_id": user_id, "user_name": user_name})


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def messages(self) -> Messages:
        queue = asyncio.Queue()
        queues.append(queue)
        messages = []
        try:
            while True:
                print("Listening")
                message = await queue.get()
                messages.append(message)
                queue.task_done()
                yield Messages(messages=messages)
        except asyncio.CancelledError:
            queues.remove(queue)
            raise


schema = strawberry.Schema(query=Query, subscription=Subscription, mutation=Mutation)


graphql_app = GraphQLRouter(schema)


app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")


@app.get("/chat")
async def get():
    return FileResponse("fast-api-strawberry-docker/chat_ws.html")
