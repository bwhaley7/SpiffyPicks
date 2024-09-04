// src/pages/AllPicks.js
import React from 'react';
import '../components/Picks.css';

const AllPicks = () => {
  return (
    <main>
      <section id="all-picks">
        <h2>All Picks</h2>
        <div className="pick-card">
          <div className="pick-header">
            <span className="sport">NFL</span>
            <span className="pick-type">Point Spread Pick</span>
          </div>
          <div className="pick-details">
            <h3>Kansas City Chiefs -7.5</h3>
            <p>NO Saints @ KC Chiefs</p>
            <p>Picked by Caleb Wilfinger</p>
          </div>
        </div>
      </section>
    </main>
  );
};

export default AllPicks;
