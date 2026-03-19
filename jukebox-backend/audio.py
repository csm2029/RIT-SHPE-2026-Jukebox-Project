from fastapi import HTTPException
from fastapi.responses import JSONResponse

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
        if curr == self.tail:
            raise HTTPException(status_code=409, detail="Cannot go past the end of the Queue")
        
        curr = curr.next
        # Update curr
        self.curr = curr

        return curr.data

    def prev_node(self):
        curr = self.curr
        if curr == self.head:
            raise HTTPException(status_code=409, detail="Cannot go past the beginning of the Queue")
    
        curr = curr.prev
        # Update curr
        self.curr = curr

        return curr.data

jukebox = None

def create_queue():
    global jukebox
    if jukebox is not None:
        return JSONResponse(status_code=409, content={"message": "Queue already exists"})

    jukebox = Queue()
    return JSONResponse(status_code=200, content={"message": "Sucessfully created a Queue"})
