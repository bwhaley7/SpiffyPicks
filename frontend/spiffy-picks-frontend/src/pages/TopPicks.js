// src/pages/TopPicks.js
import React, {useEffect, useState} from 'react';
import axios from 'axios';
import '../components/Picks.css';
import teamColors from '../util/teamColors';

const TopPicks = () => {
  const [topPicks, setTopPicks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTopPicks = async () => {
      try {
        const response = await axios.get('http://localhost:5200/api/picks/toppicks');
        console.log(response.data)
        setTopPicks(response.data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchTopPicks();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <main>
      <section id="top-picks">
        <h2>Top Picks</h2>

        {/* Grid for Top Picks */}
        <div className="pick-grid">
          {topPicks.map((pick, index) => (
            <div className="pick-card" key={index}>
              <div
                  className="pick-header"
                  style={{
                    background: `linear-gradient(45deg, ${teamColors[pick.away_team]?.primary} 50%, ${teamColors[pick.home_team]?.primary} 50%)`,
                  }}
                >
                <div className="sport">NFL</div>
                <div className="time">{pick.game_time} • {pick.game_date}</div>
              </div>

              <div className="pick-tags">
                <div className="pick-tag spread">{pick.pick_type}</div>
               {/*{pick.star_rating === 3 && <div className="pick-tag best-bet">Best Bet</div>} */}
                {pick.is_top_pick && <div className="pick-tag best-bet">Best Bet</div>}
              </div>

              <div className="pick-details">
              <img
                    src={pick.away_team === "WAS"
                        ? `https://a.espncdn.com/combiner/i?img=/i/teamlogos/nfl/500/wsh.png&h=200&w=200`
                        : `https://a.espncdn.com/combiner/i?img=/i/teamlogos/nfl/500/${pick.away_team}.png&h=200&w=200`}
                    alt={`${pick.away_team} Logo`}
                    className="team-logo"
                />
                <div className="matchup">
                  {pick.pick_type === "Moneyline" && (
                    <h3>{pick.bet_name} ML ({pick.bet_odds})</h3>
                  )}
                  {pick.pick_type === "Spread" && (
                    <h3>
                      {pick.bet_name} {pick.bet_line > 0 ? `+${pick.bet_line}` : pick.bet_line} ({pick.bet_odds})
                    </h3>
                  )}
                  {pick.pick_type === "Total" && (
                    <div>
                      <h3>{pick.bet_name} {pick.bet_line} ({pick.bet_odds})</h3>
                      <p className="vs">{pick.game}</p>
                    </div>
                  )}
                  <p>{pick.team_2}</p>
                </div>
                <img
                    src={pick.home_team === "WAS"
                        ? `https://a.espncdn.com/combiner/i?img=/i/teamlogos/nfl/500/wsh.png&h=200&w=200`
                        : `https://a.espncdn.com/combiner/i?img=/i/teamlogos/nfl/500/${pick.home_team}.png&h=200&w=200`}
                    alt={`${pick.home_team} Logo`}
                    className="team-logo"
                />
              </div>

              <div className="rating">
                {[...Array(pick.star_rating)].map((_, i) => (
                  <span className="star" key={i}>★</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
};

export default TopPicks;