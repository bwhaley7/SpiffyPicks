
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Header from './components/Header';
import TopPicks from './pages/TopPicks';
import AllPicks from './pages/AllPicks';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <Routes>
          <Route path="/top-picks" element={<TopPicks />} />
          <Route path="/all-picks" element={<AllPicks />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
