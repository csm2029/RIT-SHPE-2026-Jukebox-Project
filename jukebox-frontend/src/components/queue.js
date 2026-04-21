import React, { useEffect, useState } from "react";
import { getQueue, removeFromQueue } from "../api";
import "./queue.css";

export default function Queue({ currentSong, refreshTrigger }) {
  const [queue, setQueue] = useState([]);

  useEffect(() => {
    loadQueue();
  }, [refreshTrigger, currentSong]);

  const loadQueue = async () => {
    try {
      const data = await getQueue();
      if (Array.isArray(data)) setQueue(data);
    } catch (e) {
      // queue may not exist yet
    }
  };

  const handleRemove = async (e, index) => {
    e.stopPropagation();
    await removeFromQueue(index);
    loadQueue();
  };

  return (
    <div className="queue">
      <div className="queue-header">
        <h2 className="queue-title">Queue</h2>
        <span className="queue-count">
          {queue.length} {queue.length === 1 ? "song" : "songs"} in queue
        </span>
      </div>

      {queue.length === 0 ? (
        <div className="queue-empty">
          <span className="queue-empty-icon">⬡</span>
          <p>Queue is empty</p>
          <p className="queue-empty-sub">Add songs from the library</p>
        </div>
      ) : (
        <ul className="queue-list">
          {queue.map((song, i) => {
            const isCurrent = currentSong && song.name === currentSong.name;
            return (
              <li key={i} className={`queue-item ${isCurrent ? "queue-item--active" : ""}`}>
                <span className="queue-index">
                  {isCurrent ? (
                    <span className="playing-bars">
                      <span /><span /><span />
                    </span>
                  ) : (
                    i + 1
                  )}
                </span>
                <div className="queue-art">
                  {song.cover ? (
                    <img src={song.cover} alt="cover" className="queue-art-img" />
                  ) : (
                    <span>♪</span>
                  )}
                </div>
                <div className="queue-song-info">
                  <span className="queue-song-name">{song.name}</span>
                  <span className="queue-song-artist">{song.artist || "Unknown"}</span>
                </div>
                {song.duration && (
                  <span className="queue-duration">
                    {Math.floor(song.duration / 60000)}:{String(Math.floor((song.duration % 60000) / 1000)).padStart(2, "0")}
                  </span>
                )}
                <button
                  className="queue-remove-btn"
                  onClick={(e) => handleRemove(e, i)}
                  title="Remove from queue"
                >
                  ✕
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}