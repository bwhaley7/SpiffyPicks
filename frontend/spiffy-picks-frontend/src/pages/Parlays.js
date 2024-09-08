import React, { useEffect, useState } from 'react';
import axios from 'axios';
import '../components/Picks.css';
import teamColors from '../util/teamColors';

const AllParlays = () => {
  const [allParlays, setAllParlays] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [playerImages, setPlayerImages] = useState({}); // To store player images

  useEffect(() => {
    const fetchAllParlays = async () => {
      try {
        const response = await axios.get('http://localhost:5200/api/picks/parlays'); // Adjust the endpoint
        const parlaysData = response.data;

        // Collect all player names in the parlays that are player props or anything other than Moneyline, Spread, or Total
        const playerNames = parlaysData
          .flatMap(parlay => JSON.parse(parlay.bets))
          .filter(bet => !["Moneyline", "Spread", "Total"].includes(bet.type)) // Filter out Moneyline, Spread, and Total
          .map(bet => bet.team); // 'team' contains the player name in player props

        // Fetch headshots for all unique player names
        const uniquePlayerNames = [...new Set(playerNames)];
        const playerImagePromises = uniquePlayerNames.map(async (playerName) => {
          const imageUrl = await fetchPlayerHeadshot(playerName);
          return { player_name: playerName, imageUrl };
        });

        const imageResults = await Promise.all(playerImagePromises);

        // Map player names to their image URLs
        const imagesMap = imageResults.reduce((acc, cur) => {
          acc[cur.player_name] = cur.imageUrl;
          return acc;
        }, {});

        setAllParlays(parlaysData);
        setPlayerImages(imagesMap);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchAllParlays();
  }, []);

  // Function to fetch player headshot image by player_name
  const fetchPlayerHeadshot = async (playerName) => {
    try {
      const response = await axios.get(`http://localhost:5200/api/player/${playerName}`);
      return response.data.headshot; // Assuming your API returns { headshot: '...' }
    } catch (err) {
      console.error(`Error fetching headshot for ${playerName}:`, err);
      return null;
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <main>
      <section id="all-parlays">
        <h2>All Parlays</h2>

        {/* Grid for All Parlays */}
        <div className="parlay-grid">
          {allParlays.map((parlay, index) => (
            <div className="parlay-card" key={index}>
              <div className="parlay-header">
                <h3>Parlay Odds: {parlay.parlay_odds}</h3>
                <p>{parlay.explanation}</p>
              </div>

              {/* Stack of Pick Cards within the Parlay */}
              <div className="parlay-bets">
                {JSON.parse(parlay.bets).map((bet, betIndex) => (
                  <div className="pick-card" key={betIndex}>
                    <div
                      className="pick-header"
                      style={{ backgroundColor: teamColors[bet.team]?.primary }}
                    >
                      <div className="sport">NFL</div>
                    </div>

                    <div className="pick-tags">
                      <div className="pick-tag">{bet.type}</div>
                    </div>

                    <div className="pick-details">
                      {/* Conditional display for player image or team logo */}
                      {!["Moneyline", "Spread", "Total"].includes(bet.type) ? (
                        <img
                          src={playerImages[bet.team] || '/default-player-image.png'}
                          alt={`${bet.team} headshot`}
                          className="player-logo"
                        />
                      ) : (
                        <img
                          src={bet.team === 'WAS'
                            ? `https://a.espncdn.com/combiner/i?img=/i/teamlogos/nfl/500/wsh.png&h=200&w=200`
                            : `https://a.espncdn.com/combiner/i?img=/i/teamlogos/nfl/500/${bet.team}.png&h=200&w=200`}
                          alt={`${bet.team} Logo`}
                          className="team-logo"
                        />
                      )}

                      <div className="matchup">
                        <h3>
                          {bet.team} {bet.line} {bet.type}
                        </h3>
                      </div>
                    </div>

                    <div
                      className="accent-bar"
                      style={{
                        background: `linear-gradient(to right, ${teamColors[bet.team]?.primary}, ${teamColors[bet.team]?.secondary})`,
                      }}
                    ></div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
};

export default AllParlays;
