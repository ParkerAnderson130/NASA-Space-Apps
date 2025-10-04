// App.jsx
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Chat from "./pages/Chat.js";
import Landing from "./pages/Landing.js"; // optional home page

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} /> 
        <Route path="/chat" element={<Chat />} />
      </Routes>
    </Router>
  );
}

export default App;