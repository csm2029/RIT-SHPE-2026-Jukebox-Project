from fastapi import HTTPException
from fastapi.responses import JSONResponse
import vlc

class Node:
    def __init__(self, data):
        self.data =  data
        self.next = None
        self.prev = None

class Queue:
    def __init__(self):
        self.head = None # start of the queue
        self.tail = None # end of the queue
        self.curr = None # pointer to the current song being played
        self.size = 0

    def enqueue(self, data):
        """
        Add a song to the end of the queue.

        Notes:
            - this is adding a song to the end of the queue, but what if we want to add a song in the middle?
        Args:
            data: the song data to add to the queue
        """
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

    def dequeue(self, data):
        """
        Remove a song from the queue by finding the song in queue.
        """
        if self.size == 0:
            return

        curr = self.head # start at the head and look for the song to remove

        while curr is not None and curr.data != data:
            curr = curr.next
            if curr is None:
                raise HTTPException(status_code=404, detail="Song not found in the Queue")
        
        prev_node = curr.prev
        next_node = curr.next

        if prev_node:
            prev_node.next = next_node
        else:
            self.head = next_node  # removed the head, so update head

        if next_node:
            next_node.prev = prev_node
        else:
            self.tail = prev_node  # removed the tail, so update tail

        # Move curr to the next song, or fall back to prev
        self.curr = next_node if next_node else prev_node
        self.size -= 1

        return curr.data # returns the song that was removed from the queue


    def next_node(self):
        """
        Move the curr pointer to the next song in the queue. If there is no next song, raise an error.
        """
        curr = self.curr
        if curr == self.tail:
            raise HTTPException(status_code=409, detail="Cannot go past the end of the Queue")
        
        curr = curr.next
        # Update curr
        self.curr = curr

        return curr.data

    def prev_node(self):
        """
        Move the curr pointer to the previous node in the queue. If there is no previous node, raise an error.
        """
        curr = self.curr
        if curr == self.head:
            raise HTTPException(status_code=409, detail="Cannot go past the beginning of the Queue")
    
        curr = curr.prev
        # Update curr
        self.curr = curr

        return curr.data

# Class for the audio player with play, pause, volume control, and status
class AudioPlayer:
    def __init__(self):
        self.player = vlc.MediaPlayer()
        self.current_song = None

    # Play a song with the given file path
    def play(self, file_path):
        self.player.set_media(vlc.Media(file_path))
        self.player.play()
        self.current_song = file_path
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
        return {
            "state": state.name if state else "Stopped",
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

    # Set the state to stopped if the song is done
    def is_finished(self):
        state = self.player.get_state()
        return state == vlc.State.Ended
    

jukebox = None
player = AudioPlayer()

def create_queue():
    """
    Create a new queue. If a queue already exists, return an error.
    """
    global jukebox
    if jukebox is not None:
        return JSONResponse(status_code=409, content={"message": "Queue already exists"})

    jukebox = Queue()
    return JSONResponse(status_code=200, content={"message": "Sucessfully created a Queue"})