from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio

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
    # Move to the next song in the queue
    next_song_data = audio.jukebox.next_node()
    # Check if the next song data is valid and has a path, then play it
    if next_song_data and "path" in next_song_data:
        audio.player.play(next_song_data["path"])
    # Get the next song data to return
    return next_song_data
    
@app.get("/back")
def prev_song():
    # Move to the previous song in the queue
    prev_song_data = audio.jukebox.prev_node()
    # Check if the previous song data is valid and has a path, then play it
    if prev_song_data and "path" in prev_song_data:
        audio.player.play(prev_song_data["path"])
    # Get the previous song data to return
    return prev_song_data

@app.post("/play")
# Play the song with the file path provided
def play_song(song_path: str):
    result = audio.player.play(song_path)
    return result

# Pause the song playing
@app.post("/pause")
def pause():
    return audio.player.pause()

# Set the volume level from 0 to 100
@app.post("/volume")
def set_volume(level: int):
    if level < 0 or level > 100:
        raise HTTPException(status_code=400, detail="Volume must be between 0 and 100")
    return audio.player.set_volume(level)

# Get the status of the song playing
@app.get("/status")
def get_status():
    return audio.player.get_status()

# Get the current progress of the song in terms of time and the percentage of the song completed
@app.get("/progress")
def get_progress():
    return audio.player.get_progress()

# Switch to a different point in the song in ms
@app.post("/seek")
def seek(position_ms: int):
    if position_ms < 0:
        raise HTTPException(status_code=400, detail="Position must be non-negative")
    return audio.player.seek(position_ms)

# Flag to determine if the auto advance is running
auto_advance_running = False

# Add a background task to see if the song is done and if it is then go to the next song in the queue and play it
async def auto_advance_task():
    global auto_advance_running
    auto_advance_running = True
    
    # Loop to check if the song is done every second and if it is then go to the next song in the queue and play it
    while auto_advance_running:
        # Check if the song is finished or not
        if audio.player.is_finished() and audio.jukebox is not None:
            try:
                next_song_data = audio.jukebox.next_node()
                # Check if the next song data is valid and has a path, then play it
                if next_song_data and "path" in next_song_data:
                    audio.player.play(next_song_data["path"])
                    print(f"Auto-advanced to: {next_song_data.get('name', 'Unknown')}")
            except HTTPException:
                print("Reached end of queue")
        
        # Wait for a sec before checking again
        await asyncio.sleep(1)

# Start the auto advance when the app is running
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(auto_advance_task())

# Stop the auto advance when the app is shutting down
@app.on_event("shutdown")
async def shutdown_event():
    global auto_advance_running
    auto_advance_running = False
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)