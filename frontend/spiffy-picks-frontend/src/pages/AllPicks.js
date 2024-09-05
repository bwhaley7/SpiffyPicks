import React, { useEffect, useState } from 'react';
import axios from 'axios';
import '../components/Picks.css';

const AllPicks = () => {
  const [allPicks, setAllPicks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAllPicks = async () => {
      try {
        const response = await axios.get('http://localhost:5200/api/picks'); // Fetch non-top picks
        setAllPicks(response.data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchAllPicks();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <main>
      <section id="all-picks">
        <h2>All Picks</h2>
        <div className="pick-grid">
          {allPicks.map((pick, index) => (
            <div className="pick-card" key={index}>
              <div className="pick-header">
                <span className="sport">NFL</span>
                <div className="time">{pick.game_time} • {pick.game_date}</div>
              </div>
              <div className="pick-tags">
                <div className="pick-tag spread">{pick.pick_type}</div>
                {pick.star_rating === 3 && <div className="pick-tag best-bet">Best Bet</div>}
              </div>
              <div className="pick-details">
              <img src={pick.team_1_logo_url} alt="Team 1 Logo" className="team-logo" />
                {pick.pick_type === 'Moneyline' && (
                  <h3>{pick.bet_name} {pick.pick_type} ({pick.bet_odds})</h3>
                )}
                {pick.pick_type === 'Spread' && (
                  <h3>{pick.bet_name} {pick.bet_line > 0 ? `+${pick.bet_line}` : pick.bet_line} ({pick.bet_odds})</h3>
                )}
                {pick.pick_type === 'Total' && (
                  <div>
                    <h3>{pick.bet_name} {pick.bet_line} ({pick.bet_odds})</h3>
                    <p>{pick.game}</p>
                  </div>
                )}
                <img src={pick.team_2_logo_url} alt="Team 2 Logo" className="team-logo" />
              </div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
};

export default AllPicks;