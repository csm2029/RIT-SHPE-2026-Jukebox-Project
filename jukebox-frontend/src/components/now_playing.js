import React from "react";
import "./now_playing.css";

export default function NowPlaying({ currentSong, progress, onSeek }) {
  const { current_time = 0, percentage = 0 } = progress || {};
  
  // use polled length, fall back to song's known duration
  const total_length = (progress?.total_length > 0)
    ? progress.total_length
    : (currentSong?.duration || 0);

  const formatTime = (ms) => {
    if (!ms || ms < 0) return "0:00";
    const totalSec = Math.floor(ms / 1000);
    const m = Math.floor(totalSec / 60);
    const s = totalSec % 60;
    return `${m}:${s.toString().padStart(2, "0")}`;
  };

  const handleBarClick = (e) => {
    if (!total_length || !onSeek) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const ratio = Math.max(0, Math.min(1, clickX / rect.width));
    onSeek(Math.floor(ratio * total_length));
  };

  return (
    <div className="now-playing">
      <div className="np-art-wrapper">
        <div className={`np-art ${currentSong ? "np-art--active" : ""}`}>
          {currentSong?.cover ? (
            <img src={currentSong.cover} alt="Album Cover" className="np-art-img" />
          ) : (
            <span className="np-art-icon">♪</span>
          )}
          <div className="np-art-glow" />
        </div>
      </div>

      <div className="np-info">
        <p className="np-song-name">{currentSong ? currentSong.name : "No song playing"}</p>
        <p className="np-artist">{currentSong ? currentSong.artist : "—"}</p>
        <p className="np-album">{currentSong ? currentSong.album : ""}</p>
      </div>

      <div className="np-progress-section">
        <div className="np-progress-bar" onClick={handleBarClick} title="Click to seek">
          <div className="np-progress-track">
            <div className="np-progress-fill" style={{ width: `${percentage}%` }}>
              <div className="np-progress-head" />
            </div>
          </div>
        </div>
        <div className="np-times">
          <span>{formatTime(current_time)}</span>
          <span>{formatTime(total_length)}</span>
        </div>
      </div>
    </div>
  );
}