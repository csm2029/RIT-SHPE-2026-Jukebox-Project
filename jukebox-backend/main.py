from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import time
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

def require_queue():
    #  Check if the jukebox queue is created, if not return an error
    if audio.jukebox is None:
        raise HTTPException(status_code=404, detail="Queue not created. POST /create first.")

# Queue Endpoints
@app.post("/create")
def create_queue():
    return audio.create_queue(force=True)

@app.post("/add")
def enqueue_song(song : dict):
    require_queue()
    return audio.jukebox.enqueue(song)

@app.get("/next")
def next_song():
    require_queue()
    next_song_data = audio.jukebox.next_node()
    if next_song_data and "file_path" in next_song_data:
        audio.player.play(next_song_data["file_path"])
    return next_song_data

@app.get("/back")
def prev_song():
    require_queue()
    # Move to the previous song in the queue
    prev_song_data = audio.jukebox.prev_node()
    # Check if the previous song data is valid and has a path, then play it
    if prev_song_data and "file_path" in prev_song_data:
        audio.player.play(prev_song_data["file_path"])
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

async def auto_advance_task():
    global auto_advance_running
    auto_advance_running = True
    
    while auto_advance_running:
        if audio.player.is_finished() and audio.jukebox is not None:
            time_since_manual = time.time() - audio.player.last_manual_play_time
            if time_since_manual > 3:
                try:
                    next_song_data = audio.jukebox.next_node()
                    if next_song_data and "file_path" in next_song_data:
                        audio.player.play(next_song_data["file_path"])
                        print(f"Auto-advanced to: {next_song_data.get('name', 'Unknown')}")
                except HTTPException:
                    print("Reached end of queue")
        
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
    
@app.get("/queue")
def get_queue():
    if audio.jukebox is None:
        return []
    songs = []
    node = audio.jukebox.curr
    while node:
        songs.append(node.data)
        node = node.next
    return songs

@app.post("/play-from-queue")
def play_from_queue(song: dict):
    song_path = song.get("file_path")
    if audio.jukebox is not None:
        node = audio.jukebox.head
        found = False
        while node:
            if node.data.get("file_path") == song_path:
                audio.jukebox.curr = node
                found = True
                break
            node = node.next
        if not found:
            if audio.jukebox.curr is not None:
                audio.jukebox.curr.data = song
                audio.jukebox.curr.prev = None
                audio.jukebox.head = audio.jukebox.curr
                count = 0
                n = audio.jukebox.head
                while n:
                    count += 1
                    n = n.next
                audio.jukebox.size = count
            else:
                new_node = audio.Node(song)
                audio.jukebox.head = new_node
                audio.jukebox.tail = new_node
                audio.jukebox.curr = new_node
                audio.jukebox.size = 1

    audio.player.last_manual_play_time = time.time()
    result = audio.player.play(song_path)
    return result

@app.delete("/queue/{index}")
def remove_from_queue(index: int):
    require_queue()
    node = audio.jukebox.head
    i = 0
    while node:
        if i == index:
            is_current = (audio.jukebox.curr == node)

            if node.prev:
                node.prev.next = node.next
            else:
                audio.jukebox.head = node.next
            if node.next:
                node.next.prev = node.prev
            else:
                audio.jukebox.tail = node.prev
            if is_current:
                audio.jukebox.curr = node.next or node.prev
            audio.jukebox.size -= 1
            return {"status": "removed", "index": index}
        node = node.next
        i += 1
    raise HTTPException(status_code=404, detail="Index out of range")


@app.get("/reset-queue")
def reset_queue():
    return audio.create_queue(force=True)


@app.get("/debug-queue")
def debug_queue():
    if audio.jukebox is None:
        return {"error": "no queue"}
    nodes = []
    node = audio.jukebox.head
    while node:
        nodes.append({
            "name": node.data.get("name"),
            "is_curr": node == audio.jukebox.curr,
            "is_head": node == audio.jukebox.head,
            "is_tail": node == audio.jukebox.tail,
        })
        node = node.next
    return {"size": audio.jukebox.size, "nodes": nodes}
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)