from tinytag import TinyTag 
import base64
import os

MUSIC_FOLDER = os.path.join(os.path.dirname(__file__), "music")

def get_library():
    songs = []

    for filename in os.listdir(MUSIC_FOLDER):
        if filename.endswith(".mp3"):
            file_path = os.path.join(MUSIC_FOLDER, filename)
            tag = TinyTag.get(file_path, image=True)
            image_data = tag.get_image()
            if image_data:
                cover = f"data:image/png;base64,{base64.b64encode(image_data).decode('utf-8')}"
            else:
                cover = None
            songs.append({
                "name":     tag.title or filename,
                "file_path": file_path,
                "artist":    tag.artist or "Unknown",
                "album":     tag.album or "Unknown",
                "cover":     cover,
                "duration":  int(tag.duration * 1000) if tag.duration else 0, 
            })
    return songs

def find_song(song_name: str):
    songs = get_library()
    for song in songs:
        if song["name"].lower() == song_name.lower():
            return song
    return None


if __name__ == "__main__":
    count = 0
    library = get_library()
    for song in library:
        print(f"{song['name']} by {song['artist']} from {song['album']} ({song['duration']} ms)")
        count += 1
    print(f"Total songs: {count}")
