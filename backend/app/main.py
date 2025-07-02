import uvicorn
from fastapi import FastAPI
from .database import Base, engine
from .routers import characters, jobs

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="EVE Online Industrial Tracker", version="0.1.0")

app.include_router(characters.router)
app.include_router(jobs.router)


@app.get("/")
async def root():
    return {"message": "EVE Industrial Tracker API running"}


if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)