from lxml import html
from util.nfl_teams import TEAM_ABBREVIATIONS

class TeamAbbreviationExtractor:
    def __init__(self, content, main_div_xpath, tags_to_search=None):
        self.tree = html.fromstring(content)
        self.main_div_xpath = main_div_xpath
        self.tags_to_search = tags_to_search if tags_to_search else ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'td']

    def extract_team_abbreviations(self):
        abbreviations = set()
        
        # Find the main container div
        main_div = self.tree.xpath(self.main_div_xpath)

        if not main_div:
            print(f"No elements found with the provided XPath: {self.main_div_xpath}")
            return list(abbreviations)
        
        # Gather text from the desired tags within the main container
        xpath_expression = " | ".join([f'.//{tag}' for tag in self.tags_to_search])
        elements = main_div[0].xpath(xpath_expression)
        
        for element in elements:
            text_content = element.text_content().strip()
            

            # Check if any team name from the TEAM_ABBREVIATIONS dictionary is in the text
            for team_name, abbreviation in TEAM_ABBREVIATIONS.items():
                if team_name in text_content:
                    abbreviations.add(abbreviation)

        return list(abbreviations)
