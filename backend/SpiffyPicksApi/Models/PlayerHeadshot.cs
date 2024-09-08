namespace SpiffyPicksApi.Models{
    public class PlayerHeadshot
    {
        public required string display_name {get;set;}
        public required string team_abbr {get;set;}
        public required string headshot {get;set;}
        public int id {get;set;}
    }
}