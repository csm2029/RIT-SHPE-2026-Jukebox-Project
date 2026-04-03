from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import library
import audio

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

# Library Endpoints
@app.get("/library")
def get_library():
    return library.get_library()

@app.get("/library/{name}")
def get_song(name: str):
    result = library.find_song(name)
    if result is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return result

# Queue Endpoints
@app.post("/create")
def create_queue():
    return audio.create_queue()

@app.post("/add")
def enqueue_song(song : dict):
    return audio.jukebox.enqueue(song)

@app.delete("/delete")
def dequeue_song( song: dict):
    return audio.jukebox.dequeue(song)

@app.get("/next")
def next_song():
    return audio.jukebox.next_node()
    
@app.get("/back")
def prev_song():
    return audio.jukebox.prev_node()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)