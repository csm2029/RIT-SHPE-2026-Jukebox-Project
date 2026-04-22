from fastapi import HTTPException
from fastapi.responses import JSONResponse
import vlc
import time
import storage

class Node:
    def __init__(self, data):
        self.data =  data
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
    
        curr = curr.prev
        # Update curr
        self.curr = curr

        return curr.data
    
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


# Class for the audio player with play, pause, volume control, and status
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

    # Set the status to paused
    def pause(self):
        self.player.pause()
        return {"status": "paused"}

    # Set the volume level from 0 to 100
    def set_volume(self, level):
        self.player.audio_set_volume(level)
        return {"volume": level}

    # Be able to retrieve the status of the song playing
    def get_status(self):
        state = self.player.get_state()
        try:
            state_name = str(state).split(".")[-1]  # e.g. "State.Playing" -> "Playing"
        except:
            state_name = "Stopped"
        return {
            "state": state_name,
            "time": self.player.get_time(),
            "length": self.player.get_length(),
            "volume": self.player.audio_get_volume(),
            "current_song": self.current_song
        }

    # Get the current progress of the song in terms of time and the percentage of the song completed
    def get_progress(self):
        current_time = self.player.get_time()
        total_length = self.player.get_length()
        
        current_time = current_time if current_time != -1 else 0
        total_length = total_length if total_length != -1 else 0
        
        percentage = (current_time / total_length * 100) if total_length > 0 else 0
        
        return {
            "current_time": current_time,
            "total_length": total_length,
            "percentage": round(percentage, 2)
        }

    # Switch to a different point in the song in ms
    def seek(self, position_ms):
        self.player.set_time(position_ms)
        return {"status": "seeked", "position": position_ms}

    def is_finished(self):
        state = self.player.get_state()
        if state != vlc.State.Ended:
            return False
        return (time.time() - self.last_manual_play_time) > 3
    

jukebox = None
player = AudioPlayer()

def create_queue(force=True):
    global jukebox
    jukebox = Queue()
    return JSONResponse(status_code=200, content={"message": "Successfully created a Queue"})