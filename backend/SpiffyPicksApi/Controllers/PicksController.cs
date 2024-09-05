using Microsoft.AspNetCore.Http.Timeouts;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using SpiffyPicksApi.Data;
using System.Data;
using System.Threading.Tasks;

namespace SpiffyPicksApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class PicksController : ControllerBase
    {
        private readonly SpiffyPicksContext _context;

        public PicksController(SpiffyPicksContext context)
        {
            _context = context;
        }

        // GET api/picks
        [HttpGet]
        public async Task<IActionResult> GetAllPicks()
        {
            var picks = await _context.picks
                .Where(p => !p.is_top_pick)
                .ToListAsync();
            return Ok(picks);
        }

        // GET api/picks/toppicks
        [HttpGet("toppicks")]
        public async Task<IActionResult> GetTopPicks()
        {
            var topPicks = await _context.picks
                .Where(p => p.is_top_pick == true)
                .ToListAsync();

            return Ok(topPicks);
        }

        //GET api/picks/props
        [HttpGet("props")]
        public async Task<IActionResult> GetPlayerProps()
        {
            var playerProps = await _context.player_props
                .Where(p => !p.is_top_pick)
                .ToListAsync();
            return Ok(playerProps);
        }

        //GET api/picks/props/toppicks
        [HttpGet("props/toppicks")]
        public async Task<IActionResult> GetTopPlayerProps()
        {
            var topProps = await _context.player_props
                .Where(p => p.is_top_pick)
                .ToListAsync();

            return Ok(topProps);
        }

        //GET api/picks/parlays
        [HttpGet("parlays")]
        public async Task<IActionResult> GetParlays()
        {
            var parlays = await _context.parlays.ToListAsync();
            return Ok(parlays);
        }

    }
}