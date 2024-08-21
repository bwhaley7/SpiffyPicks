from lxml import html
from nfl_teams import get_team_abbreviation, TEAM_ABBREVIATIONS

class TeamAbbreviationExtractor:
    
    def __init__(self, html_content, element_xpath):
        self.tree = html.fromstring(html_content)
        self.element_xpath = element_xpath

    def extract_team_abbreviations(self):
        content_elements = self.tree.xpath(self.element_xpath)
        if not content_elements:
            return []
        
        team_abbreviations = set()

        tags_to_search = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'td']

        for element in content_elements:
            for tag in tags_to_search:
                for item in element.findall(f'.//{tag}'):
                    text = item.text_content().strip()
                    self._check_for_teams(text, team_abbreviations)

        return list(team_abbreviations)
    
    def _check_for_teams(self, text, team_abbreviations):
        for team_name in TEAM_ABBREVIATIONS.keys():
            if team_name in text:
                team_abbreviation = get_team_abbreviation(team_name)
                team_abbreviations.add(team_abbreviation)