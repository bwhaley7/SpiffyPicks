
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Header from './components/Header';
import TopPicks from './pages/TopPicks';
import AllPicks from './pages/AllPicks';
import TopProps from './pages/TopProps';
import AllProps from './pages/AllProps';
import Parlays from './pages/Parlays';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <Routes>
          <Route path="/top-picks" element={<TopPicks />} />
          <Route path="/all-picks" element={<AllPicks />} />
          <Route path="/top-props" element={<TopProps />} />
          <Route path="/all-props" element={<AllProps />} />
          <Route path="/parlays" element={<Parlays />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
