from fastapi import FastAPI
from app.routers import predict, health, recommend
  
app = FastAPI()

app.include_router(predict.router)
app.include_router(recommend.router)
app.include_router(health.router)

@app.get("/")
async def root():
    return {"message": "Hello there!"}