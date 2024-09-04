// src/pages/TopPicks.js
import React from 'react';
import '../components/Picks.css';

const TopPicks = () => {
  return (
    <main>
      <section id="top-picks">
        <h2>Top Picks</h2>
        <div className="pick-card">
          <div className="pick-header">
            <div className="sport">NFL</div>
            <div className="time">12:00 PM ET • Sat Sep 7</div>
          </div>

          <div className="pick-tags">
            <div className="pick-tag spread">Point Spread Pick</div>
            <div className="pick-tag best-bet">Best Bet</div>
          </div>

          <div className="pick-details">
            <img src="https://a.espncdn.com/combiner/i?img=/i/teamlogos/nfl/500/scoreboard/bal.png&scale=crop&cquality=40&location=origin&w=96&h=96" alt="Team 1 Logo" className="team-logo" />
            <div className="matchup">
              <h3>Baltimore Ravens +3 (-110)</h3>
              <p className="vs">vs</p>
              <p>Kansas City Chiefs</p>
            </div>
            <img src="https://a.espncdn.com/combiner/i?img=/i/teamlogos/nfl/500/scoreboard/kc.png&scale=crop&cquality=40&location=origin&w=96&h=96" alt="Team 2 Logo" className="team-logo" />
          </div>

          <div className="rating">
            <span className="star">★</span>
            <span className="star">★</span>
            <span className="star">★</span>
          </div>
        </div>
      </section>
    </main>
  );
};

export default TopPicks;
