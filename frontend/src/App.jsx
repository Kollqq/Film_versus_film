import { useState, useEffect } from "react";
import {
  createRoom,
  joinRoom,
  addMovie,
  startTournament,
  getCurrentMatch,
  vote,
} from "./api";

function App() {
  const [roomCode, setRoomCode] = useState("");
  const [name, setName] = useState("");
  const [participant, setParticipant] = useState(null);
  const [movieTitle, setMovieTitle] = useState("");
  const [movieYear, setMovieYear] = useState("");
  const [currentMatch, setCurrentMatch] = useState(null);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    if (!roomCode) return;

    const timer = setInterval(() => {
      getCurrentMatch(roomCode)
        .then((m) => setCurrentMatch(m))
        .catch(() => {});
    }, 2000);

    return () => clearInterval(timer);
  }, [roomCode]);

  async function handleCreateRoom() {
    try {
      const room = await createRoom();
      setRoomCode(room.code);
      setMsg(`Room created: ${room.code}`);
    } catch {
      setMsg("Create room failed");
    }
  }

  async function handleJoin() {
    try {
      const p = await joinRoom(roomCode, name);
      setParticipant(p);
      setMsg(`Joined as ${p.name}`);
    } catch {
      setMsg("Join failed");
    }
  }

  async function handleAddMovie() {
    try {
      const payload = {
        external_id: `${movieTitle}-${movieYear}`,
        title: movieTitle,
        year: movieYear,
        poster_url: "",
        added_by: participant?.id || null,
      };
      await addMovie(roomCode, payload);
      setMsg("Movie added");
    } catch {
      setMsg("Add movie failed");
    }
  }

  async function handleStart() {
    try {
      await startTournament(roomCode);
      setMsg("Tournament started");
    } catch {
      setMsg("Start failed");
    }
  }

  async function handleFetchMatch() {
    try {
      const m = await getCurrentMatch(roomCode);
      setCurrentMatch(m);
    } catch {
      setMsg("Get match failed");
    }
  }

  async function handleVote(movieId) {
    try {
      await vote(roomCode, {
        match: currentMatch.id,
        participant: participant.id,
        movie: movieId,
      });
      setMsg("Voted");
      handleFetchMatch();
    } catch {
      setMsg("Vote failed");
    }
  }

  return (
    <div style={{ padding: 24, fontFamily: "sans-serif" }}>
      <h1>Film vs Film</h1>

      <button onClick={handleCreateRoom}>Create Room</button>

      <div style={{ marginTop: 12 }}>
        <input
          placeholder="Room code"
          value={roomCode}
          onChange={(e) => setRoomCode(e.target.value.toUpperCase())}
        />
        <input
          placeholder="Your name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <button onClick={handleJoin}>Join</button>
      </div>

      <div style={{ marginTop: 12 }}>
        <input
          placeholder="Movie title"
          value={movieTitle}
          onChange={(e) => setMovieTitle(e.target.value)}
        />
        <input
          placeholder="Year"
          value={movieYear}
          onChange={(e) => setMovieYear(e.target.value)}
        />
        <button onClick={handleAddMovie}>Add Movie</button>
      </div>

      <div style={{ marginTop: 12 }}>
        <button onClick={handleStart}>Start Tournament</button>
        <button onClick={handleFetchMatch} style={{ marginLeft: 8 }}>
          Current Match
        </button>
      </div>

      {currentMatch?.id && (
        <div style={{ marginTop: 12 }}>
          <div>Match: {currentMatch.id}</div>
          <button onClick={() => handleVote(currentMatch.movie_a.id)}>
            Vote A ({currentMatch.movie_a.title})
          </button>
          <button onClick={() => handleVote(currentMatch.movie_b.id)}>
            Vote B ({currentMatch.movie_b.title})
          </button>
        </div>
      )}

      <div style={{ marginTop: 12 }}>{msg}</div>
    </div>
  );
}

export default App;