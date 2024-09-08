import React, { useEffect, useState } from 'react';
import axios from 'axios';
import '../components/Picks.css';
import teamColors
 from '../util/teamColors';
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
              <div
                  className="pick-header"
                  style={{
                    background: `linear-gradient(45deg, ${teamColors[pick.away_team]?.primary} 50%, ${teamColors[pick.home_team]?.primary} 50%)`,
                  }}
                >
                <span className="sport">NFL</span>
                <div className="time">{pick.game_time} • {pick.game_date}</div>
              </div>
              <div className="pick-tags">
                <div className="pick-tag spread">{pick.pick_type}</div>
                {pick.star_rating === 3 && <div className="pick-tag best-bet">Best Bet</div>}
              </div>
              <div className="pick-details">
              <img
                    src={pick.away_team === "WAS"
                        ? `https://a.espncdn.com/combiner/i?img=/i/teamlogos/nfl/500/wsh.png&h=200&w=200`
                        : `https://a.espncdn.com/combiner/i?img=/i/teamlogos/nfl/500/${pick.away_team}.png&h=200&w=200`}
                    alt={`${pick.away_team} Logo`}
                    className="team-logo"
                />
                {pick.pick_type === 'Moneyline' && (
                  <h3>{pick.bet_name} {pick.pick_type} ({pick.bet_odds})</h3>
                )}
                {pick.pick_type === 'Spread' && (
                  <h3>{pick.bet_name} {pick.bet_line > 0 ? `+${pick.bet_line}` : pick.bet_line} ({pick.bet_odds})</h3>
                )}
                {pick.pick_type === 'Point Spread' && (
                  <h3>{pick.bet_name} {pick.bet_line > 0 ? `+${pick.bet_line}` : pick.bet_line} ({pick.bet_odds})</h3>
                )}
                {pick.pick_type === 'Total' && (
                  <div>
                    <h3>{pick.bet_name} {pick.bet_line} ({pick.bet_odds})</h3>
                    <p>{pick.game}</p>
                  </div>
                )}
                {pick.pick_type === 'Speculative' && (
                  <div>
                    <h3>{pick.bet_name}({pick.bet_odds})</h3>
                    <p>{pick.game}</p>
                  </div>
                )}
                <img
                    src={pick.home_team === "WAS"
                        ? `https://a.espncdn.com/combiner/i?img=/i/teamlogos/nfl/500/wsh.png&h=200&w=200`
                        : `https://a.espncdn.com/combiner/i?img=/i/teamlogos/nfl/500/${pick.home_team}.png&h=200&w=200`}
                    alt={`${pick.home_team} Logo`}
                    className="team-logo"
                />
              </div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
};

export default AllPicks;