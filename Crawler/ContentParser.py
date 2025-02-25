from Crawler.PatternBase import PatternBase
from ParsingPatterns import RsPattern, RezeptePattern
from ChefkochContracts import ChefkochObject
class ContentParser():
    def __init__(self, patterns: list[PatternBase]):
        self.patterns = patterns

    def parse(self, content) -> list[ChefkochObject]:
        result = []
        for character in content:                
            for pattern in self.patterns:
                finishedString = pattern.check_character(character)
                if(finishedString):
                    result.append(finishedString)  
        return result
