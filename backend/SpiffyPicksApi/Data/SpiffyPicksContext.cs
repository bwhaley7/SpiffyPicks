using Microsoft.EntityFrameworkCore;

namespace SpiffyPicksApi.Data
{
    public class SpiffyPicksContext : DbContext
    {
        public SpiffyPicksContext(DbContextOptions<SpiffyPicksContext> options)
        : base(options)
        {
        }

        public DbSet<Models.Pick> picks {get; set;}
        public DbSet<Models.PlayerProp> player_props {get; set;}
        public DbSet<Models.Parlay> parlays {get;set;}
        public DbSet<Models.PlayerHeadshot> player_headshots {get;set;}
    }
}