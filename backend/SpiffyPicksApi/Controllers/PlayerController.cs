using Microsoft.AspNetCore.Http.Timeouts;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using SpiffyPicksApi.Data;
using System.Data;

namespace SpiffyPicksApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class PlayerController : ControllerBase
    {
        private readonly SpiffyPicksContext _context;

        public PlayerController(SpiffyPicksContext context)
        {
            _context = context;
        }

        [HttpGet("{player_name}")]
        public async Task<IActionResult> GetHeadshot(string player_name)
        {
            // Query the player_headshots table to find the matching player
            var playerHeadshot = await _context.player_headshots
                .Where(p => p.display_name == player_name)
                .Select(p => p.headshot)
                .FirstOrDefaultAsync();
            var team = await _context.player_headshots
                .Where(p => p.display_name == player_name)
                .Select(p => p.team_abbr)
                .FirstOrDefaultAsync();

            // If no matching player is found, return a 404 not found
            if (playerHeadshot == null)
            {
                return NotFound(new { message = $"Headshot for player {player_name} not found." });
            }

            // Return the headshot URL or data
            return Ok(new { display_name = player_name, headshot = playerHeadshot, team_abbr = team});
        }

    }
}