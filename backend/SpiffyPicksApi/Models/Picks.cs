namespace SpiffyPicksApi.Models
{
    public class Pick
    {
        public int id {get; set;}
        public DateTime game_date {get;set;}
        public TimeSpan game_time {get;set;}
        public string? game {get;set;}
        public required string pick_type {get;set;}
        public required string bet_name {get;set;}
        public float bet_line {get;set;}
        public required string bet_odds {get;set;}
        public int star_rating {get;set;}
        public required string explanation {get;set;}
        public bool is_top_pick {get;set;}
        public int nfl_week {get;set;}
        public required string home_team {get;set;}
        public required string away_team {get;set;}
    }
}