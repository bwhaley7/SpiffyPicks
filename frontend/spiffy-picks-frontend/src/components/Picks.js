// src/components/Picks.js
import React from 'react';
import './Picks.css';

const Picks = () => {
  return (
    <main>
      <section id="top-picks">
        <h2>Top Picks</h2>
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
        {/* Add more pick cards as needed */}
      </section>

      <section id="all-picks">
        <h2>All Picks</h2>
        {/* Add pick cards here */}
      </section>
    </main>
  );
};

export default Picks;
