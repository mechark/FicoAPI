from fastapi import FastAPI
from app.routers import predict, health, recommend
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(predict.router)
app.include_router(recommend.router)
app.include_router(health.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello there!"}
