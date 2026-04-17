from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio

import library
import audio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Lifecycle ────────────────────────────────────────────────────────────────

auto_advance_running = False

async def auto_advance_task():
    global auto_advance_running
    auto_advance_running = True
    while auto_advance_running:
        if audio.player.is_finished() and audio.jukebox is not None:
            try:
                next_song_data = audio.jukebox.next_node()
                if next_song_data and "path" in next_song_data:
                    audio.player.play(next_song_data["path"])
                    print(f"Auto-advanced to: {next_song_data.get('name', 'Unknown')}")
            except HTTPException:
                print("Reached end of queue")
        await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(auto_advance_task())

@app.on_event("shutdown")
async def shutdown_event():
    global auto_advance_running
    auto_advance_running = False

# ─── General ──────────────────────────────────────────────────────────────────

@app.get("/")
def home():
    return {"message": "Jukebox backend is running!"}

@app.get("/test")
def test():
    return {"status": "success", "data": "Hello from backend"}

# ─── Library ──────────────────────────────────────────────────────────────────

@app.get("/library")
def get_library():
    return library.get_library()

@app.get("/library/{name}")
def get_song(name: str):
    result = library.find_song(name)
    if result is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return result

# ─── Queue ────────────────────────────────────────────────────────────────────

@app.post("/create")
def create_queue():
    return audio.create_queue()

@app.post("/add")
def enqueue_song(song: dict):
    return audio.jukebox.enqueue(song)

@app.delete("/delete")
def dequeue_song(song: dict):
    return audio.jukebox.dequeue(song)

@app.get("/queue")
def get_queue():
    if audio.jukebox is None:
        return []
    songs, node = [], audio.jukebox.head
    while node:
        songs.append(node.data)
        node = node.next
    return songs

@app.delete("/queue/{index}")
def remove_from_queue(index: int):
    if audio.jukebox is None:
        raise HTTPException(status_code=404, detail="Queue does not exist")
    node, i = audio.jukebox.head, 0
    while node:
        if i == index:
            if node.prev: node.prev.next = node.next
            else: audio.jukebox.head = node.next
            if node.next: node.next.prev = node.prev
            else: audio.jukebox.tail = node.prev
            if audio.jukebox.curr == node:
                audio.jukebox.curr = node.next or node.prev
            audio.jukebox.size -= 1
            return {"status": "removed", "index": index}
        node, i = node.next, i + 1
    raise HTTPException(status_code=404, detail="Index out of range")

# ─── Playback ─────────────────────────────────────────────────────────────────

@app.get("/next")
def next_song():
    next_song_data = audio.jukebox.next_node()
    if next_song_data and "path" in next_song_data:
        audio.player.play(next_song_data["path"])
    return next_song_data

@app.get("/back")
def prev_song():
    prev_song_data = audio.jukebox.prev_node()
    if prev_song_data and "path" in prev_song_data:
        audio.player.play(prev_song_data["path"])
    return prev_song_data

@app.post("/play")
def play_song(song_path: str):
    return audio.player.play(song_path)

@app.post("/pause")
def pause():
    return audio.player.pause()

@app.post("/volume")
def set_volume(level: int):
    if not (0 <= level <= 100):
        raise HTTPException(status_code=400, detail="Volume must be between 0 and 100")
    return audio.player.set_volume(level)

@app.get("/status")
def get_status():
    return audio.player.get_status()

@app.get("/progress")
def get_progress():
    return audio.player.get_progress()

@app.post("/seek")
def seek(position_ms: int):
    if position_ms < 0:
        raise HTTPException(status_code=400, detail="Position must be non-negative")
    return audio.player.seek(position_ms)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)