from mutagen.id3 import ID3, APIC, error
from mutagen.mp3 import MP3
import os

def set_cover_art(mp3_path, image_path):
    # Load or create ID3 tags
    try:
        tags = ID3(mp3_path)
    except error:
        tags = ID3()  # Create fresh tags if none exist

    # Remove any existing cover art (APIC frames)
    tags.delall("APIC")

    # Detect image MIME type
    ext = image_path.lower().rsplit(".", 1)[-1]
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"

    # Read and embed the image
    with open(image_path, "rb") as img:
        tags.add(APIC(
            encoding=3,        # UTF-8
            mime=mime,
            type=3,            # type 3 = front cover
            desc="Cover",
            data=img.read()
        ))

    tags.save(mp3_path)
    print(f"Cover art set on {mp3_path}")

if __name__ == "__main__":
    for i in range(1, 21):
        set_cover_art(os.path.join("music", f"{i}.mp3"), os.path.join("album_photos", f"{i}.png"))