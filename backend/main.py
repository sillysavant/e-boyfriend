from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.constant.config import SECRET_KEY
from app.middleware.log import APIGatewayMiddleware
from app.routers import conversation
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.add_middleware(APIGatewayMiddleware)
router_list = [
    conversation.router
]

for router in router_list:
    app.include_router(router=router)
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'], #  allows requests from any origin 
    allow_credentials=True,
    allow_methods=['*'], # allows all HTTP methods
    allow_headers=['*'], # allows all headers
)

# models.Base.metadata.create_all(engine)