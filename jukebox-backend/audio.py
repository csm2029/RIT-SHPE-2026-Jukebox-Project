from fastapi import HTTPException
from fastapi.responses import JSONResponse
import vlc
import time
import storage

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
        # Save a copy of the prev node to link back
        prev_node = self.tail

        # Add the song to the end of the queue
        if self.tail:
            self.tail.next = new_node

        # Set the song queued to the tail
        self.tail = new_node

        # Set the prev of the new tail to the prev node
        self.tail.prev = prev_node

        # If the queue is empty, have the curr node point to the head
        if self.head is None:
            self.head = new_node
            self.curr = new_node
        self.size += 1

        return new_node.data

    def next_node(self):
        curr = self.curr
        if curr is None:
            raise HTTPException(status_code=409, detail="Queue is empty")
        if curr == self.tail:
            raise HTTPException(status_code=409, detail="Cannot go past the end of the Queue")
        
        curr = curr.next
        # Update curr
        self.curr = curr

        return curr.data

    def prev_node(self):
        curr = self.curr
        if curr is None:
            raise HTTPException(status_code=409, detail="Queue is empty")
        if curr == self.head:
            raise HTTPException(status_code=409, detail="Cannot go past the beginning of the Queue")
        self.curr = self.curr.prev
        return self.curr.data
    
    def save_queue(self):
        saved_queue = []
        curr = self.head
        while( curr != None):
            saved_queue.append(curr.data)
            curr = curr.next
        return storage.save_queue(saved_queue) # return the result of saving the queue to persistence (for testing purposes)
        
    
    def reinstate_queue(self):
        song_names = storage.load_queue() # load the queue from persistence
        for song_name in song_names:
            self.enqueue(song_name) # re-enqueue each song to reinstate the queue in memory
        

# ─── Audio Player ─────────────────────────────────────────────────────────────

class AudioPlayer:
    def __init__(self):
        instance = vlc.Instance('--vout=dummy', '--aout=alsa', '--no-xlib')
        self.player = instance.media_player_new()
        self.current_song = None
        self.last_manual_play_time = 0

    def play(self, file_path):
        self.player.set_media(vlc.Media(file_path))
        self.player.play()
        self.current_song = file_path
        self.last_manual_play_time = time.time()
        return {"status": "playing", "song": file_path}

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
        state = self.player.get_state()
        if state != vlc.State.Ended:
            return False
        return (time.time() - self.last_manual_play_time) > 3

# ─── Module-level instances ───────────────────────────────────────────────────

player = AudioPlayer()   # ← this is what main.py was looking for
jukebox = None

def create_queue(force=True):
    global jukebox
    jukebox = Queue()
    return JSONResponse(status_code=200, content={"message": "Successfully created a Queue"})