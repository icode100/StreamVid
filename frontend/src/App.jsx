import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import VideoPlayer from './VideoPlayer';
import OverlayControls from './OverlayControls';
import Login from './Login';
import Register from './Register';

const App = () => {
  const [overlays, setOverlays] = useState([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState(null);
  const [url,setUrl] = useState("");


  const handleChange = (event)=>{
    setUrl(event.target.value);
  }
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
    }
  }, []);



  useEffect(() => {
    if (token && isAuthenticated) {
      fetch('/api/overlays', {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => res.json())
        .then((data) => setOverlays(data.overlays));
    }
  }, [token, isAuthenticated]);

  const handleLogin = (newToken) => {
    setToken(newToken);
    setIsAuthenticated(true);
    localStorage.setItem('token', newToken); // Store token locally
  };

  const handleOverlayChange = (newOverlay) => {
    setOverlays([...overlays, newOverlay]);
  };

  const handleLogout = () => {
    setToken(null);
    setIsAuthenticated(false);
    localStorage.removeItem('token');
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={<Login onLogin={handleLogin} />}
          // Redirect authenticated users to app
          render={({ location }) =>
            isAuthenticated ? (
              <Navigate to="/app" replace state={{ from: location }} />
            ) : (
              <>
                {/* Login form */}
              </>
            )
          }
        />
        <Route path="/register" element={<Register />} />
        <Route
          path="/app"
          element={
            <div>
              <div>
                <input type="text" placeholder='enter your URL' onChange={handleChange}/>
              </div>
              <VideoPlayer url={url} overlays={overlays} />
              <OverlayControls overlays={overlays} onOverlayChange={handleOverlayChange} onLogout={handleLogout} />
            </div>
          }
          // Protect this route with authentication
          render={({ location }) =>
            isAuthenticated ? (
              <>
                {/* Render protected content */}
              </>
            ) : (
              <Navigate to="/" replace state={{ from: location }} />
            )
          }
        />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
