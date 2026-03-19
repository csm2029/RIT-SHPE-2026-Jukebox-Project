
class Node:
    def __init__(self, data):
        self.data =  data
        self.next = None
        self.prev = None

class Queue:
    def __init__(self):
        self.head = None
        self.tail = None
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

        # If the queue is empty
        if self.head is None:
            self.head = new_node
        self.size += 1

    def next_node(self):
        curr = self.head

        while curr:
            print(curr.data)
            curr = curr.next

song_ex1 = { "name": "Quiere", "file_path": "beep boop...", "artist": "dei v", "album": "Los Flavorz" }  
song_ex2 = { "name": "Toa", "file_path": "beep boop...", "artist": "dei v", "album": "Los Flavorz" }
song_ex3 = { "name": "Sirena", "file_path": "beep boop...", "artist": "dei v", "album": "Los Flavorz" } 
    
def test():
    jukebox = Queue()
    jukebox.enqueue(song_ex1)
    jukebox.enqueue(song_ex2)
    jukebox.enqueue(song_ex3)

    jukebox.next_node()

test()