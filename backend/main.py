from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.constant.config import REDIS_URL, SECRET_KEY
from app.database import models
from app.middleware.log import APIGatewayMiddleware
from app.routers import conversation
from starlette.middleware.sessions import SessionMiddleware
from app.database.database import session_manager
#from aioredis import Redis
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):  
    await session_manager.create_tables()
    yield
    if session_manager._engine is not None:
        await session_manager.close()
        
#     redis_client = Redis.from_url(REDIS_URL, decode_responses=True)
#     try:
#         await redis_client.ping()
#         app.state.redis = redis_client
#         yield
#     finally:
#         await redis_client.close()
        
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'], #  allows requests from any origin 
    allow_credentials=True,
    allow_methods=['*'], # allows all HTTP methods
    allow_headers=['*'], # allows all headers
)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.add_middleware(APIGatewayMiddleware)

router_list = [
    conversation.router
]

for router in router_list:
    app.include_router(router=router)
    

#redis_client = Redis.from_url(REDIS_URL, decode_responses=True)
