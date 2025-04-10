from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controller import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
async def root():
    return {"status": "Robot agent backend running"}