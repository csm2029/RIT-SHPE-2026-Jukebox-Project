import React, { useState, useRef, useCallback, useEffect } from "react";
import "./now_playing.css";

export default function NowPlaying({ currentSong, progress, onSeek, isSeeking }) {
  const { current_time = 0, percentage = 0 } = progress || {};
  const [localPercentage, setLocalPercentage] = useState(null);
  const barRef = useRef(null);
  const seekingRef = useRef(false);

  useEffect(() => {
    if (!isSeeking?.current && localPercentage !== null) {
      setLocalPercentage(null);
    }
  }, [progress]);

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

  const getRatio = useCallback((clientX) => {
    if (!barRef.current) return 0;
    const rect = barRef.current.getBoundingClientRect();
    return Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
  }, []);

  const handlePointerDown = (e) => {
    if (!total_length || !onSeek) return;
    e.preventDefault();
    seekingRef.current = true;
    if (isSeeking) isSeeking.current = true;

    const ratio = getRatio(e.clientX);
    setLocalPercentage(ratio * 100);

    const handlePointerMove = (moveE) => {
      const r = getRatio(moveE.clientX);
      setLocalPercentage(r * 100);
    };

    const handlePointerUp = (upE) => {
      const r = getRatio(upE.clientX);
      const ms = Math.floor(r * total_length);
      onSeek(ms);
      seekingRef.current = false;

      setTimeout(() => {
        if (isSeeking) isSeeking.current = false;
        setLocalPercentage(null);
      }, 3000);

      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerup", handlePointerUp);
    };

    window.addEventListener("pointermove", handlePointerMove);
    window.addEventListener("pointerup", handlePointerUp);
  };

  const displayPercentage = localPercentage !== null ? localPercentage : percentage;
  const displayTime = localPercentage !== null
    ? Math.floor((localPercentage / 100) * total_length)
    : current_time;

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
        <div
          className="np-progress-bar"
          ref={barRef}
          onPointerDown={handlePointerDown}
          onContextMenu={(e) => e.preventDefault()}
          title="Click or drag to seek"
          style={{ touchAction: "none" }}
        >
          <div className="np-progress-track">
            <div className="np-progress-fill" style={{ width: `${displayPercentage}%` }}>
              <div className="np-progress-head" />
            </div>
          </div>
        </div>
        <div className="np-times">
          <span>{formatTime(displayTime)}</span>
          <span>{formatTime(total_length)}</span>
        </div>
      </div>
    </div>
  );
}