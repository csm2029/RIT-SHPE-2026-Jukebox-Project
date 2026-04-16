from tinytag import TinyTag 
import os

# hardcoded for now for testing purposes
# need to change this to your file path
MUSIC_FOLDER = os.path.join(os.path.dirname(__file__), "music")

def get_library():
    """
    Scans the music folder and returns a list of song dictionaries.

    Reads the MUSIC_FOLDER constant for the folder path. Uses TinyTag to 
    extract ID3 tags from each MP3 file. If a tag is missing, it falls 
    back to the filename for name, and 'Unknown' for artist and album.

    Returns:
        list: a list of dictionaries, each containing:
            - name (str): song title or filename if no title tag
            - file_path (str): full path to the mp3 file
            - artist (str): artist name or 'Unknown' if no artist tag
            - album (str): album name or 'Unknown' if no album tag
    Notes:
        - function works properly with cleaned mp3 files (mp3 files with tags already embedded)
        - some songs in the msuic folder are not cleaned therefore when tested information is missing
    """
    songs = []

    for filename in os.listdir(MUSIC_FOLDER):
        if filename.endswith(".mp3"):
            file_path = os.path.join(MUSIC_FOLDER, filename)
            tag = TinyTag.get(file_path)
            songs.append({
                "name":      tag.title or filename,
                "file_path": file_path,
                "artist":    tag.artist or "Unknown",
                "album":     tag.album or "Unknown",
                "duration":  int(tag.duration * 1000) if tag.duration else 0, 
            })
    return songs

def find_song(song_name: str):
    """
    Searches the music library for a song by name.

    Calls get_library() to load all songs, then iterates through them
    comparing names case insensitively until a match is found.

    Args:
        song_name (str): the name of the song to search for

    Returns:
        dict: the song dictionary if found, containing name, file_path,
              artist, and album. Returns None if no match is found.

    Notes:
        - Search is case insensitive, so "SHOPOGOLICHA" matches "shopogolicha"
        - Calls get_library() on every invocation, rescanning the music folder
    """
    songs = get_library()
    for song in songs:
        if song["name"].lower() == song_name.lower():
            return song
    return None


 
