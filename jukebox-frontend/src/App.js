import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [message, setMessage] = useState('Loading...');

  useEffect(() => {
    // Call backend
    fetch('http://localhost:8000/test')
      .then(res => res.json())
      .then(data => setMessage(data.data))
      .catch(err => setMessage('Error connecting to backend'));
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Jukebox</h1>
        <p>{message}</p>
      </header>
    </div>
  );
}

export default App;
