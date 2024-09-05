namespace SpiffyPicksApi.Models
{
    public class PlayerProp
    {
        public int id {get;set;}
        public required string player_name {get;set;}
        public required string prop_type {get;set;}
        public float line {get;set;}
        public required string bet {get;set;}
        public required string probability {get;set;}
        public required string reasoning {get;set;}
        public bool is_top_pick {get;set;}
        public int nfl_week {get;set;}
    }
}