from fastapi import HTTPException
from fastapi.responses import JSONResponse
import vlc
import time

# ─── Nodes & Queue ────────────────────────────────────────────────────────────

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None

class Queue:
    def __init__(self):
        self.head = None
        self.tail = None
        self.curr = None
        self.size = 0

    def enqueue(self, data):
        new_node = Node(data)
        prev_node = self.tail
        if self.tail:
            self.tail.next = new_node
        self.tail = new_node
        self.tail.prev = prev_node
        if self.head is None:
            self.head = new_node
            self.curr = new_node
        self.size += 1
        return new_node.data

    def dequeue(self, data):
        if self.size == 0:
            return
        curr = self.head
        while curr is not None and curr.data != data:
            curr = curr.next
            if curr is None:
                raise HTTPException(status_code=404, detail="Song not found in the Queue")
        prev_node, next_node = curr.prev, curr.next
        if prev_node:
            prev_node.next = next_node
        else:
            self.head = next_node
        if next_node:
            next_node.prev = prev_node
        else:
            self.tail = prev_node
        self.curr = next_node if next_node else prev_node
        self.size -= 1
        return curr.data

    def next_node(self):
        if self.curr == self.tail:
            raise HTTPException(status_code=409, detail="Cannot go past the end of the Queue")
        self.curr = self.curr.next
        return self.curr.data

    def prev_node(self):
        if self.curr == self.head:
            raise HTTPException(status_code=409, detail="Cannot go past the beginning of the Queue")
        self.curr = self.curr.prev
        return self.curr.data

# ─── Audio Player ─────────────────────────────────────────────────────────────

class AudioPlayer:
    def __init__(self):
        self.instance = vlc.Instance()
        self.media_player = self.instance.media_player_new()
        self.current_path = None
        self.start_time = None

    def play(self, path: str):
        media = self.instance.media_new(path)
        self.media_player.set_media(media)
        self.media_player.play()
        self.current_path = path
        self.start_time = time.time()
        return {"status": "playing", "path": path}

    def pause(self):
        self.media_player.pause()
        state = "paused" if self.media_player.is_playing() == 0 else "playing"
        return {"status": state}

    def set_volume(self, level: int):
        self.media_player.audio_set_volume(level)
        return {"volume": level}

    def get_status(self):
        state = self.media_player.get_state()
        return {"status": str(state), "path": self.current_path}

    def get_progress(self):
        duration = self.media_player.get_length()   # ms
        position = self.media_player.get_time()     # ms
        percent = (position / duration * 100) if duration > 0 else 0
        return {"position_ms": position, "duration_ms": duration, "percent": round(percent, 2)}

    def seek(self, position_ms: int):
        self.media_player.set_time(position_ms)
        return {"seeked_to_ms": position_ms}

    def is_finished(self):
        return self.media_player.get_state() == vlc.State.Ended

# ─── Module-level instances ───────────────────────────────────────────────────

player = AudioPlayer()   # ← this is what main.py was looking for
jukebox = None

def create_queue():
    global jukebox
    if jukebox is not None:
        return JSONResponse(status_code=409, content={"message": "Queue already exists"})
    jukebox = Queue()
    return JSONResponse(status_code=200, content={"message": "Successfully created a Queue"})