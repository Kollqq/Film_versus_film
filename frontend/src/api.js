const API_BASE = "http://127.0.0.1:8000/api";

export async function createRoom() {
  const res = await fetch(`${API_BASE}/rooms/`, { method: "POST" });
  if (!res.ok) throw new Error("createRoom failed");
  return res.json();
}

export async function joinRoom(code, name) {
  const res = await fetch(`${API_BASE}/rooms/${code}/join/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) throw new Error("joinRoom failed");
  return res.json();
}

export async function addMovie(code, payload) {
  const res = await fetch(`${API_BASE}/rooms/${code}/movies/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("addMovie failed");
  return res.json();
}

export async function startTournament(code) {
  const res = await fetch(`${API_BASE}/rooms/${code}/start/`, { method: "POST" });
  if (!res.ok) throw new Error("startTournament failed");
  return res.json();
}

export async function getCurrentMatch(code) {
  const res = await fetch(`${API_BASE}/rooms/${code}/current-match/`);
  if (!res.ok) throw new Error("getCurrentMatch failed");
  return res.json();
}

export async function vote(code, payload) {
  const res = await fetch(`${API_BASE}/rooms/${code}/vote/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("vote failed");
  return res.json();
}

export async function getWinner(code) {
  const res = await fetch(`${API_BASE}/rooms/${code}/winner/`);
  if (!res.ok) throw new Error("getWinner failed");
  return res.json();
}

export async function searchMovies(query) {
  const res = await fetch(`${API_BASE}/movies/search/?query=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error("searchMovies failed");
  return res.json();
}