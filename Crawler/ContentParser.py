from PatternBase import PatternBase
from ParsingPatterns import CategoryPattern, RezeptePattern
from ChefkochContracts import ChefkochObject
class ContentParser():
    def __init__(self):
        self.patterns = [CategoryPattern(), RezeptePattern()]
        self.recipePatterns = list[PatternBase]()

    def parse(self, content, useRecipePatterns) -> list[str]:
        result = []
        usedPatterns = self.patterns.copy()
        if useRecipePatterns:
            usedPatterns.extend(self.recipePatterns)
        for character in content:                
            for pattern in self.patterns:
                finishedString = pattern.check_character(character)
                if(finishedString):
                    result.append(finishedString)  
        return result
