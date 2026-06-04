from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import notes
from app.auth import routes as auth_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Notes Vault API",
    description="A secure API for creating and managing personal notes",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(auth_routes.router)
app.include_router(notes.router)

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}