import json

with open("storage/saved_queue.json", "r") as f:
    data = json.load(f)

for song_name in data["queue"]:
    print(song_name) 

def save_queue(queue: list):
    with open("storage/saved_queue.json", "w") as f:
        return json.dump({"queue": queue}, f)
        
def load_queue():
    with open("storage/saved_queue.json", "r") as f:
        data = json.load(f)
        return data["queue"]


    