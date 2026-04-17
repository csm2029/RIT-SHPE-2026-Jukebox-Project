import React, { useEffect, useState } from "react";
import { fetchLibrary, addToQueue, playSong } from "../api";
import "./library.css";

export default function Library({ onSongPlay, queueCreated, onAddToQueue }) {
  const [songs, setSongs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [addedMap, setAddedMap] = useState({});

  useEffect(() => {
    fetchLibrary()
      .then(setSongs)
      .finally(() => setLoading(false));
  }, []);

  const handlePlay = async (song) => {
    await playSong(song.file_path);
    if (onSongPlay) onSongPlay(song);
  };

  const handleAddToQueue = async (song) => {
    if (!queueCreated) return;
    await addToQueue({ name: song.name, path: song.file_path, artist: song.artist, album: song.album });
    setAddedMap((prev) => ({ ...prev, [song.name]: true }));
    setTimeout(() => setAddedMap((prev) => ({ ...prev, [song.name]: false })), 1500);
    if (onAddToQueue) onAddToQueue(); // notify App.js to refresh queue
};

  const formatDuration = (ms) => {
    if (!ms) return "--:--";
    const totalSec = Math.floor(ms / 1000);
    const m = Math.floor(totalSec / 60);
    const s = totalSec % 60;
    return `${m}:${s.toString().padStart(2, "0")}`;
  };

  if (loading) return <div className="lib-loading">Scanning library<span className="dots">...</span></div>;

  return (
    <div className="library">
      <div className="library-header">
        <h2 className="library-title">Song Library</h2>
        <span className="library-count">{songs.length} tracks available</span>
      </div>
      <ul className="song-list">
        {songs.map((song, i) => (
          <li key={i} className="song-item" onClick={() => handlePlay(song)}>
            <div className="queue-art">
              {song.cover ? (
                <img src={song.cover} alt="cover" className="queue-art-img" />
              ) : (
                <span>♪</span>
              )}
            </div>
            <div className="song-info">
              <span className="song-name">{song.name}</span>
              <span className="song-artist">{song.artist}</span>
            </div>
            <span className="song-duration">{formatDuration(song.duration)}</span>
            <button
              className={`add-queue-btn ${addedMap[song.name] ? "added" : ""}`}
              onClick={(e) => { e.stopPropagation(); handleAddToQueue(song); }}
              disabled={!queueCreated}
              title={queueCreated ? "Add to queue" : "Create a queue first"}
            >
              {addedMap[song.name] ? "✓" : "+"}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
