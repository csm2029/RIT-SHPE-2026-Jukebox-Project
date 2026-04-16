import React, { useState, useEffect, useRef } from "react";
import Library from "./components/library";
import Queue from "./components/queue";
import Now_Playing from "./components/now_playing";
import Controls from "./components/controls";
import { createQueue, getProgress, getStatus, seekTo } from "./api";
import "./App.css";

export default function App() {
  const [currentSong, setCurrentSong] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState({ current_time: 0, total_length: 0, percentage: 0 });
  const [volume, setVolume] = useState(75);
  const [queueCreated, setQueueCreated] = useState(false);
  const [queuePosition, setQueuePosition] = useState(0);
  const [queueTotal, setQueueTotal] = useState(0);
  const [queueRefresh, setQueueRefresh] = useState(0);
  const pollRef = useRef(null);

  // Create queue on mount
  useEffect(() => {
    createQueue().then(() => setQueueCreated(true)).catch(() => setQueueCreated(true));
  }, []);
  const currentSongRef = useRef(null);

  useEffect(() => {
    currentSongRef.current = currentSong;
  }, [currentSong]);

  // Poll progress + status every second
  useEffect(() => {
    pollRef.current = setInterval(async () => {
      try {
        const [prog, status] = await Promise.all([getProgress(), getStatus()]);
        setProgress({ ...prog });
        setIsPlaying(status.state === "Playing");
  
        if (status.current_song && (!currentSongRef.current || status.current_song !== currentSongRef.current.file_path)) {
          setCurrentSong((prev) =>
            prev
              ? { ...prev, file_path: status.current_song }
              : { name: status.current_song, artist: "", album: "", file_path: status.current_song }
          );
          setQueueRefresh((n) => n + 1);
        }
      } catch (e) {}
    }, 1000);
  
    return () => clearInterval(pollRef.current);
  }, []);

  const handleSongPlay = (song) => {
    setCurrentSong(song);
    setIsPlaying(true);
  };

  const handleSeek = (ms) => {
    seekTo(ms);
  };

  const handleNext = (song) => {
    if (song) setCurrentSong({ ...song, file_path: song.file_path || song.path });
    setQueueRefresh((n) => n + 1);
  };
  
  const handlePrev = (song) => {
    if (song) setCurrentSong({ ...song, file_path: song.file_path || song.path });
    setQueueRefresh((n) => n + 1);
  };

  const handleAddToQueue = () => {
    setQueueRefresh((n) => n + 1);
  };


  return (
    <div className="app">
      {/* Background grid & glow effects */}
      <div className="app-bg">
        <div className="bg-glow bg-glow--pink" />
        <div className="bg-glow bg-glow--cyan" />
        <div className="bg-grid" />
      </div>

      {/* Header */}
      <header className="app-header">
        <div className="app-title-group">
          <h1 className="app-title">
          <span className="app-title-icon">
              <svg viewBox="0 0 64 80" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" width="28" height="35">
                {/* top arch */}
                <path d="M16 28 Q16 8 32 8 Q48 8 48 28" />
                {/* outer side columns */}
                <line x1="16" y1="28" x2="16" y2="58" />
                <line x1="48" y1="28" x2="48" y2="58" />
                {/* inner arch lines */}
                <path d="M20 28 Q20 13 32 13 Q44 13 44 28" />
                {/* speaker grille circle */}
                <ellipse cx="32" cy="26" rx="8" ry="8" />
                {/* horizontal band */}
                <rect x="18" y="36" width="28" height="6" rx="1" />
                {/* lower body */}
                <rect x="18" y="44" width="28" height="14" rx="1" />
                {/* base */}
                <path d="M13 58 Q13 63 18 63 L46 63 Q51 63 51 58" />
                {/* top knob */}
                <path d="M28 8 Q28 4 32 4 Q36 4 36 8" />
              </svg>
            </span> SHPE <span> Jukebox</span>
          </h1>
        </div>
      </header>

      {/* Main 3-column layout */}
      <main className="app-main">
        <section className="app-panel app-panel--library">
        <Library onSongPlay={handleSongPlay} queueCreated={queueCreated} onAddToQueue={handleAddToQueue} />
        </section>

        <section className="app-panel app-panel--now-playing">
          <Now_Playing currentSong={currentSong} progress={progress} onSeek={handleSeek} />
        </section>

        <section className="app-panel app-panel--queue">
          <Queue currentSong={currentSong} refreshTrigger={queueRefresh} />
        </section>
      </main>

      {/* Bottom bar: progress + controls */}
      <footer className="app-footer">
        <Controls
          isPlaying={isPlaying}
          setIsPlaying={setIsPlaying}
          currentSong={currentSong}
          onNext={handleNext}
          onPrev={handlePrev}
          volume={volume}
          setVolume={setVolume}
          queuePosition={queuePosition}
          queueTotal={queueTotal}
        />
      </footer>
    </div>
  );
}
