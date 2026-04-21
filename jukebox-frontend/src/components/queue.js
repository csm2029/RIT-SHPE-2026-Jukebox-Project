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
    } catch (e) {}
  };

  const handleRemove = async (e, index) => {
    e.stopPropagation();
    await removeFromQueue(index);
    loadQueue();
  };

  const formatDuration = (ms) => {
    if (!ms) return "";
    const totalSec = Math.floor(ms / 1000);
    const m = Math.floor(totalSec / 60);
    const s = totalSec % 60;
    return `${m}:${s.toString().padStart(2, "0")}`;
  };

  const currentIndex = queue.findIndex(
    (s) => currentSong && (
      s.file_path === currentSong.file_path ||
      s.name === currentSong.name
    )
  );

  const nowPlaying = currentIndex >= 0 ? queue[currentIndex] : null;
  const nextInQueue = currentIndex >= 0 ? queue.slice(currentIndex + 1) : queue;

  return (
    <div className="queue">
      <div className="queue-header">
        <h2 className="queue-title">Queue</h2>
      </div>

      {queue.length === 0 ? (
        <div className="queue-empty">
          <span className="queue-empty-icon">⬡</span>
          <p>Queue is empty</p>
          <p className="queue-empty-sub">Add songs from the library</p>
        </div>
      ) : (
        <div className="queue-sections">

          {nowPlaying && (
            <div className="queue-section">
              <p className="queue-section-label">Now Playing</p>
              <ul className="queue-list">
                <li className="queue-item queue-item--active">
                  <span className="queue-index">
                    <span className="playing-bars">
                      <span /><span /><span />
                    </span>
                  </span>
                  <div className="queue-art">
                    {nowPlaying.cover
                      ? <img src={nowPlaying.cover} alt="" className="queue-art-img" />
                      : <span>♪</span>}
                  </div>
                  <div className="queue-song-info">
                    <span className="queue-song-name">{nowPlaying.name}</span>
                    <span className="queue-song-artist">{nowPlaying.artist || "Unknown"}</span>
                  </div>
                  {nowPlaying.duration && (
                    <span className="queue-duration">{formatDuration(nowPlaying.duration)}</span>
                  )}
                </li>
              </ul>
            </div>
          )}

          {nextInQueue.length > 0 && (
            <div className="queue-section">
              <p className="queue-section-label">Next in Queue</p>
              <ul className="queue-list">
                {nextInQueue.map((song, i) => {
                  const actualIndex = currentIndex + 1 + i;
                  return (
                    <li key={i} className="queue-item">
                      <span className="queue-index">{i + 1}</span>
                      <div className="queue-art">
                        {song.cover
                          ? <img src={song.cover} alt="" className="queue-art-img" />
                          : <span>♪</span>}
                      </div>
                      <div className="queue-song-info">
                        <span className="queue-song-name">{song.name}</span>
                        <span className="queue-song-artist">{song.artist || "Unknown"}</span>
                      </div>
                      {song.duration && (
                        <span className="queue-duration">{formatDuration(song.duration)}</span>
                      )}
                      <button
                        className="queue-remove-btn"
                        onClick={(e) => handleRemove(e, actualIndex)}
                        title="Remove from queue"
                      >
                        ✕
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          )}

          {nowPlaying && nextInQueue.length === 0 && (
            <div className="queue-section">
              <p className="queue-section-label">Next in Queue</p>
              <div className="queue-empty" style={{flex: "unset", padding: "12px 0"}}>
                <p>No more songs in queue</p>
              </div>
            </div>
          )}

        </div>
      )}
    </div>
  );
}