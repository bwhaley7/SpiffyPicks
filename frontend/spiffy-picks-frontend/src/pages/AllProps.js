import React, { useEffect, useState } from 'react';
import axios from 'axios';
import '../components/Picks.css';
import teamColors from '../util/teamColors'

const AllProps = () => {
  const [allProps, setAllProps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [playerImages, setPlayerImages] = useState({}); // To store player images

  useEffect(() => {
    const fetchAllProps = async () => {
      try {
        const response = await axios.get('http://localhost:5200/api/picks/props'); // Adjust the endpoint
        const propsData = response.data;

        // Fetch player headshots
        const playerImagePromises = propsData.map(async (prop) => {
          const imageUrl = await fetchPlayerHeadshot(prop.player_name);
          return { player_name: prop.player_name, imageUrl };
        });

        const imageResults = await Promise.all(playerImagePromises);

        // Map player names to their image URLs
        const imagesMap = imageResults.reduce((acc, cur) => {
          acc[cur.player_name] = cur.imageUrl;
          return acc;
        }, {});

        setAllProps(propsData);
        setPlayerImages(imagesMap);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchAllProps();
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
      <section id="all-props">
        <h2>All Props</h2>

        {/* Grid for All Props */}
        <div className="pick-grid">
          {allProps.map((prop, index) => (
            <div className="pick-card" key={index}>
              <div className="pick-header" style={{ backgroundColor: teamColors[prop.team]?.primary }}>
                <div className="sport">NFL</div>
              </div>

              <div className="pick-tags">
                <div className="pick-tag spread">{prop.prop_type}</div>
                {prop.is_top_pick && <div className="pick-tag best-bet">Best Bet</div>}
              </div>

              <div className="pick-details">
                {/* Team logo */}
                <img
                    src={prop.team === "WAS"
                        ? `https://a.espncdn.com/combiner/i?img=/i/teamlogos/nfl/500/wsh.png&h=200&w=200`
                        : `https://a.espncdn.com/combiner/i?img=/i/teamlogos/nfl/500/${prop.team}.png&h=200&w=200`}
                    alt={`${prop.team} Logo`}
                    className="team-logo"
                />

                <div className="matchup">
                  <h3>{prop.player_name} {prop.bet} {prop.line} {prop.prop_type}</h3>
                </div>
                
                {/* Player headshot */}
                <img
                  src={playerImages[prop.player_name] || '/default-player-image.png'}
                  alt={`${prop.player_name} headshot`}
                  className="player-logo"
                />
              </div>
              <div
                  className="accent-bar"
                  style={{
                    background: `linear-gradient(to right, ${teamColors[prop.team].primary}, ${teamColors[prop.team].secondary})`,
                  }}
                ></div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
};

export default AllProps;
