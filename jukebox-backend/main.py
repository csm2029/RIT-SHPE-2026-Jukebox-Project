from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import library

app = FastAPI()

# Allow React to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Jukebox backend is running!"}

@app.get("/test")
def test():
    return {"status": "success", "data": "Hello from backend"}

@app.get("/library")
def get_library():
    return library.get_library()

@app.get("/library/{name}")
def get_song(name: str):
    result = library.find_song(name)
    if result is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)