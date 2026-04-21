const BASE_URL = "http://localhost:8000";

// ─── Library ────────────────────────────────────────────────────────────────

export async function fetchLibrary() {
  const res = await fetch(`${BASE_URL}/library`);
  return res.json();
}

export async function fetchSong(name) {
  const res = await fetch(`${BASE_URL}/library/${encodeURIComponent(name)}`);
  return res.json();
}

// ─── Queue ───────────────────────────────────────────────────────────────────

export async function createQueue() {
  const res = await fetch(`${BASE_URL}/create`, { method: "POST" });
  return res.json();
}

export async function addToQueue(song) {
  const res = await fetch(`${BASE_URL}/add`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(song),
  });
  return res.json();
}

export async function getQueue() {
  const res = await fetch(`${BASE_URL}/queue`);
  return res.json();
}

export async function removeFromQueue(index) {
  const res = await fetch(`${BASE_URL}/queue/${index}`, { method: "DELETE" });
  return res.json();
}

export async function nextSong() {
  const res = await fetch(`${BASE_URL}/next`);
  return res.json();
}

export async function prevSong() {
  const res = await fetch(`${BASE_URL}/back`);
  return res.json();
}

// ─── Playback ────────────────────────────────────────────────────────────────

export async function playSong(filePath) {
  const res = await fetch(
    `${BASE_URL}/play?song_path=${encodeURIComponent(filePath)}`,
    { method: "POST" }
  );
  return res.json();
}

export async function pauseSong() {
  const res = await fetch(`${BASE_URL}/pause`, { method: "POST" });
  return res.json();
}

export async function setVolume(level) {
  const res = await fetch(`${BASE_URL}/volume?level=${level}`, {
    method: "POST",
  });
  return res.json();
}

export async function getStatus() {
  const res = await fetch(`${BASE_URL}/status`);
  return res.json();
}

export async function getProgress() {
  const res = await fetch(`${BASE_URL}/progress`);
  return res.json();
}

export async function seekTo(positionMs) {
  const res = await fetch(`${BASE_URL}/seek?position_ms=${positionMs}`, {
    method: "POST",
  });
  return res.json();
}

export async function playFromQueue(song) {
  const res = await fetch(`${BASE_URL}/play-from-queue`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(song),
  });
  return res.json();
}