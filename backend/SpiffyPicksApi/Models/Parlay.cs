namespace SpiffyPicksApi.Models
{
    public class Parlay
    {
        public int id {get;set;}
        public required string parlay_odds {get;set;}
        public required string explanation {get;set;}
        public required string bets {get;set;}
        public int nfl_week {get;set;}
        public required string first_bet_odds {get;set;}
        public required string first_bet_type {get;set;}
        public required string last_bet_odds {get;set;}
        public required string last_bet_type {get;set;}
    }
}